/**
 * Document Link Provider
 * 
 * Provides navigation links to definitions and related items in the code.
 */

import * as vscode from 'vscode';
import { AnalysisManager } from '../analysisManager';

/**
 * Maximum line distance for determining if a reference is at the definition site.
 * Used to avoid creating links at the definition itself.
 */
const DEFINITION_PROXIMITY_THRESHOLD = 2;

/**
 * Provides document links for navigation to definitions
 */
export class DocumentLinkProvider implements vscode.DocumentLinkProvider {
    constructor(private analysisManager: AnalysisManager) {}

    provideDocumentLinks(
        document: vscode.TextDocument,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.DocumentLink[]> {
        const result = this.analysisManager.getResult();
        if (!result) {
            return [];
        }

        const links: vscode.DocumentLink[] = [];
        const text = document.getText();
        const filePath = document.uri.fsPath;

        // Find references to endpoints
        for (const endpoint of result.endpoints) {
            // Look for path references in the document
            const pathPattern = new RegExp(this.escapeRegExp(endpoint.path), 'g');
            let match;
            while ((match = pathPattern.exec(text)) !== null) {
                const startPos = document.positionAt(match.index);
                const endPos = document.positionAt(match.index + match[0].length);
                const range = new vscode.Range(startPos, endPos);

                if (endpoint.filePath) {
                    const link = new vscode.DocumentLink(
                        range,
                        vscode.Uri.file(endpoint.filePath).with({
                            fragment: `L${endpoint.line}`
                        })
                    );
                    link.tooltip = `Go to endpoint handler: ${endpoint.handler}`;
                    links.push(link);
                }
            }
        }

        // Find references to models
        for (const model of result.models) {
            const modelPattern = new RegExp(`\\b${this.escapeRegExp(model.name)}\\b`, 'g');
            let match;
            while ((match = modelPattern.exec(text)) !== null) {
                const startPos = document.positionAt(match.index);
                const endPos = document.positionAt(match.index + match[0].length);
                const range = new vscode.Range(startPos, endPos);

                // Don't create link if we're near the model definition itself
                if (filePath === model.filePath && 
                    Math.abs(startPos.line - (model.line - 1)) <= DEFINITION_PROXIMITY_THRESHOLD) {
                    continue;
                }

                if (model.filePath) {
                    const link = new vscode.DocumentLink(
                        range,
                        vscode.Uri.file(model.filePath).with({
                            fragment: `L${model.line}`
                        })
                    );
                    link.tooltip = `Go to model definition: ${model.name}`;
                    links.push(link);
                }
            }
        }

        // Find references to services
        for (const service of result.services) {
            const servicePattern = new RegExp(`\\b${this.escapeRegExp(service.name)}\\b`, 'g');
            let match;
            while ((match = servicePattern.exec(text)) !== null) {
                const startPos = document.positionAt(match.index);
                const endPos = document.positionAt(match.index + match[0].length);
                const range = new vscode.Range(startPos, endPos);

                // Don't create link if we're near the service definition itself
                if (filePath === service.filePath && 
                    Math.abs(startPos.line - (service.line - 1)) <= DEFINITION_PROXIMITY_THRESHOLD) {
                    continue;
                }

                if (service.filePath) {
                    const link = new vscode.DocumentLink(
                        range,
                        vscode.Uri.file(service.filePath).with({
                            fragment: `L${service.line}`
                        })
                    );
                    link.tooltip = `Go to service definition: ${service.name}`;
                    links.push(link);
                }
            }
        }

        return links;
    }

    resolveDocumentLink(
        link: vscode.DocumentLink,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.DocumentLink> {
        return link;
    }

    private escapeRegExp(string: string): string {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

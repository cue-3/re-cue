/**
 * CodeLens Provider
 * 
 * Provides CodeLens showing use case and actor references in the code.
 * Enhanced with direct code parsing support.
 */

import * as vscode from 'vscode';
import { AnalysisManager } from '../analysisManager';
import { CodeIndexManager } from '../parser/codeIndexManager';
import { EndpointElement, ServiceElement, ModelElement } from '../parser/types';

/**
 * Provides CodeLens for use case and actor references
 */
export class CodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;

    constructor(
        private analysisManager: AnalysisManager,
        private codeIndex?: CodeIndexManager
    ) {
        // Listen for code index changes
        if (this.codeIndex) {
            this.codeIndex.onIndexChanged(() => this.refresh());
        }
    }

    provideCodeLenses(
        document: vscode.TextDocument,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CodeLens[]> {
        const config = vscode.workspace.getConfiguration('recue');
        if (!config.get<boolean>('enableCodeLens')) {
            return [];
        }

        const codeLenses: vscode.CodeLens[] = [];
        const filePath = document.uri.fsPath;

        // First try direct code parsing if enabled
        if (config.get<boolean>('enableDirectParsing', true) && this.codeIndex) {
            const parsedLenses = this.getParsedCodeLenses(document, filePath);
            codeLenses.push(...parsedLenses);
        }

        // Fall back to analysis manager results
        const result = this.analysisManager.getResult();
        if (result) {
            // Find endpoints in this file from analysis results
            const fileEndpoints = result.endpoints.filter(ep => ep.filePath === filePath);
            for (const endpoint of fileEndpoints) {
                if (endpoint.line > 0 && endpoint.line <= document.lineCount) {
                    const position = new vscode.Position(endpoint.line - 1, 0);
                    const range = new vscode.Range(position, position);

                    // Find related use cases
                    const relatedUseCases = result.useCases.filter(uc => 
                        uc.mainScenario.some(step => 
                            step.toLowerCase().includes(endpoint.path.toLowerCase()) ||
                            step.toLowerCase().includes(endpoint.handler.toLowerCase())
                        )
                    );

                    if (relatedUseCases.length > 0) {
                        const useCaseNames = relatedUseCases.map(uc => uc.id).join(', ');
                        codeLenses.push(new vscode.CodeLens(range, {
                            title: `📋 Used by: ${useCaseNames}`,
                            command: 'recue.showQuickPick',
                            tooltip: `This endpoint is referenced in use cases: ${useCaseNames}`
                        }));
                    }

                    // Show endpoint info
                    codeLenses.push(new vscode.CodeLens(range, {
                        title: `🌐 ${endpoint.method} ${endpoint.path}`,
                        command: 'recue.navigateToItem',
                        arguments: [{ filePath: endpoint.filePath, line: endpoint.line }],
                        tooltip: `API Endpoint: ${endpoint.method} ${endpoint.path}`
                    }));
                }
            }

            // Find models in this file
            const fileModels = result.models.filter(m => m.filePath === filePath);
            for (const model of fileModels) {
                if (model.line > 0 && model.line <= document.lineCount) {
                    const position = new vscode.Position(model.line - 1, 0);
                    const range = new vscode.Range(position, position);

                    codeLenses.push(new vscode.CodeLens(range, {
                        title: `📦 Data Model: ${model.fields.length} fields, ${model.relationships.length} relationships`,
                        command: 'recue.navigateToItem',
                        arguments: [{ filePath: model.filePath, line: model.line }],
                        tooltip: `Data Model: ${model.name}`
                    }));
                }
            }

            // Find services in this file
            const fileServices = result.services.filter(s => s.filePath === filePath);
            for (const service of fileServices) {
                if (service.line > 0 && service.line <= document.lineCount) {
                    const position = new vscode.Position(service.line - 1, 0);
                    const range = new vscode.Range(position, position);

                    codeLenses.push(new vscode.CodeLens(range, {
                        title: `⚙️ Service: ${service.methods.length} methods`,
                        command: 'recue.navigateToItem',
                        arguments: [{ filePath: service.filePath, line: service.line }],
                        tooltip: `Service: ${service.name}`
                    }));
                }
            }
        }

        return codeLenses;
    }

    /**
     * Get CodeLens items from parsed code elements
     */
    private getParsedCodeLenses(document: vscode.TextDocument, filePath: string): vscode.CodeLens[] {
        const codeLenses: vscode.CodeLens[] = [];
        
        if (!this.codeIndex) {
            return codeLenses;
        }

        const elements = this.codeIndex.getElementsInFile(filePath);
        const result = this.analysisManager.getResult();
        const useCases = result?.useCases || [];
        const actors = result?.actors || [];

        for (const element of elements) {
            if (element.startLine <= 0 || element.startLine > document.lineCount) {
                continue;
            }

            const position = new vscode.Position(element.startLine - 1, 0);
            const range = new vscode.Range(position, position);

            // Get related use cases and actors
            const relatedUseCases = this.codeIndex.getRelatedUseCases(element, useCases);
            const relatedActors = this.codeIndex.getRelatedActors(element, actors);

            // Create CodeLens based on element type
            if (element.type === 'endpoint') {
                const endpoint = element as EndpointElement;
                
                // Show use case count if any
                if (relatedUseCases.length > 0 || relatedActors.length > 0) {
                    codeLenses.push(new vscode.CodeLens(range, {
                        title: `📋 ${relatedUseCases.length} use cases | 👤 ${relatedActors.length} actors`,
                        command: 'recue.showElementDetails',
                        arguments: [element, relatedUseCases, relatedActors],
                        tooltip: 'Click to view related use cases and actors'
                    }));
                }

                // Show endpoint info
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `🌐 ${endpoint.httpMethod} ${endpoint.path}`,
                    command: 'recue.navigateToCode',
                    arguments: [element],
                    tooltip: `API Endpoint: ${endpoint.httpMethod} ${endpoint.path}`
                }));

            } else if (element.type === 'service') {
                const service = element as ServiceElement;
                
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `⚙️ Service: ${service.methods.length} methods, ${service.dependencies.length} deps`,
                    command: 'recue.navigateToCode',
                    arguments: [element],
                    tooltip: `Service: ${service.name}`
                }));

            } else if (element.type === 'model') {
                const model = element as ModelElement;
                
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `📦 Model: ${model.fields.length} fields, ${model.relationships.length} relations`,
                    command: 'recue.navigateToCode',
                    arguments: [element],
                    tooltip: `Data Model: ${model.name}`
                }));

            } else if (element.type === 'controller') {
                codeLenses.push(new vscode.CodeLens(range, {
                    title: `🎮 Controller: ${element.name}`,
                    command: 'recue.navigateToCode',
                    arguments: [element],
                    tooltip: `Controller: ${element.name}`
                }));
            }
        }

        return codeLenses;
    }

    resolveCodeLens(
        codeLens: vscode.CodeLens,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CodeLens> {
        return codeLens;
    }

    refresh(): void {
        this._onDidChangeCodeLenses.fire();
    }
}

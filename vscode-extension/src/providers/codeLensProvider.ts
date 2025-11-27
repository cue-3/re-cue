/**
 * CodeLens Provider
 * 
 * Provides CodeLens showing use case and actor references in the code.
 */

import * as vscode from 'vscode';
import { AnalysisManager } from '../analysisManager';

/**
 * Provides CodeLens for use case and actor references
 */
export class CodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;

    constructor(private analysisManager: AnalysisManager) {}

    provideCodeLenses(
        document: vscode.TextDocument,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.CodeLens[]> {
        const config = vscode.workspace.getConfiguration('recue');
        if (!config.get<boolean>('enableCodeLens')) {
            return [];
        }

        const result = this.analysisManager.getResult();
        if (!result) {
            return [];
        }

        const codeLenses: vscode.CodeLens[] = [];
        const filePath = document.uri.fsPath;

        // Find endpoints in this file
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

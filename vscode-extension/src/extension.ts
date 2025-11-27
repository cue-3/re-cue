/**
 * RE-cue VS Code Extension
 * 
 * Provides in-editor reverse engineering analysis for codebases.
 * Features:
 * - Right-click to analyze file/folder
 * - View results in side panel
 * - Navigate to definitions
 * - Inline documentation preview
 * - Auto-update on save
 */

import * as vscode from 'vscode';
import { AnalysisManager } from './analysisManager';
import { ResultsTreeProvider } from './providers/resultsTreeProvider';
import { UseCasesTreeProvider } from './providers/useCasesTreeProvider';
import { ActorsTreeProvider } from './providers/actorsTreeProvider';
import { BoundariesTreeProvider } from './providers/boundariesTreeProvider';
import { EndpointsTreeProvider } from './providers/endpointsTreeProvider';
import { HoverProvider } from './providers/hoverProvider';
import { CodeLensProvider } from './providers/codeLensProvider';
import { DocumentLinkProvider } from './providers/documentLinkProvider';

let analysisManager: AnalysisManager;
let outputChannel: vscode.OutputChannel;

/**
 * Extension activation entry point
 */
export function activate(context: vscode.ExtensionContext): void {
    outputChannel = vscode.window.createOutputChannel('RE-cue');
    outputChannel.appendLine('RE-cue extension activated');

    // Initialize analysis manager
    analysisManager = new AnalysisManager(context, outputChannel);

    // Initialize tree view providers
    const resultsProvider = new ResultsTreeProvider(analysisManager);
    const useCasesProvider = new UseCasesTreeProvider(analysisManager);
    const actorsProvider = new ActorsTreeProvider(analysisManager);
    const boundariesProvider = new BoundariesTreeProvider(analysisManager);
    const endpointsProvider = new EndpointsTreeProvider(analysisManager);

    // Register tree views
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('recueResultsView', resultsProvider),
        vscode.window.registerTreeDataProvider('recueUseCasesView', useCasesProvider),
        vscode.window.registerTreeDataProvider('recueActorsView', actorsProvider),
        vscode.window.registerTreeDataProvider('recueBoundariesView', boundariesProvider),
        vscode.window.registerTreeDataProvider('recueEndpointsView', endpointsProvider)
    );

    // Register hover provider for supported languages
    const supportedLanguages = ['java', 'python', 'typescript', 'javascript', 'ruby', 'csharp'];
    const hoverProvider = new HoverProvider(analysisManager);
    const codeLensProvider = new CodeLensProvider(analysisManager);
    const documentLinkProvider = new DocumentLinkProvider(analysisManager);

    for (const language of supportedLanguages) {
        context.subscriptions.push(
            vscode.languages.registerHoverProvider(language, hoverProvider),
            vscode.languages.registerCodeLensProvider(language, codeLensProvider),
            vscode.languages.registerDocumentLinkProvider(language, documentLinkProvider)
        );
    }

    // Register commands
    registerCommands(context, resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);

    // Register file save watcher for auto-update
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((document) => {
            const config = vscode.workspace.getConfiguration('recue');
            if (config.get<boolean>('autoAnalyzeOnSave')) {
                analysisManager.analyzeFile(document.uri);
            }
        })
    );

    // Store output channel for disposal
    context.subscriptions.push(outputChannel);

    outputChannel.appendLine('RE-cue extension ready');
}

/**
 * Register all extension commands
 */
function registerCommands(
    context: vscode.ExtensionContext,
    resultsProvider: ResultsTreeProvider,
    useCasesProvider: UseCasesTreeProvider,
    actorsProvider: ActorsTreeProvider,
    boundariesProvider: BoundariesTreeProvider,
    endpointsProvider: EndpointsTreeProvider
): void {
    // Analyze file command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.analyzeFile', async (uri?: vscode.Uri) => {
            const fileUri = uri || vscode.window.activeTextEditor?.document.uri;
            if (!fileUri) {
                vscode.window.showErrorMessage('No file selected for analysis');
                return;
            }
            await analysisManager.analyzeFile(fileUri);
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
        })
    );

    // Analyze folder command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.analyzeFolder', async (uri?: vscode.Uri) => {
            let folderUri = uri;
            if (!folderUri) {
                const folders = await vscode.window.showOpenDialog({
                    canSelectFolders: true,
                    canSelectFiles: false,
                    canSelectMany: false,
                    openLabel: 'Select Folder to Analyze'
                });
                folderUri = folders?.[0];
            }
            if (!folderUri) {
                vscode.window.showErrorMessage('No folder selected for analysis');
                return;
            }
            await analysisManager.analyzeFolder(folderUri);
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
        })
    );

    // Analyze workspace command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.analyzeWorkspace', async () => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }
            await analysisManager.analyzeFolder(workspaceFolder.uri);
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
        })
    );

    // Generate spec command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generateSpec', async () => {
            const description = await vscode.window.showInputBox({
                prompt: 'Enter a description for the specification',
                placeHolder: 'e.g., "E-commerce platform with order management"'
            });
            if (!description) {
                return;
            }
            await analysisManager.generateDocument('spec', description);
        })
    );

    // Generate plan command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generatePlan', async () => {
            await analysisManager.generateDocument('plan');
        })
    );

    // Generate use cases command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generateUseCases', async () => {
            await analysisManager.generateDocument('use-cases');
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
        })
    );

    // Generate data model command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generateDataModel', async () => {
            await analysisManager.generateDocument('data-model');
        })
    );

    // Generate API contract command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generateApiContract', async () => {
            await analysisManager.generateDocument('api-contract');
        })
    );

    // Generate diagrams command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generateDiagrams', async () => {
            await analysisManager.generateDocument('diagrams');
        })
    );

    // Generate all documentation command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.generateAll', async () => {
            const description = await vscode.window.showInputBox({
                prompt: 'Enter a description for the documentation',
                placeHolder: 'e.g., "Complete project documentation"'
            });
            if (!description) {
                return;
            }
            await analysisManager.generateAllDocuments(description);
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
        })
    );

    // Refresh results command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.refreshResults', () => {
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
            vscode.window.showInformationMessage('RE-cue results refreshed');
        })
    );

    // Clear results command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.clearResults', () => {
            analysisManager.clearResults();
            refreshAllProviders(resultsProvider, useCasesProvider, actorsProvider, boundariesProvider, endpointsProvider);
            vscode.window.showInformationMessage('RE-cue results cleared');
        })
    );

    // Open settings command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.openSettings', () => {
            vscode.commands.executeCommand('workbench.action.openSettings', 'recue');
        })
    );

    // Quick pick command
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.showQuickPick', async () => {
            const items: vscode.QuickPickItem[] = [
                { label: '$(file-code) Analyze Current File', description: 'Analyze the currently open file' },
                { label: '$(folder) Analyze Folder...', description: 'Select a folder to analyze' },
                { label: '$(root-folder) Analyze Workspace', description: 'Analyze the entire workspace' },
                { label: '$(file-text) Generate Specification', description: 'Generate spec.md' },
                { label: '$(file-text) Generate Plan', description: 'Generate plan.md' },
                { label: '$(file-text) Generate Use Cases', description: 'Generate use-cases.md' },
                { label: '$(file-text) Generate Data Model', description: 'Generate data-model.md' },
                { label: '$(file-code) Generate API Contract', description: 'Generate api-spec.json' },
                { label: '$(graph) Generate Diagrams', description: 'Generate diagrams.md' },
                { label: '$(files) Generate All', description: 'Generate all documentation' },
                { label: '$(settings-gear) Settings', description: 'Open RE-cue settings' }
            ];

            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select an RE-cue action'
            });

            if (!selected) {
                return;
            }

            switch (selected.label) {
                case '$(file-code) Analyze Current File':
                    vscode.commands.executeCommand('recue.analyzeFile');
                    break;
                case '$(folder) Analyze Folder...':
                    vscode.commands.executeCommand('recue.analyzeFolder');
                    break;
                case '$(root-folder) Analyze Workspace':
                    vscode.commands.executeCommand('recue.analyzeWorkspace');
                    break;
                case '$(file-text) Generate Specification':
                    vscode.commands.executeCommand('recue.generateSpec');
                    break;
                case '$(file-text) Generate Plan':
                    vscode.commands.executeCommand('recue.generatePlan');
                    break;
                case '$(file-text) Generate Use Cases':
                    vscode.commands.executeCommand('recue.generateUseCases');
                    break;
                case '$(file-text) Generate Data Model':
                    vscode.commands.executeCommand('recue.generateDataModel');
                    break;
                case '$(file-code) Generate API Contract':
                    vscode.commands.executeCommand('recue.generateApiContract');
                    break;
                case '$(graph) Generate Diagrams':
                    vscode.commands.executeCommand('recue.generateDiagrams');
                    break;
                case '$(files) Generate All':
                    vscode.commands.executeCommand('recue.generateAll');
                    break;
                case '$(settings-gear) Settings':
                    vscode.commands.executeCommand('recue.openSettings');
                    break;
            }
        })
    );

    // Navigate to item command (for tree view items)
    context.subscriptions.push(
        vscode.commands.registerCommand('recue.navigateToItem', async (item: { filePath?: string; line?: number }) => {
            if (item.filePath) {
                const uri = vscode.Uri.file(item.filePath);
                const document = await vscode.workspace.openTextDocument(uri);
                const editor = await vscode.window.showTextDocument(document);
                if (item.line !== undefined) {
                    const position = new vscode.Position(item.line - 1, 0);
                    editor.selection = new vscode.Selection(position, position);
                    editor.revealRange(new vscode.Range(position, position), vscode.TextEditorRevealType.InCenter);
                }
            }
        })
    );
}

/**
 * Refresh all tree view providers
 */
function refreshAllProviders(
    resultsProvider: ResultsTreeProvider,
    useCasesProvider: UseCasesTreeProvider,
    actorsProvider: ActorsTreeProvider,
    boundariesProvider: BoundariesTreeProvider,
    endpointsProvider: EndpointsTreeProvider
): void {
    resultsProvider.refresh();
    useCasesProvider.refresh();
    actorsProvider.refresh();
    boundariesProvider.refresh();
    endpointsProvider.refresh();
}

/**
 * Extension deactivation
 */
export function deactivate(): void {
    if (outputChannel) {
        outputChannel.appendLine('RE-cue extension deactivated');
        outputChannel.dispose();
    }
}

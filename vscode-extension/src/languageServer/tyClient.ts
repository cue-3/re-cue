/**
 * ty Language Server Client
 * 
 * Provides LSP integration for Astral's ty type checker, enabling:
 * - Real-time type checking
 * - Inline type hints
 * - Hover documentation
 * - Diagnostic reporting
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient/node';
import { findTyExecutable } from './serverManager';

export class TyLanguageClient {
    private client: LanguageClient | undefined;
    private context: vscode.ExtensionContext;
    private outputChannel: vscode.OutputChannel;
    private statusBarItem: vscode.StatusBarItem;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('ty Language Server');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.text = '$(loading~spin) ty: starting...';
    }

    /**
     * Start the ty language server
     */
    async start(): Promise<void> {
        const config = vscode.workspace.getConfiguration('re-cue.ty');
        const enabled = config.get<boolean>('enabled', true);

        if (!enabled) {
            this.outputChannel.appendLine('ty language server is disabled in settings');
            return;
        }

        try {
            // Find ty executable
            const tyPath = await findTyExecutable();
            if (!tyPath) {
                this.outputChannel.appendLine('ty executable not found. Install with: pip install ty');
                vscode.window.showWarningMessage(
                    'ty type checker not found. Install it with: pip install ty',
                    'Install ty'
                ).then(selection => {
                    if (selection === 'Install ty') {
                        vscode.env.openExternal(vscode.Uri.parse('https://github.com/astral-sh/ty'));
                    }
                });
                return;
            }

            this.outputChannel.appendLine(`Found ty at: ${tyPath}`);

            // Configure server options
            const serverOptions: ServerOptions = {
                command: tyPath,
                args: ['lsp'],
                transport: TransportKind.stdio
            };

            // Configure client options
            const clientOptions: LanguageClientOptions = {
                documentSelector: [
                    { scheme: 'file', language: 'python' }
                ],
                synchronize: {
                    fileEvents: vscode.workspace.createFileSystemWatcher('**/*.py')
                },
                outputChannel: this.outputChannel,
                revealOutputChannelOn: 4 // Never automatically reveal
            };

            // Create and start the client
            this.client = new LanguageClient(
                'tyLanguageServer',
                'ty Language Server',
                serverOptions,
                clientOptions
            );

            this.statusBarItem.text = '$(loading~spin) ty: starting...';
            this.statusBarItem.show();

            await this.client.start();

            this.outputChannel.appendLine('ty language server started successfully');
            this.statusBarItem.text = '$(check) ty';
            this.statusBarItem.tooltip = 'ty type checker is running';

            // Hide status bar after 3 seconds if all is well
            setTimeout(() => {
                if (this.client?.isRunning()) {
                    this.statusBarItem.hide();
                }
            }, 3000);

            // Register for disposal
            this.context.subscriptions.push(this.client);
            this.context.subscriptions.push(this.statusBarItem);

        } catch (error) {
            this.outputChannel.appendLine(`Failed to start ty language server: ${error}`);
            this.statusBarItem.text = '$(error) ty: failed';
            this.statusBarItem.tooltip = `ty failed to start: ${error}`;
            this.statusBarItem.show();
            
            vscode.window.showErrorMessage(
                `Failed to start ty language server: ${error}`
            );
        }
    }

    /**
     * Stop the ty language server
     */
    async stop(): Promise<void> {
        if (this.client) {
            this.outputChannel.appendLine('Stopping ty language server...');
            await this.client.stop();
            this.client = undefined;
            this.statusBarItem.hide();
            this.outputChannel.appendLine('ty language server stopped');
        }
    }

    /**
     * Restart the ty language server
     */
    async restart(): Promise<void> {
        this.outputChannel.appendLine('Restarting ty language server...');
        await this.stop();
        await this.start();
    }

    /**
     * Check if the language server is running
     */
    isRunning(): boolean {
        return this.client?.isRunning() ?? false;
    }

    /**
     * Get the language client instance
     */
    getClient(): LanguageClient | undefined {
        return this.client;
    }
}

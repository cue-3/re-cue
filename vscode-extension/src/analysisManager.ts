/**
 * Analysis Manager
 * 
 * Manages the analysis process by invoking the RE-cue Python CLI
 * and parsing the results for display in VS Code.
 */

import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Analysis result data structure
 */
export interface AnalysisResult {
    timestamp: Date;
    projectPath: string;
    endpoints: EndpointInfo[];
    models: ModelInfo[];
    actors: ActorInfo[];
    useCases: UseCaseInfo[];
    boundaries: BoundaryInfo[];
    services: ServiceInfo[];
    views: ViewInfo[];
}

export interface EndpointInfo {
    method: string;
    path: string;
    handler: string;
    filePath: string;
    line: number;
    description?: string;
    parameters?: string[];
    responses?: string[];
}

export interface ModelInfo {
    name: string;
    filePath: string;
    line: number;
    fields: FieldInfo[];
    relationships: string[];
}

export interface FieldInfo {
    name: string;
    type: string;
    annotations: string[];
    description?: string;
}

export interface ActorInfo {
    id: string;
    name: string;
    type: 'human' | 'system' | 'external';
    description?: string;
    roles: string[];
    identifiedFrom: string;
}

export interface UseCaseInfo {
    id: string;
    name: string;
    primaryActor: string;
    systemBoundary?: string;
    preconditions: string[];
    mainScenario: string[];
    postconditions: string[];
    extensions: string[];
    filePath?: string;
    line?: number;
}

export interface BoundaryInfo {
    name: string;
    type: string;
    description?: string;
    components: string[];
    interfaces: string[];
}

export interface ServiceInfo {
    name: string;
    filePath: string;
    line: number;
    methods: string[];
    dependencies: string[];
}

export interface ViewInfo {
    name: string;
    filePath: string;
    type: string;
    components: string[];
}

/**
 * Manages RE-cue analysis operations
 */
export class AnalysisManager {
    private context: vscode.ExtensionContext;
    private outputChannel: vscode.OutputChannel;
    private currentResult: AnalysisResult | null = null;
    private isAnalyzing: boolean = false;
    private statusBarItem: vscode.StatusBarItem;

    constructor(context: vscode.ExtensionContext, outputChannel: vscode.OutputChannel) {
        this.context = context;
        this.outputChannel = outputChannel;

        // Create status bar item
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.statusBarItem.command = 'recue.showQuickPick';
        this.statusBarItem.text = '$(file-code) RE-cue';
        this.statusBarItem.tooltip = 'RE-cue: Click for quick actions';
        this.statusBarItem.show();
        context.subscriptions.push(this.statusBarItem);
    }

    /**
     * Get the current analysis result
     */
    public getResult(): AnalysisResult | null {
        return this.currentResult;
    }

    /**
     * Clear all analysis results
     */
    public clearResults(): void {
        this.currentResult = null;
    }

    /**
     * Analyze a single file
     */
    public async analyzeFile(uri: vscode.Uri): Promise<void> {
        const filePath = uri.fsPath;
        this.outputChannel.appendLine(`Analyzing file: ${filePath}`);

        // For single file analysis, we analyze the containing folder
        const folderPath = path.dirname(filePath);
        await this.runAnalysis(folderPath);
    }

    /**
     * Analyze a folder
     */
    public async analyzeFolder(uri: vscode.Uri): Promise<void> {
        const folderPath = uri.fsPath;
        this.outputChannel.appendLine(`Analyzing folder: ${folderPath}`);
        await this.runAnalysis(folderPath);
    }

    /**
     * Generate a specific document type
     */
    public async generateDocument(type: string, description?: string): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const args = this.buildArgs(type, workspaceFolder.uri.fsPath, description);
        await this.runPythonCommand(args, workspaceFolder.uri.fsPath);
    }

    /**
     * Generate all documentation
     */
    public async generateAllDocuments(description: string): Promise<void> {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const config = vscode.workspace.getConfiguration('recue');
        const args = [
            '-m', 'reverse_engineer',
            '--spec',
            '--plan',
            '--data-model',
            '--api-contract',
            '--use-cases',
            '--diagrams',
            '--description', description
        ];

        if (config.get<boolean>('verboseOutput')) {
            args.push('--verbose');
        }

        if (config.get<boolean>('enableCache')) {
            args.push('--cache');
        } else {
            args.push('--no-cache');
        }

        if (config.get<boolean>('enableParallelProcessing')) {
            args.push('--parallel');
        } else {
            args.push('--no-parallel');
        }

        args.push(workspaceFolder.uri.fsPath);

        await this.runPythonCommand(args, workspaceFolder.uri.fsPath);
    }

    /**
     * Build command arguments for a specific document type
     */
    private buildArgs(type: string, projectPath: string, description?: string): string[] {
        const args = ['-m', 'reverse_engineer'];

        switch (type) {
            case 'spec':
                args.push('--spec');
                if (description) {
                    args.push('--description', description);
                }
                break;
            case 'plan':
                args.push('--plan');
                break;
            case 'use-cases':
                args.push('--use-cases');
                break;
            case 'data-model':
                args.push('--data-model');
                break;
            case 'api-contract':
                args.push('--api-contract');
                break;
            case 'diagrams':
                args.push('--diagrams');
                break;
        }

        const config = vscode.workspace.getConfiguration('recue');
        if (config.get<boolean>('verboseOutput')) {
            args.push('--verbose');
        }

        args.push(projectPath);

        return args;
    }

    /**
     * Run the analysis
     */
    private async runAnalysis(projectPath: string): Promise<void> {
        if (this.isAnalyzing) {
            vscode.window.showWarningMessage('Analysis already in progress');
            return;
        }

        this.isAnalyzing = true;
        this.updateStatusBar('$(sync~spin) RE-cue: Analyzing...');

        try {
            const config = vscode.workspace.getConfiguration('recue');
            const args = [
                '-m', 'reverse_engineer',
                '--use-cases'  // Run full analysis including use cases
            ];

            if (config.get<boolean>('verboseOutput')) {
                args.push('--verbose');
            }

            if (config.get<boolean>('enableCache')) {
                args.push('--cache');
            } else {
                args.push('--no-cache');
            }

            if (config.get<boolean>('enableParallelProcessing')) {
                args.push('--parallel');
            } else {
                args.push('--no-parallel');
            }

            args.push(projectPath);

            await this.runPythonCommand(args, projectPath);

            // After analysis, try to parse generated files
            await this.parseGeneratedFiles(projectPath);

            vscode.window.showInformationMessage('RE-cue analysis complete');
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            vscode.window.showErrorMessage(`RE-cue analysis failed: ${errorMessage}`);
            this.outputChannel.appendLine(`Error: ${errorMessage}`);
        } finally {
            this.isAnalyzing = false;
            this.updateStatusBar('$(file-code) RE-cue');
        }
    }

    /**
     * Run a Python command
     */
    private async runPythonCommand(args: string[], cwd: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const config = vscode.workspace.getConfiguration('recue');
            const pythonPath = config.get<string>('pythonPath') || 'python3';

            this.outputChannel.appendLine(`Running: ${pythonPath} ${args.join(' ')}`);
            this.outputChannel.appendLine(`Working directory: ${cwd}`);

            const process = cp.spawn(pythonPath, args, { cwd });

            let stdout = '';
            let stderr = '';

            process.stdout.on('data', (data: Buffer) => {
                const text = data.toString();
                stdout += text;
                this.outputChannel.append(text);
            });

            process.stderr.on('data', (data: Buffer) => {
                const text = data.toString();
                stderr += text;
                this.outputChannel.append(text);
            });

            process.on('close', (code: number | null) => {
                if (code === 0) {
                    this.outputChannel.appendLine('Command completed successfully');
                    resolve(stdout);
                } else {
                    const error = `Command failed with exit code ${code}`;
                    this.outputChannel.appendLine(error);
                    reject(new Error(stderr || error));
                }
            });

            process.on('error', (err: Error) => {
                const error = `Failed to start process: ${err.message}`;
                this.outputChannel.appendLine(error);
                reject(new Error(error));
            });
        });
    }

    /**
     * Parse generated files to extract analysis results
     */
    private async parseGeneratedFiles(projectPath: string): Promise<void> {
        const projectName = path.basename(projectPath);
        const outputDir = path.join(projectPath, `re-${projectName}`);

        this.outputChannel.appendLine(`Looking for generated files in: ${outputDir}`);

        if (!fs.existsSync(outputDir)) {
            this.outputChannel.appendLine('Output directory not found');
            return;
        }

        this.currentResult = {
            timestamp: new Date(),
            projectPath: projectPath,
            endpoints: [],
            models: [],
            actors: [],
            useCases: [],
            boundaries: [],
            services: [],
            views: []
        };

        // Parse phase files
        await this.parsePhase2Actors(outputDir);
        await this.parsePhase3Boundaries(outputDir);
        await this.parsePhase4UseCases(outputDir);

        this.outputChannel.appendLine(`Parsed results: ${this.currentResult.actors.length} actors, ${this.currentResult.useCases.length} use cases, ${this.currentResult.boundaries.length} boundaries`);
    }

    /**
     * Parse Phase 2 actors file
     * 
     * Expected format:
     * ### ActorName
     * **Type**: human|system|external
     * **Description**: Actor description
     */
    private async parsePhase2Actors(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase2-actors.md');
        if (!fs.existsSync(filePath)) {
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        
        // Split content into sections by ### headers
        const sections = content.split(/^### /gm).slice(1);
        
        for (const section of sections) {
            const lines = section.split('\n');
            const name = lines[0]?.trim() || '';
            if (!name) {
                continue;
            }
            
            // Extract type from **Type**: value
            const typeMatch = section.match(/\*\*Type\*\*:\s*(\w+)/i);
            const type = (typeMatch?.[1]?.toLowerCase() as 'human' | 'system' | 'external') || 'human';
            
            // Extract description from **Description**: value
            const descMatch = section.match(/\*\*Description\*\*:\s*(.+?)(?:\n|$)/i);
            const description = descMatch?.[1]?.trim();
            
            this.currentResult?.actors.push({
                id: name.toLowerCase().replace(/\s+/g, '-'),
                name,
                type,
                description,
                roles: [],
                identifiedFrom: 'phase2-actors.md'
            });
        }
    }

    /**
     * Parse Phase 3 boundaries file
     * 
     * Expected format:
     * ### BoundaryName
     * **Type**: type value
     */
    private async parsePhase3Boundaries(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase3-boundaries.md');
        if (!fs.existsSync(filePath)) {
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        
        // Split content into sections by ### headers
        const sections = content.split(/^### /gm).slice(1);
        
        for (const section of sections) {
            const lines = section.split('\n');
            const name = lines[0]?.trim() || '';
            if (!name) {
                continue;
            }
            
            // Extract type from **Type**: value
            const typeMatch = section.match(/\*\*Type\*\*:\s*(.+?)(?:\n|$)/i);
            const type = typeMatch?.[1]?.trim() || 'unknown';
            
            this.currentResult?.boundaries.push({
                name,
                type,
                components: [],
                interfaces: []
            });
        }
    }

    /**
     * Parse Phase 4 use cases file
     * 
     * Expected format:
     * ### UC-XXX: Use Case Name
     * **Primary Actor**: ActorName
     */
    private async parsePhase4UseCases(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase4-use-cases.md');
        if (!fs.existsSync(filePath)) {
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        
        // Split content into sections by ### UC- headers to isolate each use case
        const sections = content.split(/^### (UC-\d+):\s*/gm);
        
        // Process pairs: [prefix, id, content, id, content, ...]
        for (let i = 1; i < sections.length; i += 2) {
            const id = sections[i] || '';
            const sectionContent = sections[i + 1] || '';
            
            const lines = sectionContent.split('\n');
            const name = lines[0]?.trim() || '';
            if (!name) {
                continue;
            }
            
            // Extract primary actor from **Primary Actor**: value
            const actorMatch = sectionContent.match(/\*\*Primary Actor\*\*:\s*(.+?)(?:\n|$)/i);
            const primaryActor = actorMatch?.[1]?.trim() || '';
            
            this.currentResult?.useCases.push({
                id,
                name,
                primaryActor,
                preconditions: [],
                mainScenario: [],
                postconditions: [],
                extensions: [],
                filePath
            });
        }
    }

    /**
     * Update the status bar
     */
    private updateStatusBar(text: string): void {
        this.statusBarItem.text = text;
    }
}

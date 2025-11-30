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
     * Manually parse existing generated files (for testing/debugging)
     */
    public async parseExistingFiles(projectPath: string): Promise<void> {
        this.outputChannel.show(); // Force show the output channel
        this.outputChannel.appendLine(`\n========================================`);
        this.outputChannel.appendLine(`MANUAL PARSE INITIATED`);
        this.outputChannel.appendLine(`========================================`);
        this.outputChannel.appendLine(`Manually parsing existing files for: ${projectPath}`);
        await this.parseGeneratedFiles(projectPath);
        this.outputChannel.appendLine('Manual parsing complete');
        this.outputChannel.appendLine(`========================================\n`);
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
            '--output-dir', '.',  // Save files in project root
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
        const args = ['-m', 'reverse_engineer', '--output-dir', '.'];

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

        this.outputChannel.appendLine('\n╔═══════════════════════════════════════╗');
        this.outputChannel.appendLine('║  RE-CUE EXTENSION - NEW VERSION      ║');
        this.outputChannel.appendLine('╚═══════════════════════════════════════╝\n');

        try {
            const config = vscode.workspace.getConfiguration('recue');
            const args = [
                '-m', 'reverse_engineer',
                '--use-cases',  // Run full analysis including use cases
                '--output-dir', '.'  // Save files in project root
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
        // Look for files in the project root
        const outputDir = projectPath;

        this.outputChannel.appendLine(`\n=== Parsing Generated Files ===`);
        this.outputChannel.appendLine(`Project path: ${projectPath}`);
        this.outputChannel.appendLine(`Project name: ${projectName}`);
        this.outputChannel.appendLine(`Looking for generated files in: ${outputDir}`);

        if (!fs.existsSync(outputDir)) {
            this.outputChannel.appendLine(`ERROR: Output directory not found: ${outputDir}`);
            this.outputChannel.appendLine(`Checking if directory exists...`);
            
            // Try to list parent directory contents
            try {
                const parentContents = fs.readdirSync(projectPath);
                this.outputChannel.appendLine(`Parent directory contents: ${parentContents.join(', ')}`);
                
                // Look for any re-* directories
                const reDirectories = parentContents.filter(name => name.startsWith('re-'));
                if (reDirectories.length > 0) {
                    this.outputChannel.appendLine(`Found RE-cue directories: ${reDirectories.join(', ')}`);
                    // Use the first one found
                    const actualOutputDir = path.join(projectPath, reDirectories[0]);
                    this.outputChannel.appendLine(`Using directory: ${actualOutputDir}`);
                    await this.parseFromDirectory(actualOutputDir, projectPath);
                    return;
                }
            } catch (error) {
                this.outputChannel.appendLine(`Error reading directory: ${error}`);
            }
            
            this.outputChannel.appendLine('No RE-cue output directory found');
            return;
        }

        await this.parseFromDirectory(outputDir, projectPath);
    }

    /**
     * Parse files from a specific directory
     */
    private async parseFromDirectory(outputDir: string, projectPath: string): Promise<void> {
        this.outputChannel.appendLine(`\nParsing files from: ${outputDir}`);
        
        // List directory contents
        try {
            const files = fs.readdirSync(outputDir);
            this.outputChannel.appendLine(`Files found: ${files.join(', ')}`);
        } catch (error) {
            this.outputChannel.appendLine(`Error listing directory: ${error}`);
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
        await this.parsePhase1Structure(outputDir);
        await this.parsePhase2Actors(outputDir);
        await this.parsePhase3Boundaries(outputDir);
        await this.parsePhase4UseCases(outputDir);

        this.outputChannel.appendLine(`\n=== Parsing Complete ===`);
        this.outputChannel.appendLine(`Parsed results: ${this.currentResult.actors.length} actors, ${this.currentResult.useCases.length} use cases, ${this.currentResult.boundaries.length} boundaries`);
    }

    /**
     * Parse Phase 1 structure file for API endpoints
     * 
     * Expected format (table):
     * | Method | Endpoint | Controller |
     * |--------|----------|------------|
     * | GET | /api/path | ControllerName |
     */
    private async parsePhase1Structure(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase1-structure.md');
        this.outputChannel.appendLine(`\nParsing structure from: ${filePath}`);
        
        if (!fs.existsSync(filePath)) {
            this.outputChannel.appendLine('ERROR: phase1-structure.md not found');
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        this.outputChannel.appendLine(`File size: ${content.length} bytes`);
        
        // Find the API Endpoints table
        const lines = content.split('\n');
        this.outputChannel.appendLine(`Total lines in file: ${lines.length}`);
        
        let inTable = false;
        let endpointCount = 0;
        let tableLineCount = 0;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Look for the API Endpoints table header
            if (line.startsWith('| Method | Endpoint |') || 
                (inTable && line.startsWith('|---'))) {
                inTable = true;
                this.outputChannel.appendLine(`Found endpoints table ${line.includes('Method') ? 'header' : 'separator'} at line ${i + 1}`);
                continue;
            }
            
            // Stop at empty line or next section after table started
            if (inTable && (!line.startsWith('|') || line === '' || line.startsWith('##'))) {
                this.outputChannel.appendLine(`Endpoints table ended at line ${i + 1}`);
                break;
            }
            
            // Parse endpoint row
            if (inTable && line.startsWith('|') && !line.includes('Method | Endpoint')) {
                tableLineCount++;
                const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
                
                if (cells.length >= 3) {
                    const method = cells[0];
                    const endpoint = cells[1];
                    const controller = cells[2];
                    
                    if (tableLineCount <= 5) {
                        this.outputChannel.appendLine(`  Row ${tableLineCount}: ${method} ${endpoint}`);
                    }
                    
                    this.currentResult?.endpoints.push({
                        method,
                        path: endpoint,
                        handler: controller,
                        filePath: '',
                        line: 0,
                        description: `${controller} controller`,
                        parameters: [],
                        responses: []
                    });
                    endpointCount++;
                }
            }
        }
        
        this.outputChannel.appendLine(`Parsed ${endpointCount} endpoints from phase1-structure.md`);
    }

    /**
     * Parse Phase 2 actors file
     * 
     * Expected format (table):
     * | Actor | Type | Access Level | Evidence |
     * |-------|------|--------------|----------|
     * | ActorName | ActorType | access | evidence |
     */
    private async parsePhase2Actors(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase2-actors.md');
        this.outputChannel.appendLine(`\nParsing actors from: ${filePath}`);
        
        if (!fs.existsSync(filePath)) {
            this.outputChannel.appendLine('ERROR: phase2-actors.md not found');
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        this.outputChannel.appendLine(`File size: ${content.length} bytes`);
        
        // Find the actors table - look for lines starting with |
        const lines = content.split('\n');
        this.outputChannel.appendLine(`Total lines in file: ${lines.length}`);
        
        let inTable = false;
        let actorCount = 0;
        let tableLineCount = 0;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Skip header and separator lines
            if (line.startsWith('| Actor |') || line.startsWith('|---')) {
                inTable = true;
                this.outputChannel.appendLine(`Found table ${inTable ? 'header' : 'separator'} at line ${i + 1}`);
                continue;
            }
            
            // Stop at empty line or non-table line after table started
            if (inTable && (!line.startsWith('|') || line === '')) {
                this.outputChannel.appendLine(`Table ended at line ${i + 1}`);
                break;
            }
            
            // Parse actor row
            if (inTable && line.startsWith('|')) {
                tableLineCount++;
                const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
                this.outputChannel.appendLine(`  Row ${tableLineCount}: ${cells.length} cells - ${cells[0]}`);
                
                if (cells.length >= 2) {
                    const name = cells[0];
                    const typeStr = cells[1]?.toLowerCase() || '';
                    
                    // Map type strings to our types
                    let type: 'human' | 'system' | 'external' = 'human';
                    if (typeStr.includes('external')) {
                        type = 'external';
                    } else if (typeStr.includes('internal') || typeStr.includes('end user')) {
                        type = 'human';
                    } else if (typeStr.includes('system')) {
                        type = 'system';
                    }
                    
                    const description = cells.length >= 4 ? cells[3] : undefined;
                    
                    this.currentResult?.actors.push({
                        id: name.toLowerCase().replace(/\s+/g, '-'),
                        name,
                        type,
                        description,
                        roles: [],
                        identifiedFrom: 'phase2-actors.md'
                    });
                    actorCount++;
                    this.outputChannel.appendLine(`    ✓ Added actor: ${name} (${type})`);
                }
            }
        }
        
        this.outputChannel.appendLine(`Parsed ${actorCount} actors from phase2-actors.md`);
    }

    /**
     * Parse Phase 3 boundaries file
     * 
     * Expected format (table):
     * | System Boundary | Type | Component Count | Key Components |
     * |-----------------|------|-----------------|----------------|
     * | BoundaryName | Type | count | components |
     */
    private async parsePhase3Boundaries(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase3-boundaries.md');
        this.outputChannel.appendLine(`\nParsing boundaries from: ${filePath}`);
        
        if (!fs.existsSync(filePath)) {
            this.outputChannel.appendLine('ERROR: phase3-boundaries.md not found');
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        this.outputChannel.appendLine(`File size: ${content.length} bytes`);
        
        // Find the System Boundaries table
        const lines = content.split('\n');
        this.outputChannel.appendLine(`Total lines in file: ${lines.length}`);
        
        let inTable = false;
        let boundaryCount = 0;
        let tableLineCount = 0;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Look for the System Boundaries table header
            if (line.startsWith('| System Boundary |') || 
                (inTable && line.startsWith('|---'))) {
                inTable = true;
                this.outputChannel.appendLine(`Found boundaries table ${line.includes('System Boundary') ? 'header' : 'separator'} at line ${i + 1}`);
                continue;
            }
            
            // Stop at empty line or section break after table started
            if (inTable && (!line.startsWith('|') || line === '' || line.startsWith('---'))) {
                this.outputChannel.appendLine(`Boundaries table ended at line ${i + 1}`);
                break;
            }
            
            // Parse boundary row
            if (inTable && line.startsWith('|') && !line.includes('System Boundary')) {
                tableLineCount++;
                const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
                
                if (cells.length >= 2) {
                    const name = cells[0];
                    const type = cells[1];
                    
                    // Skip rows with "No" or "*No" (like "*No subsystems identified*")
                    if (name.startsWith('*No') || name.startsWith('No ')) {
                        this.outputChannel.appendLine(`  Skipping row: ${name}`);
                        continue;
                    }
                    
                    this.outputChannel.appendLine(`  Row ${tableLineCount}: ${cells.length} cells - ${name} (${type})`);
                    
                    // Extract components from the Key Components column if available
                    const components: string[] = [];
                    if (cells.length >= 4) {
                        const keyComponents = cells[3];
                        // Split by comma and take first few
                        const componentList = keyComponents.split(',').map(c => c.trim()).filter(c => c);
                        components.push(...componentList.slice(0, 10)); // Limit to first 10
                    }
                    
                    this.currentResult?.boundaries.push({
                        name,
                        type,
                        description: undefined,
                        components,
                        interfaces: []
                    });
                    boundaryCount++;
                    this.outputChannel.appendLine(`    ✓ Added boundary: ${name} (${type}) with ${components.length} components`);
                }
            }
        }
        
        this.outputChannel.appendLine(`Parsed ${boundaryCount} boundaries from phase3-boundaries.md`);
    }

    /**
     * Parse Phase 4 use cases file
     * 
     * Expected format:
     * #### UC01: Use Case Name
     * **Primary Actor**: ActorName
     */
    private async parsePhase4UseCases(outputDir: string): Promise<void> {
        const filePath = path.join(outputDir, 'phase4-use-cases.md');
        this.outputChannel.appendLine(`\nParsing use cases from: ${filePath}`);
        
        if (!fs.existsSync(filePath)) {
            this.outputChannel.appendLine('ERROR: phase4-use-cases.md not found');
            return;
        }

        const content = fs.readFileSync(filePath, 'utf-8');
        this.outputChannel.appendLine(`File size: ${content.length} bytes`);
        
        // Split content into sections by #### UC headers (level 4 headers)
        const sections = content.split(/^#### (UC\d+):\s*/gm);
        this.outputChannel.appendLine(`Split into ${sections.length} sections`);
        
        let useCaseCount = 0;
        
        // Process pairs: [prefix, id, content, id, content, ...]
        for (let i = 1; i < sections.length; i += 2) {
            const id = sections[i] || '';
            const sectionContent = sections[i + 1] || '';
            
            const lines = sectionContent.split('\n');
            const name = lines[0]?.trim() || '';
            if (!name) {
                this.outputChannel.appendLine(`  Skipping section ${id} - no name found`);
                continue;
            }
            
            // Extract primary actor from **Primary Actor**: value
            const actorMatch = sectionContent.match(/\*\*Primary Actor\*\*:\s*(.+?)(?:\n|$)/i);
            const primaryActor = actorMatch?.[1]?.trim() || '';
            
            // Extract preconditions
            const preconditions: string[] = [];
            const precondMatch = sectionContent.match(/\*\*Preconditions\*\*:([\s\S]*?)(?:\*\*|$)/);
            if (precondMatch) {
                const precondText = precondMatch[1];
                const precondLines = precondText.split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-'))
                    .map(line => line.substring(1).trim());
                preconditions.push(...precondLines);
            }
            
            // Extract postconditions
            const postconditions: string[] = [];
            const postcondMatch = sectionContent.match(/\*\*Postconditions\*\*:([\s\S]*?)(?:\*\*|$|---)/);
            if (postcondMatch) {
                const postcondText = postcondMatch[1];
                const postcondLines = postcondText.split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-'))
                    .map(line => line.substring(1).trim());
                postconditions.push(...postcondLines);
            }
            
            // Extract main scenario
            const mainScenario: string[] = [];
            const scenarioMatch = sectionContent.match(/\*\*Main Scenario\*\*:([\s\S]*?)(?:\*\*|$|---)/);
            if (scenarioMatch) {
                const scenarioText = scenarioMatch[1];
                const scenarioLines = scenarioText.split('\n')
                    .map(line => line.trim())
                    .filter(line => /^\d+\./.test(line))
                    .map(line => line.replace(/^\d+\.\s*/, ''));
                mainScenario.push(...scenarioLines);
            }
            
            this.currentResult?.useCases.push({
                id,
                name,
                primaryActor,
                preconditions,
                mainScenario,
                postconditions,
                extensions: [],
                filePath
            });
            useCaseCount++;
            
            if (useCaseCount <= 3) {
                this.outputChannel.appendLine(`  ✓ Added: ${id}: ${name} (Actor: ${primaryActor})`);
            }
        }
        
        this.outputChannel.appendLine(`Parsed ${useCaseCount} use cases from phase4-use-cases.md`);
    }

    /**
     * Update the status bar
     */
    private updateStatusBar(text: string): void {
        this.statusBarItem.text = text;
    }
}

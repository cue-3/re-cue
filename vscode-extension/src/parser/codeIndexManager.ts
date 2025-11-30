/**
 * Code Index Manager
 * 
 * Maintains and queries the code index for efficient lookups.
 * Supports incremental updates when files change.
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import { 
    CodeElement, 
    CodeIndex, 
    EndpointElement, 
    ServiceElement, 
    ModelElement,
    UseCaseInfo,
    ActorInfo
} from './types';
import { CodeParser } from './codeParser';

/**
 * Default glob pattern for excluding files from indexing
 */
const DEFAULT_EXCLUDE_PATTERNS = [
    '**/node_modules/**',
    '**/target/**',
    '**/build/**',
    '**/dist/**',
    '**/.git/**',
    '**/venv/**',
    '**/__pycache__/**',
    '**/vendor/**',
    '**/bin/**',
    '**/obj/**'
];

/**
 * Manages the code index with file watching and incremental updates
 */
export class CodeIndexManager {
    private index: CodeIndex;
    private parser: CodeParser;
    private watchers: vscode.FileSystemWatcher[] = [];
    private outputChannel: vscode.OutputChannel | undefined;
    private onIndexChangedEmitter = new vscode.EventEmitter<void>();
    
    /** Event fired when the index changes */
    readonly onIndexChanged = this.onIndexChangedEmitter.event;
    
    constructor(outputChannel?: vscode.OutputChannel) {
        this.parser = new CodeParser();
        this.outputChannel = outputChannel;
        this.index = this.createEmptyIndex();
    }
    
    /**
     * Create an empty code index
     */
    private createEmptyIndex(): CodeIndex {
        return {
            elements: new Map(),
            fileToElements: new Map(),
            nameToFiles: new Map(),
            endpointsByPath: new Map(),
            servicesByName: new Map(),
            modelsByName: new Map()
        };
    }
    
    /**
     * Initialize the index for a workspace
     * @param workspaceRoot Root path of the workspace
     */
    async initialize(workspaceRoot: string): Promise<void> {
        this.log(`Initializing code index for: ${workspaceRoot}`);
        
        // Clear existing index
        this.index = this.createEmptyIndex();
        
        // Find all source files
        const extensions = this.parser.getSupportedExtensions();
        const files = await this.findSourceFiles(workspaceRoot, extensions);
        
        this.log(`Found ${files.length} source files to index`);
        
        // Parse all files
        let successCount = 0;
        let errorCount = 0;
        
        for (const filePath of files) {
            try {
                await this.indexFile(filePath);
                successCount++;
            } catch (error) {
                errorCount++;
                this.log(`Error indexing ${filePath}: ${error}`);
            }
        }
        
        this.log(`Indexed ${successCount} files successfully, ${errorCount} errors`);
        this.log(`Total elements: ${this.index.elements.size}`);
        
        // Set up file watchers
        this.setupFileWatchers(workspaceRoot);
        
        // Notify listeners
        this.onIndexChangedEmitter.fire();
    }
    
    /**
     * Find all source files matching supported extensions
     */
    private async findSourceFiles(rootPath: string, extensions: string[]): Promise<string[]> {
        const files: string[] = [];
        const config = vscode.workspace.getConfiguration('recue');
        const excludePatterns = config.get<string[]>('parsingExclude') || DEFAULT_EXCLUDE_PATTERNS;
        
        // Build glob pattern for supported extensions
        const extensionPattern = extensions.map(ext => `**/*${ext}`).join(',');
        const pattern = new vscode.RelativePattern(rootPath, `{${extensionPattern}}`);
        
        const uris = await vscode.workspace.findFiles(
            pattern,
            `{${excludePatterns.join(',')}}`
        );
        
        for (const uri of uris) {
            files.push(uri.fsPath);
        }
        
        return files;
    }
    
    /**
     * Index a single file
     * @param filePath Absolute path to the file
     */
    async indexFile(filePath: string): Promise<void> {
        if (!this.parser.canParse(filePath)) {
            return;
        }
        
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const result = this.parser.parse(content, filePath);
            
            // Remove old elements from this file
            this.removeFileFromIndex(filePath);
            
            // Add new elements
            for (const element of result.elements) {
                this.addElementToIndex(element);
            }
            
            if (result.errors && result.errors.length > 0) {
                this.log(`Parse errors in ${filePath}: ${result.errors.join(', ')}`);
            }
        } catch (error) {
            this.log(`Error reading/parsing ${filePath}: ${error}`);
        }
    }
    
    /**
     * Remove a file from the index
     */
    private removeFileFromIndex(filePath: string): void {
        const existingElements = this.index.fileToElements.get(filePath) || [];
        
        for (const element of existingElements) {
            const key = this.getElementKey(element);
            this.index.elements.delete(key);
            
            // Remove from name index
            const filesForName = this.index.nameToFiles.get(element.name);
            if (filesForName) {
                const idx = filesForName.indexOf(filePath);
                if (idx !== -1) {
                    filesForName.splice(idx, 1);
                }
            }
            
            // Remove from type-specific indexes
            if (element.type === 'endpoint') {
                const endpointElem = element as EndpointElement;
                const endpointsForPath = this.index.endpointsByPath.get(endpointElem.path);
                if (endpointsForPath) {
                    const idx = endpointsForPath.findIndex(e => e.filePath === filePath);
                    if (idx !== -1) {
                        endpointsForPath.splice(idx, 1);
                    }
                }
            } else if (element.type === 'service') {
                const services = this.index.servicesByName.get(element.name);
                if (services) {
                    const idx = services.findIndex(s => s.filePath === filePath);
                    if (idx !== -1) {
                        services.splice(idx, 1);
                    }
                }
            } else if (element.type === 'model') {
                const models = this.index.modelsByName.get(element.name);
                if (models) {
                    const idx = models.findIndex(m => m.filePath === filePath);
                    if (idx !== -1) {
                        models.splice(idx, 1);
                    }
                }
            }
        }
        
        this.index.fileToElements.delete(filePath);
    }
    
    /**
     * Add an element to the index
     */
    private addElementToIndex(element: CodeElement): void {
        const key = this.getElementKey(element);
        this.index.elements.set(key, element);
        
        // Add to file index
        let fileElements = this.index.fileToElements.get(element.filePath);
        if (!fileElements) {
            fileElements = [];
            this.index.fileToElements.set(element.filePath, fileElements);
        }
        fileElements.push(element);
        
        // Add to name index
        let filesForName = this.index.nameToFiles.get(element.name);
        if (!filesForName) {
            filesForName = [];
            this.index.nameToFiles.set(element.name, filesForName);
        }
        if (!filesForName.includes(element.filePath)) {
            filesForName.push(element.filePath);
        }
        
        // Add to type-specific indexes
        if (element.type === 'endpoint') {
            const endpointElem = element as EndpointElement;
            let endpointsForPath = this.index.endpointsByPath.get(endpointElem.path);
            if (!endpointsForPath) {
                endpointsForPath = [];
                this.index.endpointsByPath.set(endpointElem.path, endpointsForPath);
            }
            endpointsForPath.push(endpointElem);
        } else if (element.type === 'service') {
            const serviceElem = element as ServiceElement;
            let services = this.index.servicesByName.get(element.name);
            if (!services) {
                services = [];
                this.index.servicesByName.set(element.name, services);
            }
            services.push(serviceElem);
        } else if (element.type === 'model') {
            const modelElem = element as ModelElement;
            let models = this.index.modelsByName.get(element.name);
            if (!models) {
                models = [];
                this.index.modelsByName.set(element.name, models);
            }
            models.push(modelElem);
        }
    }
    
    /**
     * Generate a unique key for an element
     */
    private getElementKey(element: CodeElement): string {
        return `${element.filePath}:${element.startLine}:${element.name}`;
    }
    
    /**
     * Set up file watchers for incremental updates
     */
    private setupFileWatchers(workspaceRoot: string): void {
        // Dispose existing watchers
        for (const watcher of this.watchers) {
            watcher.dispose();
        }
        this.watchers = [];
        
        // Create pattern for all supported extensions
        const extensions = this.parser.getSupportedExtensions();
        const pattern = `**/*{${extensions.join(',')}}`;
        
        const watcher = vscode.workspace.createFileSystemWatcher(
            new vscode.RelativePattern(workspaceRoot, pattern)
        );
        
        watcher.onDidChange(async (uri) => {
            this.log(`File changed: ${uri.fsPath}`);
            await this.updateFile(uri.fsPath);
        });
        
        watcher.onDidCreate(async (uri) => {
            this.log(`File created: ${uri.fsPath}`);
            await this.indexFile(uri.fsPath);
            this.onIndexChangedEmitter.fire();
        });
        
        watcher.onDidDelete((uri) => {
            this.log(`File deleted: ${uri.fsPath}`);
            this.removeFileFromIndex(uri.fsPath);
            this.onIndexChangedEmitter.fire();
        });
        
        this.watchers.push(watcher);
    }
    
    /**
     * Update a file in the index
     * @param filePath Absolute path to the file
     */
    async updateFile(filePath: string): Promise<void> {
        await this.indexFile(filePath);
        this.onIndexChangedEmitter.fire();
    }
    
    /**
     * Get code element at a specific location
     * @param filePath File path
     * @param line 1-based line number
     * @returns Element at that location or null
     */
    getElementAt(filePath: string, line: number): CodeElement | null {
        const elements = this.index.fileToElements.get(filePath);
        if (!elements) {
            return null;
        }
        
        // Only match elements where the hover is on or very near the declaration line
        // This prevents triggering within the method body
        for (const element of elements) {
            if (line === element.startLine) {
                return element;
            }
        }
        
        // Allow 1 line tolerance for multi-line declarations
        for (const element of elements) {
            if (Math.abs(element.startLine - line) <= 1) {
                return element;
            }
        }
        
        return null;
    }
    
    /**
     * Get all elements in a file
     * @param filePath File path
     * @returns Array of elements in that file
     */
    getElementsInFile(filePath: string): CodeElement[] {
        return this.index.fileToElements.get(filePath) || [];
    }
    
    /**
     * Find elements by name
     * @param name Element name to search for
     * @returns Array of matching elements
     */
    findElementsByName(name: string): CodeElement[] {
        const filePaths = this.index.nameToFiles.get(name) || [];
        const elements: CodeElement[] = [];
        
        for (const filePath of filePaths) {
            const fileElements = this.index.fileToElements.get(filePath) || [];
            elements.push(...fileElements.filter(e => e.name === name));
        }
        
        return elements;
    }
    
    /**
     * Get all endpoints
     * @returns Array of all endpoint elements
     */
    getAllEndpoints(): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        for (const pathEndpoints of this.index.endpointsByPath.values()) {
            endpoints.push(...pathEndpoints);
        }
        return endpoints;
    }
    
    /**
     * Get all services
     * @returns Array of all service elements
     */
    getAllServices(): ServiceElement[] {
        const services: ServiceElement[] = [];
        for (const nameServices of this.index.servicesByName.values()) {
            services.push(...nameServices);
        }
        return services;
    }
    
    /**
     * Get all models
     * @returns Array of all model elements
     */
    getAllModels(): ModelElement[] {
        const models: ModelElement[] = [];
        for (const nameModels of this.index.modelsByName.values()) {
            models.push(...nameModels);
        }
        return models;
    }
    
    /**
     * Find related use cases for an element using heuristic matching
     * @param element Code element to find use cases for
     * @param useCases Array of use cases to search
     * @returns Array of matching use cases
     */
    getRelatedUseCases(element: CodeElement, useCases: UseCaseInfo[]): UseCaseInfo[] {
        return useCases.filter(uc => {
            const elementNameLower = element.name.toLowerCase();
            const ucNameLower = uc.name.toLowerCase();
            
            // Match by name
            if (ucNameLower.includes(elementNameLower) || 
                elementNameLower.includes(ucNameLower.replace(/\s+/g, ''))) {
                return true;
            }
            
            // Match by endpoint path for endpoints
            if (element.type === 'endpoint') {
                const endpointElem = element as EndpointElement;
                const pathParts = endpointElem.path.split('/').filter(p => p && !p.startsWith('{'));
                for (const part of pathParts) {
                    if (ucNameLower.includes(part.toLowerCase())) {
                        return true;
                    }
                }
            }
            
            // Match by main scenario content
            for (const step of uc.mainScenario) {
                if (step.toLowerCase().includes(elementNameLower)) {
                    return true;
                }
            }
            
            // Match by annotations
            if (element.annotations) {
                for (const annotation of element.annotations) {
                    if (ucNameLower.includes(annotation.toLowerCase())) {
                        return true;
                    }
                }
            }
            
            return false;
        });
    }
    
    /**
     * Find related actors for an element
     * @param element Code element to find actors for
     * @param actors Array of actors to search
     * @returns Array of matching actors
     */
    getRelatedActors(element: CodeElement, actors: ActorInfo[]): ActorInfo[] {
        return actors.filter(actor => {
            const elementNameLower = element.name.toLowerCase();
            const actorNameLower = actor.name.toLowerCase();
            
            // Match by name
            if (elementNameLower.includes(actorNameLower) || 
                actorNameLower.includes(elementNameLower)) {
                return true;
            }
            
            // Match by roles
            for (const role of actor.roles) {
                if (elementNameLower.includes(role.toLowerCase())) {
                    return true;
                }
            }
            
            return false;
        });
    }
    
    /**
     * Find elements for a use case
     * @param useCase Use case to find elements for
     * @returns Array of related code elements
     */
    findElementsForUseCase(useCase: UseCaseInfo): CodeElement[] {
        const elements: CodeElement[] = [];
        const ucNameLower = useCase.name.toLowerCase();
        
        // Search all elements
        for (const element of this.index.elements.values()) {
            const elementNameLower = element.name.toLowerCase();
            
            // Match by name
            if (ucNameLower.includes(elementNameLower) || 
                elementNameLower.includes(ucNameLower.replace(/\s+/g, ''))) {
                elements.push(element);
                continue;
            }
            
            // Match endpoints by path parts
            if (element.type === 'endpoint') {
                const endpointElem = element as EndpointElement;
                const pathParts = endpointElem.path.split('/').filter(p => p && !p.startsWith('{'));
                for (const part of pathParts) {
                    if (ucNameLower.includes(part.toLowerCase())) {
                        elements.push(element);
                        break;
                    }
                }
            }
        }
        
        return elements;
    }
    
    /**
     * Get index statistics
     * @returns Object with counts of different element types
     */
    getStats(): { 
        totalElements: number; 
        files: number; 
        endpoints: number; 
        services: number; 
        models: number 
    } {
        return {
            totalElements: this.index.elements.size,
            files: this.index.fileToElements.size,
            endpoints: this.getAllEndpoints().length,
            services: this.getAllServices().length,
            models: this.getAllModels().length
        };
    }
    
    /**
     * Clear the index
     */
    clear(): void {
        this.index = this.createEmptyIndex();
        this.onIndexChangedEmitter.fire();
    }
    
    /**
     * Dispose watchers and clean up
     */
    dispose(): void {
        for (const watcher of this.watchers) {
            watcher.dispose();
        }
        this.watchers = [];
        this.onIndexChangedEmitter.dispose();
    }
    
    /**
     * Log a message to the output channel
     */
    private log(message: string): void {
        if (this.outputChannel) {
            this.outputChannel.appendLine(`[CodeIndex] ${message}`);
        }
    }
}

/**
 * Results Tree Provider
 * 
 * Provides a tree view of analysis results including files, endpoints, models, etc.
 */

import * as vscode from 'vscode';
import { AnalysisManager, AnalysisResult } from '../analysisManager';

/**
 * Tree item representing an analysis result entry
 */
export class ResultTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly category?: string,
        public readonly data?: {
            filePath?: string;
            line?: number;
            description?: string;
        }
    ) {
        super(label, collapsibleState);

        if (data?.description) {
            this.tooltip = data.description;
            this.description = data.description;
        }

        if (data?.filePath) {
            this.command = {
                command: 'recue.navigateToItem',
                title: 'Navigate to Item',
                arguments: [data]
            };
        }

        // Set icon based on category
        switch (category) {
            case 'actor':
                this.iconPath = new vscode.ThemeIcon('account');
                break;
            case 'useCase':
                this.iconPath = new vscode.ThemeIcon('symbol-event');
                break;
            case 'boundary':
                this.iconPath = new vscode.ThemeIcon('symbol-namespace');
                break;
            case 'endpoint':
                this.iconPath = new vscode.ThemeIcon('symbol-method');
                break;
            case 'model':
                this.iconPath = new vscode.ThemeIcon('symbol-class');
                break;
            case 'service':
                this.iconPath = new vscode.ThemeIcon('symbol-interface');
                break;
            case 'view':
                this.iconPath = new vscode.ThemeIcon('symbol-file');
                break;
            case 'category':
                this.iconPath = new vscode.ThemeIcon('folder');
                break;
            default:
                this.iconPath = new vscode.ThemeIcon('circle-outline');
        }

        this.contextValue = category || 'item';
    }
}

/**
 * Tree data provider for analysis results
 */
export class ResultsTreeProvider implements vscode.TreeDataProvider<ResultTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ResultTreeItem | undefined | null | void> = 
        new vscode.EventEmitter<ResultTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ResultTreeItem | undefined | null | void> = 
        this._onDidChangeTreeData.event;

    constructor(private analysisManager: AnalysisManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ResultTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ResultTreeItem): Thenable<ResultTreeItem[]> {
        const result = this.analysisManager.getResult();
        
        if (!result) {
            return Promise.resolve([]);
        }

        if (!element) {
            // Root level - show categories
            return Promise.resolve(this.getRootCategories(result));
        }

        // Show items in category
        return Promise.resolve(this.getCategoryItems(element, result));
    }

    private getRootCategories(result: AnalysisResult): ResultTreeItem[] {
        const items: ResultTreeItem[] = [];

        // Show actors
        if (result.actors.length > 0) {
            items.push(new ResultTreeItem(
                `Actors (${result.actors.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Discovered system actors' }
            ));
        }

        // Show use cases
        if (result.useCases.length > 0) {
            items.push(new ResultTreeItem(
                `Use Cases (${result.useCases.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Extracted use cases' }
            ));
        }

        // Show boundaries
        if (result.boundaries.length > 0) {
            items.push(new ResultTreeItem(
                `System Boundaries (${result.boundaries.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Identified system boundaries' }
            ));
        }

        // Show API endpoints (from code analysis)
        if (result.endpoints.length > 0) {
            items.push(new ResultTreeItem(
                `API Endpoints (${result.endpoints.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Discovered API endpoints' }
            ));
        }

        // Show data models (from code analysis)
        if (result.models.length > 0) {
            items.push(new ResultTreeItem(
                `Data Models (${result.models.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Discovered data models' }
            ));
        }

        // Show services (from code analysis)
        if (result.services.length > 0) {
            items.push(new ResultTreeItem(
                `Services (${result.services.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Discovered services' }
            ));
        }

        // Show views (from code analysis)
        if (result.views.length > 0) {
            items.push(new ResultTreeItem(
                `Views (${result.views.length})`,
                vscode.TreeItemCollapsibleState.Collapsed,
                'category',
                { description: 'Discovered views' }
            ));
        }

        if (items.length === 0) {
            items.push(new ResultTreeItem(
                'No analysis results yet',
                vscode.TreeItemCollapsibleState.None
            ));
        }

        return items;
    }

    private getCategoryItems(element: ResultTreeItem, result: AnalysisResult): ResultTreeItem[] {
        const label = element.label as string;

        if (label.startsWith('Actors')) {
            return result.actors.map(actor =>
                new ResultTreeItem(
                    actor.name,
                    vscode.TreeItemCollapsibleState.None,
                    'actor',
                    {
                        description: actor.type
                    }
                )
            );
        }

        if (label.startsWith('Use Cases')) {
            return result.useCases.map(useCase =>
                new ResultTreeItem(
                    `${useCase.id}: ${useCase.name}`,
                    vscode.TreeItemCollapsibleState.None,
                    'useCase',
                    {
                        filePath: useCase.filePath,
                        line: useCase.line,
                        description: useCase.primaryActor
                    }
                )
            );
        }

        if (label.startsWith('System Boundaries')) {
            return result.boundaries.map(boundary =>
                new ResultTreeItem(
                    boundary.name,
                    vscode.TreeItemCollapsibleState.None,
                    'boundary',
                    {
                        description: boundary.type
                    }
                )
            );
        }

        if (label.startsWith('API Endpoints')) {
            return result.endpoints.map(endpoint => 
                new ResultTreeItem(
                    `${endpoint.method} ${endpoint.path}`,
                    vscode.TreeItemCollapsibleState.None,
                    'endpoint',
                    {
                        filePath: endpoint.filePath,
                        line: endpoint.line,
                        description: endpoint.handler
                    }
                )
            );
        }

        if (label.startsWith('Data Models')) {
            return result.models.map(model =>
                new ResultTreeItem(
                    model.name,
                    vscode.TreeItemCollapsibleState.None,
                    'model',
                    {
                        filePath: model.filePath,
                        line: model.line,
                        description: `${model.fields.length} fields`
                    }
                )
            );
        }

        if (label.startsWith('Services')) {
            return result.services.map(service =>
                new ResultTreeItem(
                    service.name,
                    vscode.TreeItemCollapsibleState.None,
                    'service',
                    {
                        filePath: service.filePath,
                        line: service.line,
                        description: `${service.methods.length} methods`
                    }
                )
            );
        }

        if (label.startsWith('Views')) {
            return result.views.map(view =>
                new ResultTreeItem(
                    view.name,
                    vscode.TreeItemCollapsibleState.None,
                    'view',
                    {
                        filePath: view.filePath,
                        description: view.type
                    }
                )
            );
        }

        return [];
    }
}

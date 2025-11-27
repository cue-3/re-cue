/**
 * Endpoints Tree Provider
 * 
 * Provides a tree view of discovered API endpoints from the analysis.
 */

import * as vscode from 'vscode';
import { AnalysisManager, EndpointInfo } from '../analysisManager';

/**
 * Tree item representing an API endpoint
 */
export class EndpointTreeItem extends vscode.TreeItem {
    constructor(
        public readonly endpoint: EndpointInfo,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly isDetail: boolean = false,
        public readonly detailLabel?: string
    ) {
        super(
            isDetail ? (detailLabel || '') : `${endpoint.method} ${endpoint.path}`,
            collapsibleState
        );

        if (!isDetail) {
            this.tooltip = new vscode.MarkdownString(this.createTooltip());
            this.description = endpoint.handler;
            
            // Set icon based on HTTP method
            switch (endpoint.method.toUpperCase()) {
                case 'GET':
                    this.iconPath = new vscode.ThemeIcon('arrow-down', new vscode.ThemeColor('charts.green'));
                    break;
                case 'POST':
                    this.iconPath = new vscode.ThemeIcon('add', new vscode.ThemeColor('charts.blue'));
                    break;
                case 'PUT':
                    this.iconPath = new vscode.ThemeIcon('edit', new vscode.ThemeColor('charts.yellow'));
                    break;
                case 'PATCH':
                    this.iconPath = new vscode.ThemeIcon('edit', new vscode.ThemeColor('charts.orange'));
                    break;
                case 'DELETE':
                    this.iconPath = new vscode.ThemeIcon('trash', new vscode.ThemeColor('charts.red'));
                    break;
                default:
                    this.iconPath = new vscode.ThemeIcon('globe');
            }

            this.contextValue = 'endpoint';

            if (endpoint.filePath) {
                this.command = {
                    command: 'recue.navigateToItem',
                    title: 'Navigate to Endpoint',
                    arguments: [{ filePath: endpoint.filePath, line: endpoint.line }]
                };
            }
        } else {
            if (detailLabel?.startsWith('Parameter:')) {
                this.iconPath = new vscode.ThemeIcon('symbol-parameter');
            } else if (detailLabel?.startsWith('Response:')) {
                this.iconPath = new vscode.ThemeIcon('json');
            } else {
                this.iconPath = new vscode.ThemeIcon('info');
            }
        }
    }

    private createTooltip(): string {
        const ep = this.endpoint;
        let tooltip = `**${ep.method} ${ep.path}**\n\n`;
        tooltip += `**Handler:** ${ep.handler}\n\n`;
        
        if (ep.description) {
            tooltip += `**Description:** ${ep.description}\n\n`;
        }

        if (ep.parameters && ep.parameters.length > 0) {
            tooltip += `**Parameters:**\n`;
            ep.parameters.forEach(p => tooltip += `- ${p}\n`);
            tooltip += '\n';
        }

        if (ep.responses && ep.responses.length > 0) {
            tooltip += `**Responses:**\n`;
            ep.responses.forEach(r => tooltip += `- ${r}\n`);
        }

        if (ep.filePath) {
            tooltip += `\n**File:** ${ep.filePath}:${ep.line}`;
        }

        return tooltip;
    }
}

/**
 * Tree data provider for API endpoints
 */
export class EndpointsTreeProvider implements vscode.TreeDataProvider<EndpointTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<EndpointTreeItem | undefined | null | void> = 
        new vscode.EventEmitter<EndpointTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<EndpointTreeItem | undefined | null | void> = 
        this._onDidChangeTreeData.event;

    constructor(private analysisManager: AnalysisManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: EndpointTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: EndpointTreeItem): Thenable<EndpointTreeItem[]> {
        const result = this.analysisManager.getResult();
        
        if (!result || result.endpoints.length === 0) {
            return Promise.resolve([]);
        }

        if (!element) {
            // Root level - group endpoints by HTTP method
            const groupedEndpoints = this.groupByMethod(result.endpoints);
            const items: EndpointTreeItem[] = [];

            // Add endpoints in method order: GET, POST, PUT, PATCH, DELETE, others
            const methodOrder = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];
            
            for (const method of methodOrder) {
                const endpoints = groupedEndpoints.get(method) || [];
                items.push(...endpoints.map(ep => 
                    new EndpointTreeItem(ep, vscode.TreeItemCollapsibleState.Collapsed)
                ));
            }

            // Add any other methods
            groupedEndpoints.forEach((endpoints, method) => {
                if (!methodOrder.includes(method)) {
                    items.push(...endpoints.map(ep => 
                        new EndpointTreeItem(ep, vscode.TreeItemCollapsibleState.Collapsed)
                    ));
                }
            });

            return Promise.resolve(items);
        }

        // Show endpoint details
        return Promise.resolve(this.getEndpointDetails(element.endpoint));
    }

    private groupByMethod(endpoints: EndpointInfo[]): Map<string, EndpointInfo[]> {
        const groups = new Map<string, EndpointInfo[]>();
        
        for (const endpoint of endpoints) {
            const method = endpoint.method.toUpperCase();
            if (!groups.has(method)) {
                groups.set(method, []);
            }
            groups.get(method)!.push(endpoint);
        }

        return groups;
    }

    private getEndpointDetails(endpoint: EndpointInfo): EndpointTreeItem[] {
        const items: EndpointTreeItem[] = [];

        // Handler
        items.push(new EndpointTreeItem(
            endpoint,
            vscode.TreeItemCollapsibleState.None,
            true,
            `Handler: ${endpoint.handler}`
        ));

        // Description
        if (endpoint.description) {
            items.push(new EndpointTreeItem(
                endpoint,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Description: ${endpoint.description}`
            ));
        }

        // Parameters
        if (endpoint.parameters) {
            endpoint.parameters.forEach(param => {
                items.push(new EndpointTreeItem(
                    endpoint,
                    vscode.TreeItemCollapsibleState.None,
                    true,
                    `Parameter: ${param}`
                ));
            });
        }

        // Responses
        if (endpoint.responses) {
            endpoint.responses.forEach(response => {
                items.push(new EndpointTreeItem(
                    endpoint,
                    vscode.TreeItemCollapsibleState.None,
                    true,
                    `Response: ${response}`
                ));
            });
        }

        // File location
        if (endpoint.filePath) {
            items.push(new EndpointTreeItem(
                endpoint,
                vscode.TreeItemCollapsibleState.None,
                true,
                `File: ${endpoint.filePath}:${endpoint.line}`
            ));
        }

        return items;
    }
}

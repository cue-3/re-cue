/**
 * Boundaries Tree Provider
 * 
 * Provides a tree view of discovered system boundaries from the analysis.
 */

import * as vscode from 'vscode';
import { AnalysisManager, BoundaryInfo } from '../analysisManager';

/**
 * Tree item representing a system boundary
 */
export class BoundaryTreeItem extends vscode.TreeItem {
    constructor(
        public readonly boundary: BoundaryInfo,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly isDetail: boolean = false,
        public readonly detailLabel?: string
    ) {
        super(
            isDetail ? (detailLabel || '') : boundary.name,
            collapsibleState
        );

        if (!isDetail) {
            this.tooltip = new vscode.MarkdownString(this.createTooltip());
            this.description = boundary.type;
            this.iconPath = new vscode.ThemeIcon('symbol-namespace');
            this.contextValue = 'boundary';
        } else {
            if (detailLabel?.startsWith('Component:')) {
                this.iconPath = new vscode.ThemeIcon('symbol-class');
            } else if (detailLabel?.startsWith('Interface:')) {
                this.iconPath = new vscode.ThemeIcon('symbol-interface');
            } else {
                this.iconPath = new vscode.ThemeIcon('info');
            }
        }
    }

    private createTooltip(): string {
        const boundary = this.boundary;
        let tooltip = `**${boundary.name}**\n\n`;
        tooltip += `**Type:** ${boundary.type}\n\n`;
        
        if (boundary.description) {
            tooltip += `**Description:** ${boundary.description}\n\n`;
        }

        if (boundary.components.length > 0) {
            tooltip += `**Components:**\n`;
            boundary.components.forEach(c => tooltip += `- ${c}\n`);
            tooltip += '\n';
        }

        if (boundary.interfaces.length > 0) {
            tooltip += `**Interfaces:**\n`;
            boundary.interfaces.forEach(i => tooltip += `- ${i}\n`);
        }

        return tooltip;
    }
}

/**
 * Tree data provider for system boundaries
 */
export class BoundariesTreeProvider implements vscode.TreeDataProvider<BoundaryTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<BoundaryTreeItem | undefined | null | void> = 
        new vscode.EventEmitter<BoundaryTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<BoundaryTreeItem | undefined | null | void> = 
        this._onDidChangeTreeData.event;

    constructor(private analysisManager: AnalysisManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: BoundaryTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: BoundaryTreeItem): Thenable<BoundaryTreeItem[]> {
        const result = this.analysisManager.getResult();
        
        if (!result || result.boundaries.length === 0) {
            return Promise.resolve([]);
        }

        if (!element) {
            // Root level - show boundaries
            return Promise.resolve(
                result.boundaries.map(boundary => 
                    new BoundaryTreeItem(
                        boundary,
                        vscode.TreeItemCollapsibleState.Collapsed
                    )
                )
            );
        }

        // Show boundary details
        return Promise.resolve(this.getBoundaryDetails(element.boundary));
    }

    private getBoundaryDetails(boundary: BoundaryInfo): BoundaryTreeItem[] {
        const items: BoundaryTreeItem[] = [];

        // Type
        items.push(new BoundaryTreeItem(
            boundary,
            vscode.TreeItemCollapsibleState.None,
            true,
            `Type: ${boundary.type}`
        ));

        // Description
        if (boundary.description) {
            items.push(new BoundaryTreeItem(
                boundary,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Description: ${boundary.description}`
            ));
        }

        // Components
        boundary.components.forEach(component => {
            items.push(new BoundaryTreeItem(
                boundary,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Component: ${component}`
            ));
        });

        // Interfaces
        boundary.interfaces.forEach(iface => {
            items.push(new BoundaryTreeItem(
                boundary,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Interface: ${iface}`
            ));
        });

        return items;
    }
}

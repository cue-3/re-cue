/**
 * Use Cases Tree Provider
 * 
 * Provides a tree view of discovered use cases from the analysis.
 */

import * as vscode from 'vscode';
import { AnalysisManager, UseCaseInfo } from '../analysisManager';

/**
 * Tree item representing a use case
 */
export class UseCaseTreeItem extends vscode.TreeItem {
    constructor(
        public readonly useCase: UseCaseInfo,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly isDetail: boolean = false,
        public readonly detailLabel?: string
    ) {
        super(
            isDetail ? (detailLabel || '') : `${useCase.id}: ${useCase.name}`,
            collapsibleState
        );

        if (!isDetail) {
            this.tooltip = new vscode.MarkdownString(this.createTooltip());
            this.description = useCase.primaryActor;
            this.iconPath = new vscode.ThemeIcon('symbol-event');
            this.contextValue = 'useCase';

            if (useCase.filePath) {
                this.command = {
                    command: 'recue.navigateToItem',
                    title: 'Navigate to Use Case',
                    arguments: [{ filePath: useCase.filePath, line: useCase.line }]
                };
            }
        } else {
            this.iconPath = new vscode.ThemeIcon('debug-breakpoint');
        }
    }

    private createTooltip(): string {
        const uc = this.useCase;
        let tooltip = `**${uc.id}: ${uc.name}**\n\n`;
        tooltip += `**Primary Actor:** ${uc.primaryActor}\n\n`;
        
        if (uc.systemBoundary) {
            tooltip += `**System Boundary:** ${uc.systemBoundary}\n\n`;
        }

        if (uc.preconditions.length > 0) {
            tooltip += `**Preconditions:**\n`;
            uc.preconditions.forEach(p => tooltip += `- ${p}\n`);
            tooltip += '\n';
        }

        if (uc.mainScenario.length > 0) {
            tooltip += `**Main Scenario:**\n`;
            uc.mainScenario.forEach((step, i) => tooltip += `${i + 1}. ${step}\n`);
            tooltip += '\n';
        }

        if (uc.postconditions.length > 0) {
            tooltip += `**Postconditions:**\n`;
            uc.postconditions.forEach(p => tooltip += `- ${p}\n`);
        }

        return tooltip;
    }
}

/**
 * Tree data provider for use cases
 */
export class UseCasesTreeProvider implements vscode.TreeDataProvider<UseCaseTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<UseCaseTreeItem | undefined | null | void> = 
        new vscode.EventEmitter<UseCaseTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<UseCaseTreeItem | undefined | null | void> = 
        this._onDidChangeTreeData.event;

    constructor(private analysisManager: AnalysisManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: UseCaseTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: UseCaseTreeItem): Thenable<UseCaseTreeItem[]> {
        const result = this.analysisManager.getResult();
        
        if (!result || result.useCases.length === 0) {
            return Promise.resolve([]);
        }

        if (!element) {
            // Root level - show use cases
            return Promise.resolve(
                result.useCases.map(uc => 
                    new UseCaseTreeItem(
                        uc,
                        vscode.TreeItemCollapsibleState.Collapsed
                    )
                )
            );
        }

        // Show use case details
        return Promise.resolve(this.getUseCaseDetails(element.useCase));
    }

    private getUseCaseDetails(useCase: UseCaseInfo): UseCaseTreeItem[] {
        const items: UseCaseTreeItem[] = [];

        // Primary Actor
        items.push(new UseCaseTreeItem(
            useCase,
            vscode.TreeItemCollapsibleState.None,
            true,
            `Actor: ${useCase.primaryActor}`
        ));

        // System Boundary
        if (useCase.systemBoundary) {
            items.push(new UseCaseTreeItem(
                useCase,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Boundary: ${useCase.systemBoundary}`
            ));
        }

        // Preconditions count
        if (useCase.preconditions.length > 0) {
            items.push(new UseCaseTreeItem(
                useCase,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Preconditions: ${useCase.preconditions.length}`
            ));
        }

        // Main scenario steps count
        if (useCase.mainScenario.length > 0) {
            items.push(new UseCaseTreeItem(
                useCase,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Scenario Steps: ${useCase.mainScenario.length}`
            ));
        }

        // Postconditions count
        if (useCase.postconditions.length > 0) {
            items.push(new UseCaseTreeItem(
                useCase,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Postconditions: ${useCase.postconditions.length}`
            ));
        }

        // Extensions count
        if (useCase.extensions.length > 0) {
            items.push(new UseCaseTreeItem(
                useCase,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Extensions: ${useCase.extensions.length}`
            ));
        }

        return items;
    }
}

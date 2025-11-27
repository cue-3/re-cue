/**
 * Actors Tree Provider
 * 
 * Provides a tree view of discovered actors from the analysis.
 */

import * as vscode from 'vscode';
import { AnalysisManager, ActorInfo } from '../analysisManager';

/**
 * Tree item representing an actor
 */
export class ActorTreeItem extends vscode.TreeItem {
    constructor(
        public readonly actor: ActorInfo,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly isDetail: boolean = false,
        public readonly detailLabel?: string
    ) {
        super(
            isDetail ? (detailLabel || '') : actor.name,
            collapsibleState
        );

        if (!isDetail) {
            this.tooltip = new vscode.MarkdownString(this.createTooltip());
            this.description = actor.type;
            
            // Set icon based on actor type
            switch (actor.type) {
                case 'human':
                    this.iconPath = new vscode.ThemeIcon('person');
                    break;
                case 'system':
                    this.iconPath = new vscode.ThemeIcon('server');
                    break;
                case 'external':
                    this.iconPath = new vscode.ThemeIcon('cloud');
                    break;
                default:
                    this.iconPath = new vscode.ThemeIcon('account');
            }

            this.contextValue = 'actor';
        } else {
            this.iconPath = new vscode.ThemeIcon('info');
        }
    }

    private createTooltip(): string {
        const actor = this.actor;
        let tooltip = `**${actor.name}**\n\n`;
        tooltip += `**Type:** ${actor.type}\n\n`;
        
        if (actor.description) {
            tooltip += `**Description:** ${actor.description}\n\n`;
        }

        if (actor.roles.length > 0) {
            tooltip += `**Roles:**\n`;
            actor.roles.forEach(role => tooltip += `- ${role}\n`);
            tooltip += '\n';
        }

        tooltip += `**Identified from:** ${actor.identifiedFrom}`;

        return tooltip;
    }
}

/**
 * Tree data provider for actors
 */
export class ActorsTreeProvider implements vscode.TreeDataProvider<ActorTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<ActorTreeItem | undefined | null | void> = 
        new vscode.EventEmitter<ActorTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<ActorTreeItem | undefined | null | void> = 
        this._onDidChangeTreeData.event;

    constructor(private analysisManager: AnalysisManager) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ActorTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ActorTreeItem): Thenable<ActorTreeItem[]> {
        const result = this.analysisManager.getResult();
        
        if (!result || result.actors.length === 0) {
            return Promise.resolve([]);
        }

        if (!element) {
            // Root level - show actors grouped by type
            const humanActors = result.actors.filter(a => a.type === 'human');
            const systemActors = result.actors.filter(a => a.type === 'system');
            const externalActors = result.actors.filter(a => a.type === 'external');
            
            const items: ActorTreeItem[] = [];

            // Create category items if there are actors of that type
            if (humanActors.length > 0) {
                items.push(...humanActors.map(actor => 
                    new ActorTreeItem(actor, vscode.TreeItemCollapsibleState.Collapsed)
                ));
            }

            if (systemActors.length > 0) {
                items.push(...systemActors.map(actor => 
                    new ActorTreeItem(actor, vscode.TreeItemCollapsibleState.Collapsed)
                ));
            }

            if (externalActors.length > 0) {
                items.push(...externalActors.map(actor => 
                    new ActorTreeItem(actor, vscode.TreeItemCollapsibleState.Collapsed)
                ));
            }

            return Promise.resolve(items);
        }

        // Show actor details
        return Promise.resolve(this.getActorDetails(element.actor));
    }

    private getActorDetails(actor: ActorInfo): ActorTreeItem[] {
        const items: ActorTreeItem[] = [];

        // Type
        items.push(new ActorTreeItem(
            actor,
            vscode.TreeItemCollapsibleState.None,
            true,
            `Type: ${actor.type}`
        ));

        // Description
        if (actor.description) {
            items.push(new ActorTreeItem(
                actor,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Description: ${actor.description}`
            ));
        }

        // Roles
        actor.roles.forEach(role => {
            items.push(new ActorTreeItem(
                actor,
                vscode.TreeItemCollapsibleState.None,
                true,
                `Role: ${role}`
            ));
        });

        // Source
        items.push(new ActorTreeItem(
            actor,
            vscode.TreeItemCollapsibleState.None,
            true,
            `Source: ${actor.identifiedFrom}`
        ));

        return items;
    }
}

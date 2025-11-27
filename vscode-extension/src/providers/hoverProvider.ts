/**
 * Hover Provider
 * 
 * Provides inline documentation preview on hover for analyzed code elements.
 */

import * as vscode from 'vscode';
import { AnalysisManager } from '../analysisManager';

/**
 * Provides hover information for code elements
 */
export class HoverProvider implements vscode.HoverProvider {
    constructor(private analysisManager: AnalysisManager) {}

    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        _token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.Hover> {
        const config = vscode.workspace.getConfiguration('recue');
        if (!config.get<boolean>('enableHover')) {
            return null;
        }

        const result = this.analysisManager.getResult();
        if (!result) {
            return null;
        }

        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return null;
        }

        const word = document.getText(wordRange);
        const line = position.line + 1;
        const filePath = document.uri.fsPath;

        // Check for endpoint at this position
        const endpoint = result.endpoints.find(ep => 
            ep.filePath === filePath && 
            Math.abs(ep.line - line) <= 2 &&
            (ep.handler.includes(word) || ep.path.includes(word))
        );

        if (endpoint) {
            return new vscode.Hover(this.createEndpointHover(endpoint), wordRange);
        }

        // Check for model at this position
        const model = result.models.find(m => 
            m.filePath === filePath && 
            Math.abs(m.line - line) <= 2 &&
            m.name === word
        );

        if (model) {
            return new vscode.Hover(this.createModelHover(model), wordRange);
        }

        // Check for use case reference
        const useCase = result.useCases.find(uc => 
            uc.name.toLowerCase().includes(word.toLowerCase()) ||
            uc.primaryActor.toLowerCase() === word.toLowerCase()
        );

        if (useCase) {
            return new vscode.Hover(this.createUseCaseHover(useCase), wordRange);
        }

        // Check for actor reference
        const actor = result.actors.find(a => 
            a.name.toLowerCase() === word.toLowerCase() ||
            a.roles.some(r => r.toLowerCase() === word.toLowerCase())
        );

        if (actor) {
            return new vscode.Hover(this.createActorHover(actor), wordRange);
        }

        // Check for service at this position
        const service = result.services.find(s => 
            s.filePath === filePath && 
            Math.abs(s.line - line) <= 2 &&
            s.name === word
        );

        if (service) {
            return new vscode.Hover(this.createServiceHover(service), wordRange);
        }

        return null;
    }

    private createEndpointHover(endpoint: {
        method: string;
        path: string;
        handler: string;
        description?: string;
        parameters?: string[];
        responses?: string[];
    }): vscode.MarkdownString {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;

        md.appendMarkdown(`### 🌐 API Endpoint\n\n`);
        md.appendMarkdown(`**${endpoint.method}** \`${endpoint.path}\`\n\n`);
        md.appendMarkdown(`**Handler:** ${endpoint.handler}\n\n`);

        if (endpoint.description) {
            md.appendMarkdown(`**Description:** ${endpoint.description}\n\n`);
        }

        if (endpoint.parameters && endpoint.parameters.length > 0) {
            md.appendMarkdown(`**Parameters:**\n`);
            endpoint.parameters.forEach(p => md.appendMarkdown(`- ${p}\n`));
            md.appendMarkdown(`\n`);
        }

        if (endpoint.responses && endpoint.responses.length > 0) {
            md.appendMarkdown(`**Responses:**\n`);
            endpoint.responses.forEach(r => md.appendMarkdown(`- ${r}\n`));
        }

        md.appendMarkdown(`\n---\n*Discovered by RE-cue*`);

        return md;
    }

    private createModelHover(model: {
        name: string;
        fields: { name: string; type: string; annotations: string[] }[];
        relationships: string[];
    }): vscode.MarkdownString {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;

        md.appendMarkdown(`### 📦 Data Model\n\n`);
        md.appendMarkdown(`**${model.name}**\n\n`);

        if (model.fields.length > 0) {
            md.appendMarkdown(`**Fields:**\n`);
            model.fields.slice(0, 10).forEach(f => {
                md.appendMarkdown(`- \`${f.name}\`: ${f.type}`);
                if (f.annotations.length > 0) {
                    md.appendMarkdown(` (${f.annotations.join(', ')})`);
                }
                md.appendMarkdown(`\n`);
            });
            if (model.fields.length > 10) {
                md.appendMarkdown(`- ... and ${model.fields.length - 10} more fields\n`);
            }
            md.appendMarkdown(`\n`);
        }

        if (model.relationships.length > 0) {
            md.appendMarkdown(`**Relationships:**\n`);
            model.relationships.forEach(r => md.appendMarkdown(`- ${r}\n`));
        }

        md.appendMarkdown(`\n---\n*Discovered by RE-cue*`);

        return md;
    }

    private createUseCaseHover(useCase: {
        id: string;
        name: string;
        primaryActor: string;
        systemBoundary?: string;
        preconditions: string[];
        mainScenario: string[];
    }): vscode.MarkdownString {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;

        md.appendMarkdown(`### 📋 Use Case\n\n`);
        md.appendMarkdown(`**${useCase.id}: ${useCase.name}**\n\n`);
        md.appendMarkdown(`**Primary Actor:** ${useCase.primaryActor}\n\n`);

        if (useCase.systemBoundary) {
            md.appendMarkdown(`**System Boundary:** ${useCase.systemBoundary}\n\n`);
        }

        if (useCase.preconditions.length > 0) {
            md.appendMarkdown(`**Preconditions:**\n`);
            useCase.preconditions.slice(0, 3).forEach(p => md.appendMarkdown(`- ${p}\n`));
            if (useCase.preconditions.length > 3) {
                md.appendMarkdown(`- ... and ${useCase.preconditions.length - 3} more\n`);
            }
            md.appendMarkdown(`\n`);
        }

        if (useCase.mainScenario.length > 0) {
            md.appendMarkdown(`**Main Scenario:**\n`);
            useCase.mainScenario.slice(0, 3).forEach((s, i) => md.appendMarkdown(`${i + 1}. ${s}\n`));
            if (useCase.mainScenario.length > 3) {
                md.appendMarkdown(`... and ${useCase.mainScenario.length - 3} more steps\n`);
            }
        }

        md.appendMarkdown(`\n---\n*Discovered by RE-cue*`);

        return md;
    }

    private createActorHover(actor: {
        name: string;
        type: 'human' | 'system' | 'external';
        description?: string;
        roles: string[];
    }): vscode.MarkdownString {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;

        const icon = actor.type === 'human' ? '👤' : actor.type === 'system' ? '🖥️' : '☁️';
        md.appendMarkdown(`### ${icon} Actor\n\n`);
        md.appendMarkdown(`**${actor.name}** (${actor.type})\n\n`);

        if (actor.description) {
            md.appendMarkdown(`**Description:** ${actor.description}\n\n`);
        }

        if (actor.roles.length > 0) {
            md.appendMarkdown(`**Roles:**\n`);
            actor.roles.forEach(r => md.appendMarkdown(`- ${r}\n`));
        }

        md.appendMarkdown(`\n---\n*Discovered by RE-cue*`);

        return md;
    }

    private createServiceHover(service: {
        name: string;
        methods: string[];
        dependencies: string[];
    }): vscode.MarkdownString {
        const md = new vscode.MarkdownString();
        md.isTrusted = true;

        md.appendMarkdown(`### ⚙️ Service\n\n`);
        md.appendMarkdown(`**${service.name}**\n\n`);

        if (service.methods.length > 0) {
            md.appendMarkdown(`**Methods:**\n`);
            service.methods.slice(0, 5).forEach(m => md.appendMarkdown(`- \`${m}\`\n`));
            if (service.methods.length > 5) {
                md.appendMarkdown(`- ... and ${service.methods.length - 5} more\n`);
            }
            md.appendMarkdown(`\n`);
        }

        if (service.dependencies.length > 0) {
            md.appendMarkdown(`**Dependencies:**\n`);
            service.dependencies.forEach(d => md.appendMarkdown(`- ${d}\n`));
        }

        md.appendMarkdown(`\n---\n*Discovered by RE-cue*`);

        return md;
    }
}

/**
 * Base Extractor Interface
 * 
 * Defines the contract for language-specific code extractors.
 */

import { 
    CodeElement, 
    EndpointElement, 
    ServiceElement, 
    ModelElement, 
    ControllerElement,
    ParseResult,
    SupportedLanguage 
} from '../types';

/**
 * Interface for language-specific code extractors
 */
export interface LanguageExtractor {
    /** Language this extractor handles */
    readonly language: SupportedLanguage;
    
    /** File extensions this extractor can parse */
    readonly extensions: string[];
    
    /**
     * Parse a source file and extract code elements
     * @param content Source code content
     * @param filePath Absolute path to the file
     * @returns Parse result with extracted elements
     */
    parse(content: string, filePath: string): ParseResult;
    
    /**
     * Extract endpoints from source code
     * @param content Source code content
     * @param filePath Absolute path to the file
     * @returns Array of endpoint elements
     */
    extractEndpoints(content: string, filePath: string): EndpointElement[];
    
    /**
     * Extract services from source code
     * @param content Source code content
     * @param filePath Absolute path to the file
     * @returns Array of service elements
     */
    extractServices(content: string, filePath: string): ServiceElement[];
    
    /**
     * Extract models from source code
     * @param content Source code content
     * @param filePath Absolute path to the file
     * @returns Array of model elements
     */
    extractModels(content: string, filePath: string): ModelElement[];
    
    /**
     * Extract controllers from source code
     * @param content Source code content
     * @param filePath Absolute path to the file
     * @returns Array of controller elements
     */
    extractControllers?(content: string, filePath: string): ControllerElement[];
}

/**
 * Abstract base class providing common functionality for extractors
 */
export abstract class BaseExtractor implements LanguageExtractor {
    abstract readonly language: SupportedLanguage;
    abstract readonly extensions: string[];
    
    /**
     * Parse source code and extract all code elements
     */
    parse(content: string, filePath: string): ParseResult {
        const elements: CodeElement[] = [];
        const errors: string[] = [];
        
        try {
            // Extract different element types
            elements.push(...this.extractEndpoints(content, filePath));
            elements.push(...this.extractServices(content, filePath));
            elements.push(...this.extractModels(content, filePath));
            
            if (this.extractControllers) {
                elements.push(...this.extractControllers(content, filePath));
            }
        } catch (error) {
            errors.push(`Error parsing ${filePath}: ${error instanceof Error ? error.message : String(error)}`);
        }
        
        return {
            language: this.language,
            filePath,
            elements,
            errors: errors.length > 0 ? errors : undefined
        };
    }
    
    abstract extractEndpoints(content: string, filePath: string): EndpointElement[];
    abstract extractServices(content: string, filePath: string): ServiceElement[];
    abstract extractModels(content: string, filePath: string): ModelElement[];
    extractControllers?(content: string, filePath: string): ControllerElement[];
    
    /**
     * Find line number for a given position in content
     * @param content Full file content
     * @param position Character position in content
     * @returns 1-based line number
     */
    protected getLineNumber(content: string, position: number): number {
        const before = content.substring(0, position);
        return (before.match(/\n/g) || []).length + 1;
    }
    
    /**
     * Find the end line for a block starting at a given line
     * @param lines Array of lines
     * @param startLine 1-based start line
     * @param openBrace Opening brace character
     * @param closeBrace Closing brace character
     * @returns 1-based end line
     */
    protected findBlockEnd(lines: string[], startLine: number, openBrace = '{', closeBrace = '}'): number {
        let depth = 0;
        let foundStart = false;
        
        for (let i = startLine - 1; i < lines.length; i++) {
            const line = lines[i];
            for (const char of line) {
                if (char === openBrace) {
                    depth++;
                    foundStart = true;
                } else if (char === closeBrace) {
                    depth--;
                    if (foundStart && depth === 0) {
                        return i + 1; // Return 1-based line number
                    }
                }
            }
        }
        
        return startLine; // If no closing brace found, return start line
    }
    
    /**
     * Extract documentation comment above a given line
     * @param lines Array of lines
     * @param line 1-based line number
     * @returns Documentation string or undefined
     */
    protected extractDocumentation(lines: string[], line: number): string | undefined {
        const docLines: string[] = [];
        let i = line - 2; // Start from line above (0-indexed, so -2 for line above)
        
        // Look for JavaDoc/JSDoc style comments
        while (i >= 0) {
            const trimmed = lines[i].trim();
            
            if (trimmed.startsWith('*/')) {
                // Found end of doc comment, work backwards
                i--;
                while (i >= 0) {
                    const docLine = lines[i].trim();
                    if (docLine.startsWith('/**')) {
                        // Found start of doc comment
                        break;
                    } else if (docLine.startsWith('*')) {
                        docLines.unshift(docLine.substring(1).trim());
                    }
                    i--;
                }
                break;
            } else if (trimmed.startsWith('//')) {
                // Single line comments
                docLines.unshift(trimmed.substring(2).trim());
                i--;
            } else if (trimmed.startsWith('#')) {
                // Python comments
                docLines.unshift(trimmed.substring(1).trim());
                i--;
            } else if (trimmed === '' || trimmed.startsWith('@')) {
                // Empty line or annotation, continue looking
                i--;
            } else {
                break;
            }
        }
        
        return docLines.length > 0 ? docLines.join('\n') : undefined;
    }
}

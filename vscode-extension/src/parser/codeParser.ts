/**
 * Code Parser
 * 
 * Main entry point for parsing source code files.
 * Delegates to language-specific extractors based on file extension.
 */

import * as path from 'path';
import { 
    CodeElement, 
    ParseResult, 
    SupportedLanguage 
} from './types';
import { LanguageExtractor } from './extractors/baseExtractor';
import { JavaExtractor } from './extractors/javaExtractor';
import { TypeScriptExtractor } from './extractors/typescriptExtractor';
import { PythonExtractor } from './extractors/pythonExtractor';

/**
 * Main code parser that delegates to language-specific extractors
 */
export class CodeParser {
    private extractors: Map<string, LanguageExtractor>;
    
    constructor() {
        this.extractors = new Map();
        
        // Register extractors
        const javaExtractor = new JavaExtractor();
        const tsExtractor = new TypeScriptExtractor();
        const pythonExtractor = new PythonExtractor();
        
        // Map extensions to extractors
        for (const ext of javaExtractor.extensions) {
            this.extractors.set(ext, javaExtractor);
        }
        for (const ext of tsExtractor.extensions) {
            this.extractors.set(ext, tsExtractor);
        }
        for (const ext of pythonExtractor.extensions) {
            this.extractors.set(ext, pythonExtractor);
        }
    }
    
    /**
     * Check if a file can be parsed
     * @param filePath Path to the file
     * @returns True if the file extension is supported
     */
    canParse(filePath: string): boolean {
        const ext = path.extname(filePath).toLowerCase();
        return this.extractors.has(ext);
    }
    
    /**
     * Get the language for a file
     * @param filePath Path to the file
     * @returns Language or undefined if not supported
     */
    getLanguage(filePath: string): SupportedLanguage | undefined {
        const ext = path.extname(filePath).toLowerCase();
        const extractor = this.extractors.get(ext);
        return extractor?.language;
    }
    
    /**
     * Parse a source file and extract code elements
     * @param content Source code content
     * @param filePath Absolute path to the file
     * @returns Parse result with extracted elements
     */
    parse(content: string, filePath: string): ParseResult {
        const ext = path.extname(filePath).toLowerCase();
        const extractor = this.extractors.get(ext);
        
        if (!extractor) {
            return {
                language: 'typescript', // Default
                filePath,
                elements: [],
                errors: [`Unsupported file extension: ${ext}`]
            };
        }
        
        return extractor.parse(content, filePath);
    }
    
    /**
     * Get all supported file extensions
     * @returns Array of file extensions including the dot
     */
    getSupportedExtensions(): string[] {
        return Array.from(this.extractors.keys());
    }
    
    /**
     * Get extractor for a specific language
     * @param language Language to get extractor for
     * @returns Language extractor or undefined
     */
    getExtractor(language: SupportedLanguage): LanguageExtractor | undefined {
        // Find extractor by language
        for (const extractor of this.extractors.values()) {
            if (extractor.language === language) {
                return extractor;
            }
        }
        return undefined;
    }
    
    /**
     * Parse multiple files
     * @param files Array of {content, filePath} objects
     * @returns Array of parse results
     */
    parseMultiple(files: Array<{content: string; filePath: string}>): ParseResult[] {
        return files.map(file => this.parse(file.content, file.filePath));
    }
    
    /**
     * Merge multiple parse results into a single list of elements
     * @param results Array of parse results
     * @returns Combined array of code elements
     */
    static mergeResults(results: ParseResult[]): CodeElement[] {
        const elements: CodeElement[] = [];
        for (const result of results) {
            elements.push(...result.elements);
        }
        return elements;
    }
}

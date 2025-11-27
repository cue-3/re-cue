/**
 * TypeScript/JavaScript Extractor
 * 
 * Extracts code elements from TypeScript and JavaScript source files.
 * Supports Express, NestJS, and general TypeScript patterns.
 */

import { BaseExtractor } from './baseExtractor';
import { 
    EndpointElement, 
    ServiceElement, 
    ModelElement,
    HttpMethod,
    SupportedLanguage,
    Parameter,
    FieldInfo
} from '../types';

/**
 * Regex patterns for TypeScript/JavaScript
 */
const PATTERNS = {
    // NestJS decorators
    CONTROLLER: /@Controller\s*\(\s*['"]?([^'")\s]*)['"]?\s*\)/,
    INJECTABLE: /@Injectable\s*\(/,
    GET: /@Get\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g,
    POST: /@Post\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g,
    PUT: /@Put\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g,
    DELETE: /@Delete\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g,
    PATCH: /@Patch\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g,
    
    // Express patterns
    EXPRESS_GET: /(?:app|router)\.get\s*\(\s*['"`]([^'"`]+)['"`]/g,
    EXPRESS_POST: /(?:app|router)\.post\s*\(\s*['"`]([^'"`]+)['"`]/g,
    EXPRESS_PUT: /(?:app|router)\.put\s*\(\s*['"`]([^'"`]+)['"`]/g,
    EXPRESS_DELETE: /(?:app|router)\.delete\s*\(\s*['"`]([^'"`]+)['"`]/g,
    EXPRESS_PATCH: /(?:app|router)\.patch\s*\(\s*['"`]([^'"`]+)['"`]/g,
    EXPRESS_USE: /(?:app|router)\.use\s*\(\s*['"`]([^'"`]+)['"`]/g,
    
    // Class declaration
    CLASS_DECLARATION: /(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?\s*\{/g,
    
    // Function/Method declaration
    METHOD_DECLARATION: /(?:async\s+)?(\w+)\s*\(\s*([^)]*)\s*\)(?:\s*:\s*([^{]+))?\s*\{/g,
    ARROW_FUNCTION: /(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*[^=]+)?\s*=>/g,
    
    // Interface declaration
    INTERFACE_DECLARATION: /(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([\w\s,]+))?\s*\{/g,
    
    // Type declaration
    TYPE_DECLARATION: /(?:export\s+)?type\s+(\w+)\s*=\s*/g,
    
    // NestJS parameter decorators
    PARAM: /@Param\s*\(\s*['"]?(\w*)['"]?\s*\)/g,
    QUERY: /@Query\s*\(\s*['"]?(\w*)['"]?\s*\)/g,
    BODY: /@Body\s*\(\s*['"]?(\w*)['"]?\s*\)/g,
    
    // Dependency injection
    INJECT: /@Inject\s*\(\s*['"]?(\w+)['"]?\s*\)/g
};

/**
 * TypeScript/JavaScript code extractor
 */
export class TypeScriptExtractor extends BaseExtractor {
    readonly language: SupportedLanguage = 'typescript';
    readonly extensions: string[] = ['.ts', '.tsx', '.js', '.jsx'];
    
    /**
     * Extract REST endpoints from TypeScript/JavaScript source code
     */
    extractEndpoints(content: string, filePath: string): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        const lines = content.split('\n');
        
        // Try NestJS patterns first
        const nestEndpoints = this.extractNestJSEndpoints(content, filePath, lines);
        endpoints.push(...nestEndpoints);
        
        // Try Express patterns
        const expressEndpoints = this.extractExpressEndpoints(content, filePath, lines);
        endpoints.push(...expressEndpoints);
        
        return endpoints;
    }
    
    /**
     * Extract NestJS endpoints
     */
    private extractNestJSEndpoints(content: string, filePath: string, lines: string[]): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        
        // Find controller base path
        let basePath = '';
        const controllerMatch = content.match(PATTERNS.CONTROLLER);
        if (controllerMatch) {
            basePath = controllerMatch[1] || '';
        }
        
        // If no controller decorator, skip NestJS patterns
        if (!controllerMatch) {
            return endpoints;
        }
        
        // Find all endpoint methods
        const mappingTypes: Array<{ pattern: RegExp; method: HttpMethod }> = [
            { pattern: /@Get\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g, method: 'GET' },
            { pattern: /@Post\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g, method: 'POST' },
            { pattern: /@Put\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g, method: 'PUT' },
            { pattern: /@Delete\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g, method: 'DELETE' },
            { pattern: /@Patch\s*\(\s*['"]?([^'")]*)['"]?\s*\)/g, method: 'PATCH' }
        ];
        
        for (const { pattern, method } of mappingTypes) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const path = match[1] || '';
                const fullPath = this.normalizePath(basePath, path);
                const lineNumber = this.getLineNumber(content, match.index);
                
                // Find method name
                let methodName = '';
                let returnType = '';
                const parameters: Parameter[] = [];
                
                // Look for method declaration after the decorator
                for (let i = lineNumber - 1; i < Math.min(lineNumber + 5, lines.length); i++) {
                    const line = lines[i];
                    const methodMatch = line.match(/(?:async\s+)?(\w+)\s*\(/);
                    if (methodMatch && !line.includes('@')) {
                        methodName = methodMatch[1];
                        
                        // Try to extract return type
                        const returnMatch = line.match(/\)\s*:\s*([^{]+)/);
                        if (returnMatch) {
                            returnType = returnMatch[1].trim();
                        }
                        
                        // Extract parameters
                        this.extractNestJSParameters(lines, i, parameters);
                        break;
                    }
                }
                
                const documentation = this.extractDocumentation(lines, lineNumber);
                const endLine = this.findBlockEnd(lines, lineNumber);
                
                endpoints.push({
                    type: 'endpoint',
                    name: methodName || `${method.toLowerCase()}${fullPath.replace(/[/{}:]/g, '_')}`,
                    filePath,
                    startLine: lineNumber,
                    endLine,
                    httpMethod: method,
                    path: fullPath,
                    parameters,
                    returnType,
                    annotations: [method, 'NestJS'],
                    documentation
                });
            }
        }
        
        return endpoints;
    }
    
    /**
     * Extract Express endpoints
     */
    private extractExpressEndpoints(content: string, filePath: string, lines: string[]): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        
        const expressTypes: Array<{ pattern: RegExp; method: HttpMethod }> = [
            { pattern: /(?:app|router)\.get\s*\(\s*['"`]([^'"`]+)['"`]/g, method: 'GET' },
            { pattern: /(?:app|router)\.post\s*\(\s*['"`]([^'"`]+)['"`]/g, method: 'POST' },
            { pattern: /(?:app|router)\.put\s*\(\s*['"`]([^'"`]+)['"`]/g, method: 'PUT' },
            { pattern: /(?:app|router)\.delete\s*\(\s*['"`]([^'"`]+)['"`]/g, method: 'DELETE' },
            { pattern: /(?:app|router)\.patch\s*\(\s*['"`]([^'"`]+)['"`]/g, method: 'PATCH' }
        ];
        
        for (const { pattern, method } of expressTypes) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const path = match[1];
                const lineNumber = this.getLineNumber(content, match.index);
                
                const documentation = this.extractDocumentation(lines, lineNumber);
                
                // Find the end of the route handler
                let endLine = lineNumber;
                const line = lines[lineNumber - 1];
                if (line.includes('=>') || line.includes('function')) {
                    endLine = this.findBlockEnd(lines, lineNumber);
                }
                
                endpoints.push({
                    type: 'endpoint',
                    name: `${method.toLowerCase()}${path.replace(/[/{}:]/g, '_')}`,
                    filePath,
                    startLine: lineNumber,
                    endLine,
                    httpMethod: method,
                    path,
                    annotations: [method, 'Express'],
                    documentation
                });
            }
        }
        
        return endpoints;
    }
    
    /**
     * Extract NestJS parameter decorators
     */
    private extractNestJSParameters(lines: string[], startLine: number, parameters: Parameter[]): void {
        // Look at the method line for parameter decorators
        for (let i = startLine; i < Math.min(startLine + 5, lines.length); i++) {
            const line = lines[i];
            
            // Check for @Param
            const paramMatches = line.matchAll(/@Param\s*\(\s*['"]?(\w*)['"]?\s*\)\s*(\w+)(?:\s*:\s*(\w+))?/g);
            for (const match of paramMatches) {
                parameters.push({
                    name: match[1] || match[2],
                    type: match[3] || 'string',
                    description: 'Path parameter',
                    required: true
                });
            }
            
            // Check for @Query
            const queryMatches = line.matchAll(/@Query\s*\(\s*['"]?(\w*)['"]?\s*\)\s*(\w+)(?:\s*:\s*(\w+))?/g);
            for (const match of queryMatches) {
                parameters.push({
                    name: match[1] || match[2],
                    type: match[3] || 'string',
                    description: 'Query parameter'
                });
            }
            
            // Check for @Body
            const bodyMatches = line.matchAll(/@Body\s*\(\s*['"]?(\w*)['"]?\s*\)\s*(\w+)(?:\s*:\s*(\w+))?/g);
            for (const match of bodyMatches) {
                parameters.push({
                    name: match[1] || match[2],
                    type: match[3] || 'object',
                    description: 'Request body',
                    required: true
                });
            }
            
            // Stop if we hit a closing brace or another method
            if (line.includes('{') && !line.includes('@')) {break;}
        }
    }
    
    /**
     * Extract services from TypeScript source code
     */
    extractServices(content: string, filePath: string): ServiceElement[] {
        const services: ServiceElement[] = [];
        const lines = content.split('\n');
        
        // Check for NestJS Injectable decorator
        const isService = PATTERNS.INJECTABLE.test(content);
        
        if (!isService) {
            // Also check for classes ending with Service
            if (!content.includes('class') || !content.match(/class\s+\w+Service/)) {
                return services;
            }
        }
        
        // Find class declaration
        const classMatch = content.match(/(?:export\s+)?class\s+(\w+)/);
        if (!classMatch) {
            return services;
        }
        
        const className = classMatch[1];
        const classLine = this.getLineNumber(content, classMatch.index || 0);
        const endLine = this.findBlockEnd(lines, classLine);
        
        // Extract methods
        const methods: string[] = [];
        const methodPattern = /(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{/g;
        let methodMatch;
        while ((methodMatch = methodPattern.exec(content)) !== null) {
            const methodName = methodMatch[1];
            if (methodName !== 'constructor' && !methods.includes(methodName)) {
                methods.push(methodName);
            }
        }
        
        // Extract dependencies from constructor
        const dependencies: string[] = [];
        const constructorMatch = content.match(/constructor\s*\(([^)]+)\)/);
        if (constructorMatch) {
            const params = constructorMatch[1].split(',');
            for (const param of params) {
                const typeMatch = param.match(/(?:private|public|readonly)?\s*\w+\s*:\s*(\w+)/);
                if (typeMatch) {
                    dependencies.push(typeMatch[1]);
                }
            }
        }
        
        const documentation = this.extractDocumentation(lines, classLine);
        
        const annotations: string[] = [];
        if (isService) {annotations.push('Injectable');}
        
        services.push({
            type: 'service',
            name: className,
            filePath,
            startLine: classLine,
            endLine,
            methods,
            dependencies,
            annotations,
            documentation
        });
        
        return services;
    }
    
    /**
     * Extract models/interfaces from TypeScript source code
     */
    extractModels(content: string, filePath: string): ModelElement[] {
        const models: ModelElement[] = [];
        const lines = content.split('\n');
        
        // Extract interfaces
        const interfacePattern = /(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([\w\s,]+))?\s*\{/g;
        let interfaceMatch;
        while ((interfaceMatch = interfacePattern.exec(content)) !== null) {
            const name = interfaceMatch[1];
            const startLine = this.getLineNumber(content, interfaceMatch.index);
            const endLine = this.findBlockEnd(lines, startLine);
            
            // Extract fields
            const fields = this.extractInterfaceFields(lines, startLine, endLine);
            
            // Extract relationships from extends
            const relationships: string[] = [];
            if (interfaceMatch[2]) {
                const extended = interfaceMatch[2].split(',').map(e => e.trim());
                extended.forEach(e => relationships.push(`extends ${e}`));
            }
            
            const documentation = this.extractDocumentation(lines, startLine);
            
            models.push({
                type: 'model',
                name,
                filePath,
                startLine,
                endLine,
                fields,
                relationships,
                annotations: ['interface'],
                documentation
            });
        }
        
        // Extract type aliases that look like models
        const typePattern = /(?:export\s+)?type\s+(\w+)\s*=\s*\{/g;
        let typeMatch;
        while ((typeMatch = typePattern.exec(content)) !== null) {
            const name = typeMatch[1];
            const startLine = this.getLineNumber(content, typeMatch.index);
            const endLine = this.findBlockEnd(lines, startLine);
            
            const fields = this.extractInterfaceFields(lines, startLine, endLine);
            const documentation = this.extractDocumentation(lines, startLine);
            
            models.push({
                type: 'model',
                name,
                filePath,
                startLine,
                endLine,
                fields,
                relationships: [],
                annotations: ['type'],
                documentation
            });
        }
        
        // Extract classes that look like models (DTOs, Entities)
        const classPattern = /(?:export\s+)?class\s+(\w+(?:Dto|DTO|Entity|Model|Request|Response))/g;
        let classMatch;
        while ((classMatch = classPattern.exec(content)) !== null) {
            const name = classMatch[1];
            const startLine = this.getLineNumber(content, classMatch.index);
            const endLine = this.findBlockEnd(lines, startLine);
            
            const fields = this.extractClassFields(content, startLine, endLine);
            const documentation = this.extractDocumentation(lines, startLine);
            
            models.push({
                type: 'model',
                name,
                filePath,
                startLine,
                endLine,
                fields,
                relationships: [],
                annotations: ['class'],
                documentation
            });
        }
        
        return models;
    }
    
    /**
     * Extract fields from an interface
     */
    private extractInterfaceFields(lines: string[], startLine: number, endLine: number): FieldInfo[] {
        const fields: FieldInfo[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Skip empty lines, opening braces, and comments
            if (!line || line === '{' || line === '}' || line.startsWith('//') || line.startsWith('/*')) {
                continue;
            }
            
            // Match field pattern: name: type; or name?: type;
            const fieldMatch = line.match(/^(\w+)(\?)?:\s*([^;]+)/);
            if (fieldMatch) {
                fields.push({
                    name: fieldMatch[1],
                    type: fieldMatch[3].trim(),
                    annotations: fieldMatch[2] ? ['optional'] : undefined
                });
            }
        }
        
        return fields;
    }
    
    /**
     * Extract fields from a class
     */
    private extractClassFields(content: string, startLine: number, endLine: number): FieldInfo[] {
        const fields: FieldInfo[] = [];
        const lines = content.split('\n');
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Match class field patterns
            // @ApiProperty() field: type;
            // public/private field: type;
            const fieldMatch = line.match(/(?:@\w+\([^)]*\)\s*)?(?:public|private|protected|readonly)?\s*(\w+)(?:\?)?\s*:\s*([^;=]+)/);
            if (fieldMatch && (!line.includes('(') || line.includes('@'))) {
                const annotations: string[] = [];
                const annotationMatches = line.matchAll(/@(\w+)/g);
                for (const match of annotationMatches) {
                    annotations.push(match[1]);
                }
                
                fields.push({
                    name: fieldMatch[1],
                    type: fieldMatch[2].trim(),
                    annotations: annotations.length > 0 ? annotations : undefined
                });
            }
        }
        
        return fields;
    }
    
    /**
     * Normalize and combine path segments
     */
    private normalizePath(basePath: string, subPath: string): string {
        let result = basePath;
        
        // Ensure base path starts with /
        if (result && !result.startsWith('/')) {
            result = '/' + result;
        }
        
        // Add sub path
        if (subPath) {
            if (!subPath.startsWith('/') && result && !result.endsWith('/')) {
                result += '/';
            }
            result += subPath;
        }
        
        // Clean up double slashes
        result = result.replace(/\/+/g, '/');
        
        // Ensure starts with /
        if (!result.startsWith('/')) {
            result = '/' + result;
        }
        
        return result || '/';
    }
}

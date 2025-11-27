/**
 * Java Extractor
 * 
 * Extracts code elements from Java source files.
 * Supports Spring Boot annotations for endpoints, services, and models.
 */

import { BaseExtractor } from './baseExtractor';
import { 
    EndpointElement, 
    ServiceElement, 
    ModelElement, 
    ControllerElement,
    HttpMethod,
    SupportedLanguage,
    Parameter,
    FieldInfo
} from '../types';

/**
 * Regex patterns for Java annotations and declarations
 */
const PATTERNS = {
    // Class annotations
    REST_CONTROLLER: /@RestController\b/,
    CONTROLLER: /@Controller\b/,
    SERVICE: /@Service\b/,
    COMPONENT: /@Component\b/,
    REPOSITORY: /@Repository\b/,
    ENTITY: /@Entity\b/,
    TABLE: /@Table\b/,
    
    // Request mapping annotations
    REQUEST_MAPPING: /@RequestMapping\s*\(\s*(?:value\s*=\s*)?["']([^"']+)["'](?:\s*,\s*method\s*=\s*RequestMethod\.(\w+))?\)/,
    GET_MAPPING: /@GetMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/,
    POST_MAPPING: /@PostMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/,
    PUT_MAPPING: /@PutMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/,
    DELETE_MAPPING: /@DeleteMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/,
    PATCH_MAPPING: /@PatchMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/,
    
    // Class declaration
    CLASS_DECLARATION: /(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?\s*\{/g,
    
    // Method declaration
    METHOD_DECLARATION: /(?:public|private|protected)?\s*(?:static\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)/g,
    
    // Field declaration
    FIELD_DECLARATION: /(?:@\w+(?:\([^)]*\))?\s*)*(?:private|protected|public)\s+(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*(?:=|;)/g,
    
    // Annotations
    ANNOTATION: /@(\w+)(?:\(([^)]*)\))?/g,
    
    // Path variable and request parameters
    PATH_VARIABLE: /@PathVariable(?:\s*\(\s*(?:value\s*=\s*)?["']?(\w+)["']?\s*\))?\s+\w+\s+(\w+)/g,
    REQUEST_PARAM: /@RequestParam(?:\s*\(\s*(?:value\s*=\s*)?["']?(\w+)["']?(?:\s*,\s*required\s*=\s*(\w+))?\s*\))?\s+\w+\s+(\w+)/g,
    REQUEST_BODY: /@RequestBody\s+(\w+(?:<[^>]+>)?)\s+(\w+)/g,
    
    // Autowired dependencies
    AUTOWIRED: /@Autowired\s*(?:\n\s*)?(?:private\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)/g,
    
    // JPA annotations
    ID: /@Id\b/,
    COLUMN: /@Column\b/,
    MANY_TO_ONE: /@ManyToOne\b/,
    ONE_TO_MANY: /@OneToMany\b/,
    MANY_TO_MANY: /@ManyToMany\b/,
    ONE_TO_ONE: /@OneToOne\b/
};

/**
 * Java code extractor for Spring Boot applications
 */
export class JavaExtractor extends BaseExtractor {
    readonly language: SupportedLanguage = 'java';
    readonly extensions: string[] = ['.java'];
    
    /**
     * Extract REST endpoints from Java source code
     */
    extractEndpoints(content: string, filePath: string): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        const lines = content.split('\n');
        
        // First find controller base path
        let basePath = '';
        const requestMappingMatch = content.match(/@RequestMapping\s*\(\s*(?:value\s*=\s*)?["']([^"']+)["']/);
        if (requestMappingMatch) {
            basePath = requestMappingMatch[1];
        }
        
        // Check if this is a controller
        const isController = PATTERNS.REST_CONTROLLER.test(content) || PATTERNS.CONTROLLER.test(content);
        if (!isController) {
            return endpoints;
        }
        
        // Find all endpoint methods
        const mappingTypes: Array<{ pattern: RegExp; method: HttpMethod }> = [
            { pattern: /@GetMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/g, method: 'GET' },
            { pattern: /@PostMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/g, method: 'POST' },
            { pattern: /@PutMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/g, method: 'PUT' },
            { pattern: /@DeleteMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/g, method: 'DELETE' },
            { pattern: /@PatchMapping\s*(?:\(\s*(?:value\s*=\s*)?["']?([^"')]*?)["']?\s*\))?/g, method: 'PATCH' }
        ];
        
        for (const { pattern, method } of mappingTypes) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const path = match[1] || '';
                const fullPath = this.normalizePath(basePath, path);
                const lineNumber = this.getLineNumber(content, match.index);
                
                // Find the method name (next line typically has the method declaration)
                let methodName = '';
                let returnType = '';
                const parameters: Parameter[] = [];
                
                // Look for method declaration after the annotation
                for (let i = lineNumber - 1; i < Math.min(lineNumber + 5, lines.length); i++) {
                    const line = lines[i];
                    const methodMatch = line.match(/(?:public|private|protected)?\s*(?:ResponseEntity<)?(\w+)>?\s+(\w+)\s*\(/);
                    if (methodMatch && !line.includes('@')) {
                        returnType = methodMatch[1];
                        methodName = methodMatch[2];
                        
                        // Extract parameters from this method
                        this.extractMethodParameters(lines, i, parameters);
                        break;
                    }
                }
                
                // Extract documentation
                const documentation = this.extractDocumentation(lines, lineNumber);
                
                // Find end of method block
                const endLine = this.findBlockEnd(lines, lineNumber);
                
                // Extract annotations for this method
                const annotations: string[] = [];
                for (let i = Math.max(0, lineNumber - 5); i < lineNumber; i++) {
                    const annotationMatch = lines[i].match(/@(\w+)/);
                    if (annotationMatch) {
                        annotations.push(annotationMatch[1]);
                    }
                }
                
                endpoints.push({
                    type: 'endpoint',
                    name: methodName || `${method.toLowerCase()}${fullPath.replace(/[/{}]/g, '_')}`,
                    filePath,
                    startLine: lineNumber,
                    endLine,
                    httpMethod: method,
                    path: fullPath,
                    parameters,
                    returnType,
                    annotations,
                    documentation
                });
            }
        }
        
        // Also handle @RequestMapping with method specified
        const reqMappingPattern = /@RequestMapping\s*\([^)]*method\s*=\s*RequestMethod\.(\w+)[^)]*(?:value\s*=\s*)?["']?([^"'),]*)/g;
        let match;
        while ((match = reqMappingPattern.exec(content)) !== null) {
            // Skip class-level @RequestMapping
            const lineNumber = this.getLineNumber(content, match.index);
            const line = lines[lineNumber - 1];
            if (line.match(/class\s+\w+/)) {
                continue;
            }
            
            const method = match[1].toUpperCase() as HttpMethod;
            const path = match[2] || '';
            const fullPath = this.normalizePath(basePath, path);
            
            const endLine = this.findBlockEnd(lines, lineNumber);
            const documentation = this.extractDocumentation(lines, lineNumber);
            
            endpoints.push({
                type: 'endpoint',
                name: `${method.toLowerCase()}${fullPath.replace(/[/{}]/g, '_')}`,
                filePath,
                startLine: lineNumber,
                endLine,
                httpMethod: method,
                path: fullPath,
                documentation
            });
        }
        
        return endpoints;
    }
    
    /**
     * Extract parameters from a method declaration
     */
    private extractMethodParameters(lines: string[], startLine: number, parameters: Parameter[]): void {
        // Collect the full method signature (may span multiple lines)
        let signature = '';
        let depth = 0;
        let started = false;
        
        for (let i = startLine; i < Math.min(startLine + 10, lines.length); i++) {
            const line = lines[i];
            for (const char of line) {
                if (char === '(') {
                    depth++;
                    started = true;
                } else if (char === ')') {
                    depth--;
                    if (started && depth === 0) {
                        signature += char;
                        break;
                    }
                }
                if (started) {
                    signature += char;
                }
            }
            if (started && depth === 0) {break;}
            signature += ' ';
        }
        
        // Parse parameters from signature
        const paramContent = signature.slice(1, -1); // Remove parentheses
        const paramParts = this.splitParameters(paramContent);
        
        for (const param of paramParts) {
            const trimmed = param.trim();
            if (!trimmed) {continue;}
            
            // Check for annotations
            const pathVarMatch = trimmed.match(/@PathVariable(?:\s*\([^)]*\))?\s+(\w+)\s+(\w+)/);
            if (pathVarMatch) {
                parameters.push({
                    name: pathVarMatch[2],
                    type: pathVarMatch[1],
                    description: 'Path variable',
                    required: true
                });
                continue;
            }
            
            const reqParamMatch = trimmed.match(/@RequestParam(?:\s*\([^)]*\))?\s+(\w+)\s+(\w+)/);
            if (reqParamMatch) {
                parameters.push({
                    name: reqParamMatch[2],
                    type: reqParamMatch[1],
                    description: 'Request parameter'
                });
                continue;
            }
            
            const reqBodyMatch = trimmed.match(/@RequestBody\s+(\w+(?:<[^>]+>)?)\s+(\w+)/);
            if (reqBodyMatch) {
                parameters.push({
                    name: reqBodyMatch[2],
                    type: reqBodyMatch[1],
                    description: 'Request body',
                    required: true
                });
            }
        }
    }
    
    /**
     * Split parameter string respecting generics
     */
    private splitParameters(paramString: string): string[] {
        const params: string[] = [];
        let current = '';
        let depth = 0;
        
        for (const char of paramString) {
            if (char === '<') {depth++;}
            else if (char === '>') {depth--;}
            else if (char === ',' && depth === 0) {
                params.push(current);
                current = '';
                continue;
            }
            current += char;
        }
        if (current.trim()) {
            params.push(current);
        }
        
        return params;
    }
    
    /**
     * Extract service classes from Java source code
     */
    extractServices(content: string, filePath: string): ServiceElement[] {
        const services: ServiceElement[] = [];
        const lines = content.split('\n');
        
        // Check for service annotations
        const isService = PATTERNS.SERVICE.test(content) || 
                         PATTERNS.COMPONENT.test(content) ||
                         PATTERNS.REPOSITORY.test(content);
        
        if (!isService) {
            return services;
        }
        
        // Find class declaration
        const classMatch = content.match(/(?:public\s+)?(?:abstract\s+)?class\s+(\w+)/);
        if (!classMatch) {
            return services;
        }
        
        const className = classMatch[1];
        const classLine = this.getLineNumber(content, classMatch.index || 0);
        const endLine = this.findBlockEnd(lines, classLine);
        
        // Extract methods
        const methods: string[] = [];
        const methodPattern = /(?:public|protected)\s+(?!class\b)(\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)/g;
        let methodMatch;
        while ((methodMatch = methodPattern.exec(content)) !== null) {
            methods.push(methodMatch[2]);
        }
        
        // Extract dependencies (Autowired fields)
        const dependencies: string[] = [];
        const autowiredPattern = /@Autowired[\s\S]*?(?:private\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)/g;
        let depMatch;
        while ((depMatch = autowiredPattern.exec(content)) !== null) {
            dependencies.push(depMatch[1]);
        }
        
        // Also check for constructor injection
        const constructorPattern = /(?:public\s+)?\w+\s*\(([^)]+)\)\s*\{/;
        const constructorMatch = content.match(constructorPattern);
        if (constructorMatch) {
            const params = constructorMatch[1].split(',');
            for (const param of params) {
                const typeMatch = param.trim().match(/(\w+(?:<[^>]+>)?)\s+\w+/);
                if (typeMatch && !dependencies.includes(typeMatch[1])) {
                    dependencies.push(typeMatch[1]);
                }
            }
        }
        
        // Extract annotations
        const annotations: string[] = [];
        if (PATTERNS.SERVICE.test(content)) {annotations.push('Service');}
        if (PATTERNS.COMPONENT.test(content)) {annotations.push('Component');}
        if (PATTERNS.REPOSITORY.test(content)) {annotations.push('Repository');}
        
        const documentation = this.extractDocumentation(lines, classLine);
        
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
     * Extract model/entity classes from Java source code
     */
    extractModels(content: string, filePath: string): ModelElement[] {
        const models: ModelElement[] = [];
        const lines = content.split('\n');
        
        // Check for entity/model annotations
        const isModel = PATTERNS.ENTITY.test(content) || 
                       PATTERNS.TABLE.test(content) ||
                       content.includes('class') && (
                           content.includes('Model') ||
                           content.includes('Entity') ||
                           content.includes('DTO') ||
                           content.includes('Dto')
                       );
        
        if (!isModel && !PATTERNS.ENTITY.test(content)) {
            return models;
        }
        
        // Find class declaration
        const classMatch = content.match(/(?:public\s+)?(?:abstract\s+)?class\s+(\w+)/);
        if (!classMatch) {
            return models;
        }
        
        const className = classMatch[1];
        const classLine = this.getLineNumber(content, classMatch.index || 0);
        const endLine = this.findBlockEnd(lines, classLine);
        
        // Extract fields
        const fields: FieldInfo[] = [];
        const fieldPattern = /((?:@\w+(?:\([^)]*\))?\s*)+)?(?:private|protected|public)\s+(?:final\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*(?:=|;)/g;
        let fieldMatch;
        while ((fieldMatch = fieldPattern.exec(content)) !== null) {
            const annotationsStr = fieldMatch[1] || '';
            const type = fieldMatch[2];
            const name = fieldMatch[3];
            
            // Extract annotations
            const fieldAnnotations: string[] = [];
            const annotationMatches = annotationsStr.matchAll(/@(\w+)/g);
            for (const match of annotationMatches) {
                fieldAnnotations.push(match[1]);
            }
            
            fields.push({
                name,
                type,
                annotations: fieldAnnotations
            });
        }
        
        // Extract relationships
        const relationships: string[] = [];
        if (PATTERNS.MANY_TO_ONE.test(content)) {
            const mtoMatch = content.match(/@ManyToOne[\s\S]*?(\w+)\s+\w+/);
            if (mtoMatch) {
                relationships.push(`ManyToOne -> ${mtoMatch[1]}`);
            }
        }
        if (PATTERNS.ONE_TO_MANY.test(content)) {
            const otmMatch = content.match(/@OneToMany[\s\S]*?(\w+)<(\w+)>\s+\w+/);
            if (otmMatch) {
                relationships.push(`OneToMany -> ${otmMatch[2]}`);
            }
        }
        if (PATTERNS.MANY_TO_MANY.test(content)) {
            const mtmMatch = content.match(/@ManyToMany[\s\S]*?(\w+)<(\w+)>\s+\w+/);
            if (mtmMatch) {
                relationships.push(`ManyToMany -> ${mtmMatch[2]}`);
            }
        }
        if (PATTERNS.ONE_TO_ONE.test(content)) {
            const otoMatch = content.match(/@OneToOne[\s\S]*?(\w+)\s+\w+/);
            if (otoMatch) {
                relationships.push(`OneToOne -> ${otoMatch[1]}`);
            }
        }
        
        // Extract annotations
        const annotations: string[] = [];
        if (PATTERNS.ENTITY.test(content)) {annotations.push('Entity');}
        if (PATTERNS.TABLE.test(content)) {annotations.push('Table');}
        
        const documentation = this.extractDocumentation(lines, classLine);
        
        models.push({
            type: 'model',
            name: className,
            filePath,
            startLine: classLine,
            endLine,
            fields,
            relationships,
            annotations,
            documentation
        });
        
        return models;
    }
    
    /**
     * Extract controller classes from Java source code
     */
    extractControllers(content: string, filePath: string): ControllerElement[] {
        const controllers: ControllerElement[] = [];
        const lines = content.split('\n');
        
        // Check for controller annotations
        const isController = PATTERNS.REST_CONTROLLER.test(content) || PATTERNS.CONTROLLER.test(content);
        if (!isController) {
            return controllers;
        }
        
        // Find class declaration
        const classMatch = content.match(/(?:public\s+)?(?:abstract\s+)?class\s+(\w+)/);
        if (!classMatch) {
            return controllers;
        }
        
        const className = classMatch[1];
        const classLine = this.getLineNumber(content, classMatch.index || 0);
        const endLine = this.findBlockEnd(lines, classLine);
        
        // Get base path
        let basePath = '';
        const requestMappingMatch = content.match(/@RequestMapping\s*\(\s*(?:value\s*=\s*)?["']([^"']+)["']/);
        if (requestMappingMatch) {
            basePath = requestMappingMatch[1];
        }
        
        // Get endpoints in this controller
        const endpoints = this.extractEndpoints(content, filePath);
        
        // Extract annotations
        const annotations: string[] = [];
        if (PATTERNS.REST_CONTROLLER.test(content)) {annotations.push('RestController');}
        if (PATTERNS.CONTROLLER.test(content)) {annotations.push('Controller');}
        
        const documentation = this.extractDocumentation(lines, classLine);
        
        controllers.push({
            type: 'controller',
            name: className,
            filePath,
            startLine: classLine,
            endLine,
            basePath,
            endpoints,
            annotations,
            documentation
        });
        
        return controllers;
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

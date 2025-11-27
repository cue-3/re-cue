/**
 * Python Extractor
 * 
 * Extracts code elements from Python source files.
 * Supports Flask, FastAPI, and Django patterns.
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
 * Regex patterns for Python frameworks
 * Note: These patterns are reference documentation for the extraction logic below
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const _PATTERNS = {
    // Flask patterns
    FLASK_ROUTE: /@(?:app|bp|blueprint)\.route\s*\(\s*['"]([^'"]+)['"](?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?\s*\)/g,
    FLASK_GET: /@(?:app|bp|blueprint)\.get\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
    FLASK_POST: /@(?:app|bp|blueprint)\.post\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
    FLASK_PUT: /@(?:app|bp|blueprint)\.put\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
    FLASK_DELETE: /@(?:app|bp|blueprint)\.delete\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
    FLASK_PATCH: /@(?:app|bp|blueprint)\.patch\s*\(\s*['"]([^'"]+)['"]\s*\)/g,
    
    // FastAPI patterns
    FASTAPI_GET: /@(?:app|router)\.get\s*\(\s*['"]([^'"]+)['"]/g,
    FASTAPI_POST: /@(?:app|router)\.post\s*\(\s*['"]([^'"]+)['"]/g,
    FASTAPI_PUT: /@(?:app|router)\.put\s*\(\s*['"]([^'"]+)['"]/g,
    FASTAPI_DELETE: /@(?:app|router)\.delete\s*\(\s*['"]([^'"]+)['"]/g,
    FASTAPI_PATCH: /@(?:app|router)\.patch\s*\(\s*['"]([^'"]+)['"]/g,
    
    // Django patterns
    DJANGO_PATH: /path\s*\(\s*['"]([^'"]+)['"](?:\s*,\s*[\w.]+)?/g,
    DJANGO_URL: /url\s*\(\s*r?['"]([^'"]+)['"](?:\s*,\s*[\w.]+)?/g,
    
    // Class patterns
    CLASS_DECLARATION: /class\s+(\w+)(?:\s*\(([^)]*)\))?\s*:/g,
    
    // Function patterns
    FUNCTION_DECLARATION: /def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?\s*:/g,
    ASYNC_FUNCTION: /async\s+def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?\s*:/g,
    
    // Django Model
    DJANGO_MODEL: /class\s+(\w+)\s*\(\s*(?:models\.Model|Model)\s*\)\s*:/g,
    
    // Pydantic/SQLAlchemy
    PYDANTIC_MODEL: /class\s+(\w+)\s*\(\s*(?:BaseModel|Schema)\s*\)\s*:/g,
    SQLALCHEMY_MODEL: /class\s+(\w+)\s*\(\s*(?:Base|db\.Model)\s*\)\s*:/g,
    
    // Field patterns
    DJANGO_FIELD: /(\w+)\s*=\s*models\.(\w+Field)\s*\(([^)]*)\)/g,
    PYDANTIC_FIELD: /(\w+)\s*:\s*([^=\n]+)(?:\s*=\s*Field\s*\([^)]*\))?/g,
    SQLALCHEMY_COLUMN: /(\w+)\s*=\s*(?:db\.)?Column\s*\(([^)]+)\)/g
};

/**
 * Python code extractor for Flask, FastAPI, and Django
 */
export class PythonExtractor extends BaseExtractor {
    readonly language: SupportedLanguage = 'python';
    readonly extensions: string[] = ['.py'];
    
    /**
     * Extract REST endpoints from Python source code
     */
    extractEndpoints(content: string, filePath: string): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        const lines = content.split('\n');
        
        // Try Flask patterns
        const flaskEndpoints = this.extractFlaskEndpoints(content, filePath, lines);
        endpoints.push(...flaskEndpoints);
        
        // Try FastAPI patterns
        const fastapiEndpoints = this.extractFastAPIEndpoints(content, filePath, lines);
        endpoints.push(...fastapiEndpoints);
        
        // Try Django URL patterns (only in urls.py files)
        if (filePath.includes('urls.py')) {
            const djangoEndpoints = this.extractDjangoUrls(content, filePath, lines);
            endpoints.push(...djangoEndpoints);
        }
        
        return endpoints;
    }
    
    /**
     * Extract Flask endpoints
     */
    private extractFlaskEndpoints(content: string, filePath: string, lines: string[]): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        
        // Check for Flask imports
        if (!content.includes('flask') && !content.includes('Flask')) {
            return endpoints;
        }
        
        // Handle @app.route with methods parameter
        const routePattern = /@(?:app|bp|blueprint)\.route\s*\(\s*['"]([^'"]+)['"](?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?\s*\)/g;
        let match;
        while ((match = routePattern.exec(content)) !== null) {
            const path = match[1];
            const methodsStr = match[2];
            const lineNumber = this.getLineNumber(content, match.index);
            
            // Parse methods
            const methods: HttpMethod[] = [];
            if (methodsStr) {
                const methodMatches = methodsStr.matchAll(/['"](\w+)['"]/g);
                for (const m of methodMatches) {
                    methods.push(m[1].toUpperCase() as HttpMethod);
                }
            } else {
                methods.push('GET'); // Default to GET
            }
            
            // Find function name
            const funcName = this.findNextFunctionName(lines, lineNumber);
            const documentation = this.extractPythonDocstring(lines, lineNumber);
            const endLine = this.findPythonBlockEnd(lines, lineNumber);
            
            // Create endpoint for each method
            for (const method of methods) {
                endpoints.push({
                    type: 'endpoint',
                    name: funcName || `${method.toLowerCase()}${path.replace(/[/{}:<>]/g, '_')}`,
                    filePath,
                    startLine: lineNumber,
                    endLine,
                    httpMethod: method,
                    path,
                    annotations: ['Flask', method],
                    documentation
                });
            }
        }
        
        // Handle specific method decorators
        const methodPatterns: Array<{ pattern: RegExp; method: HttpMethod }> = [
            { pattern: /@(?:app|bp|blueprint)\.get\s*\(\s*['"]([^'"]+)['"]\s*\)/g, method: 'GET' },
            { pattern: /@(?:app|bp|blueprint)\.post\s*\(\s*['"]([^'"]+)['"]\s*\)/g, method: 'POST' },
            { pattern: /@(?:app|bp|blueprint)\.put\s*\(\s*['"]([^'"]+)['"]\s*\)/g, method: 'PUT' },
            { pattern: /@(?:app|bp|blueprint)\.delete\s*\(\s*['"]([^'"]+)['"]\s*\)/g, method: 'DELETE' },
            { pattern: /@(?:app|bp|blueprint)\.patch\s*\(\s*['"]([^'"]+)['"]\s*\)/g, method: 'PATCH' }
        ];
        
        for (const { pattern, method } of methodPatterns) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const path = match[1];
                const lineNumber = this.getLineNumber(content, match.index);
                const funcName = this.findNextFunctionName(lines, lineNumber);
                const documentation = this.extractPythonDocstring(lines, lineNumber);
                const endLine = this.findPythonBlockEnd(lines, lineNumber);
                
                endpoints.push({
                    type: 'endpoint',
                    name: funcName || `${method.toLowerCase()}${path.replace(/[/{}:<>]/g, '_')}`,
                    filePath,
                    startLine: lineNumber,
                    endLine,
                    httpMethod: method,
                    path,
                    annotations: ['Flask', method],
                    documentation
                });
            }
        }
        
        return endpoints;
    }
    
    /**
     * Extract FastAPI endpoints
     */
    private extractFastAPIEndpoints(content: string, filePath: string, lines: string[]): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        
        // Check for FastAPI imports
        if (!content.includes('fastapi') && !content.includes('FastAPI') && !content.includes('APIRouter')) {
            return endpoints;
        }
        
        const methodPatterns: Array<{ pattern: RegExp; method: HttpMethod }> = [
            { pattern: /@(?:app|router)\.get\s*\(\s*['"]([^'"]+)['"]/g, method: 'GET' },
            { pattern: /@(?:app|router)\.post\s*\(\s*['"]([^'"]+)['"]/g, method: 'POST' },
            { pattern: /@(?:app|router)\.put\s*\(\s*['"]([^'"]+)['"]/g, method: 'PUT' },
            { pattern: /@(?:app|router)\.delete\s*\(\s*['"]([^'"]+)['"]/g, method: 'DELETE' },
            { pattern: /@(?:app|router)\.patch\s*\(\s*['"]([^'"]+)['"]/g, method: 'PATCH' }
        ];
        
        for (const { pattern, method } of methodPatterns) {
            let match;
            while ((match = pattern.exec(content)) !== null) {
                const path = match[1];
                const lineNumber = this.getLineNumber(content, match.index);
                const funcName = this.findNextFunctionName(lines, lineNumber);
                const documentation = this.extractPythonDocstring(lines, lineNumber);
                const endLine = this.findPythonBlockEnd(lines, lineNumber);
                
                // Extract parameters from function signature
                const parameters = this.extractFastAPIParameters(lines, lineNumber);
                
                endpoints.push({
                    type: 'endpoint',
                    name: funcName || `${method.toLowerCase()}${path.replace(/[/{}:<>]/g, '_')}`,
                    filePath,
                    startLine: lineNumber,
                    endLine,
                    httpMethod: method,
                    path,
                    parameters,
                    annotations: ['FastAPI', method],
                    documentation
                });
            }
        }
        
        return endpoints;
    }
    
    /**
     * Extract Django URL patterns
     */
    private extractDjangoUrls(content: string, filePath: string, _lines: string[]): EndpointElement[] {
        const endpoints: EndpointElement[] = [];
        
        // Match path() calls
        const pathPattern = /path\s*\(\s*['"]([^'"]+)['"](?:\s*,\s*([\w.]+))?/g;
        let match;
        while ((match = pathPattern.exec(content)) !== null) {
            const path = match[1];
            const viewName = match[2];
            const lineNumber = this.getLineNumber(content, match.index);
            
            endpoints.push({
                type: 'endpoint',
                name: viewName || path.replace(/[/{}:<>]/g, '_'),
                filePath,
                startLine: lineNumber,
                endLine: lineNumber,
                httpMethod: 'GET', // Django URLs don't specify method in urls.py
                path: '/' + path,
                annotations: ['Django'],
                documentation: viewName ? `View: ${viewName}` : undefined
            });
        }
        
        // Match url() calls (older Django)
        const urlPattern = /url\s*\(\s*r?['"]([^'"]+)['"](?:\s*,\s*([\w.]+))?/g;
        while ((match = urlPattern.exec(content)) !== null) {
            const path = match[1];
            const viewName = match[2];
            const lineNumber = this.getLineNumber(content, match.index);
            
            endpoints.push({
                type: 'endpoint',
                name: viewName || path.replace(/[/{}:<>^$]/g, '_'),
                filePath,
                startLine: lineNumber,
                endLine: lineNumber,
                httpMethod: 'GET',
                path: '/' + path.replace(/[^$]/g, ''),
                annotations: ['Django'],
                documentation: viewName ? `View: ${viewName}` : undefined
            });
        }
        
        return endpoints;
    }
    
    /**
     * Extract FastAPI parameters from function signature
     */
    private extractFastAPIParameters(lines: string[], startLine: number): Parameter[] {
        const parameters: Parameter[] = [];
        
        // Find function definition
        for (let i = startLine - 1; i < Math.min(startLine + 10, lines.length); i++) {
            const line = lines[i];
            const funcMatch = line.match(/(?:async\s+)?def\s+\w+\s*\(([^)]*)/);
            if (funcMatch) {
                let paramStr = funcMatch[1];
                
                // If parameters continue to next line
                if (!line.includes(')')) {
                    for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
                        paramStr += ' ' + lines[j];
                        if (lines[j].includes(')')) {break;}
                    }
                }
                
                // Parse parameters
                const params = paramStr.split(',');
                for (const param of params) {
                    const trimmed = param.trim();
                    if (!trimmed || trimmed === 'self' || trimmed.startsWith('*')) {continue;}
                    
                    // Match name: Type = Default
                    const paramMatch = trimmed.match(/(\w+)\s*:\s*([^=]+)(?:\s*=\s*(.+))?/);
                    if (paramMatch) {
                        const name = paramMatch[1];
                        const type = paramMatch[2].trim();
                        
                        // Determine if required
                        const required = !paramMatch[3] || paramMatch[3].includes('...');
                        
                        parameters.push({
                            name,
                            type,
                            required
                        });
                    }
                }
                break;
            }
        }
        
        return parameters;
    }
    
    /**
     * Find the next function name after a decorator
     */
    private findNextFunctionName(lines: string[], startLine: number): string {
        for (let i = startLine - 1; i < Math.min(startLine + 10, lines.length); i++) {
            const line = lines[i];
            const funcMatch = line.match(/(?:async\s+)?def\s+(\w+)\s*\(/);
            if (funcMatch) {
                return funcMatch[1];
            }
        }
        return '';
    }
    
    /**
     * Extract Python docstring
     */
    private extractPythonDocstring(lines: string[], startLine: number): string | undefined {
        // Find function definition
        let funcLine = -1;
        for (let i = startLine - 1; i < Math.min(startLine + 10, lines.length); i++) {
            if (lines[i].match(/(?:async\s+)?def\s+\w+\s*\(/)) {
                funcLine = i;
                break;
            }
        }
        
        if (funcLine === -1) {return undefined;}
        
        // Look for docstring after function definition
        for (let i = funcLine + 1; i < Math.min(funcLine + 3, lines.length); i++) {
            const line = lines[i].trim();
            
            if (line.startsWith('"""') || line.startsWith("'''")) {
                const quote = line.startsWith('"""') ? '"""' : "'''";
                
                // Single line docstring
                if (line.endsWith(quote) && line.length > 6) {
                    return line.slice(3, -3).trim();
                }
                
                // Multi-line docstring
                const docLines: string[] = [line.slice(3)];
                for (let j = i + 1; j < Math.min(i + 20, lines.length); j++) {
                    const docLine = lines[j];
                    if (docLine.includes(quote)) {
                        docLines.push(docLine.slice(0, docLine.indexOf(quote)));
                        break;
                    }
                    docLines.push(docLine.trim());
                }
                return docLines.join('\n').trim();
            }
        }
        
        return undefined;
    }
    
    /**
     * Find end of Python block using indentation
     */
    private findPythonBlockEnd(lines: string[], startLine: number): number {
        // Find function definition first
        let funcLine = -1;
        let baseIndent = 0;
        
        for (let i = startLine - 1; i < Math.min(startLine + 10, lines.length); i++) {
            const line = lines[i];
            const funcMatch = line.match(/^(\s*)(?:async\s+)?def\s+\w+\s*\(/);
            if (funcMatch) {
                funcLine = i;
                baseIndent = funcMatch[1].length;
                break;
            }
        }
        
        if (funcLine === -1) {return startLine;}
        
        // Find first non-empty line after function def to get body indent
        let bodyIndent = -1;
        for (let i = funcLine + 1; i < lines.length; i++) {
            const line = lines[i];
            if (line.trim() === '') {continue;}
            
            const match = line.match(/^(\s*)/);
            if (match) {
                bodyIndent = match[1].length;
                if (bodyIndent <= baseIndent) {
                    // No body
                    return funcLine + 1;
                }
                break;
            }
        }
        
        if (bodyIndent === -1) {return funcLine + 1;}
        
        // Find where indentation returns to base level or less
        for (let i = funcLine + 1; i < lines.length; i++) {
            const line = lines[i];
            if (line.trim() === '') {continue;}
            
            const match = line.match(/^(\s*)/);
            if (match && match[1].length <= baseIndent) {
                return i;
            }
        }
        
        return lines.length;
    }
    
    /**
     * Extract services from Python source code
     */
    extractServices(content: string, filePath: string): ServiceElement[] {
        const services: ServiceElement[] = [];
        const lines = content.split('\n');
        
        // Look for classes that end with Service or have service patterns
        const classPattern = /class\s+(\w+(?:Service|Manager|Handler|Provider))\s*(?:\([^)]*\))?\s*:/g;
        let match;
        
        while ((match = classPattern.exec(content)) !== null) {
            const className = match[1];
            const startLine = this.getLineNumber(content, match.index);
            const endLine = this.findPythonClassEnd(lines, startLine);
            
            // Extract methods
            const methods = this.extractClassMethods(lines, startLine, endLine);
            
            // Extract dependencies from __init__
            const dependencies = this.extractPythonDependencies(lines, startLine, endLine);
            
            const documentation = this.extractPythonDocstring(lines, startLine);
            
            services.push({
                type: 'service',
                name: className,
                filePath,
                startLine,
                endLine,
                methods,
                dependencies,
                annotations: ['Service'],
                documentation
            });
        }
        
        return services;
    }
    
    /**
     * Extract models from Python source code
     */
    extractModels(content: string, filePath: string): ModelElement[] {
        const models: ModelElement[] = [];
        const lines = content.split('\n');
        
        // Django models
        const djangoPattern = /class\s+(\w+)\s*\(\s*(?:models\.Model|Model)\s*\)\s*:/g;
        let match;
        
        while ((match = djangoPattern.exec(content)) !== null) {
            const name = match[1];
            const startLine = this.getLineNumber(content, match.index);
            const endLine = this.findPythonClassEnd(lines, startLine);
            
            const fields = this.extractDjangoFields(lines, startLine, endLine);
            const relationships = this.extractDjangoRelationships(lines, startLine, endLine);
            const documentation = this.extractPythonDocstring(lines, startLine);
            
            models.push({
                type: 'model',
                name,
                filePath,
                startLine,
                endLine,
                fields,
                relationships,
                annotations: ['Django', 'Model'],
                documentation
            });
        }
        
        // Pydantic models
        const pydanticPattern = /class\s+(\w+)\s*\(\s*(?:BaseModel|Schema)\s*\)\s*:/g;
        while ((match = pydanticPattern.exec(content)) !== null) {
            const name = match[1];
            const startLine = this.getLineNumber(content, match.index);
            const endLine = this.findPythonClassEnd(lines, startLine);
            
            const fields = this.extractPydanticFields(lines, startLine, endLine);
            const documentation = this.extractPythonDocstring(lines, startLine);
            
            models.push({
                type: 'model',
                name,
                filePath,
                startLine,
                endLine,
                fields,
                relationships: [],
                annotations: ['Pydantic', 'BaseModel'],
                documentation
            });
        }
        
        // SQLAlchemy models
        const sqlalchemyPattern = /class\s+(\w+)\s*\(\s*(?:Base|db\.Model)\s*\)\s*:/g;
        while ((match = sqlalchemyPattern.exec(content)) !== null) {
            const name = match[1];
            const startLine = this.getLineNumber(content, match.index);
            const endLine = this.findPythonClassEnd(lines, startLine);
            
            const fields = this.extractSQLAlchemyFields(lines, startLine, endLine);
            const relationships = this.extractSQLAlchemyRelationships(lines, startLine, endLine);
            const documentation = this.extractPythonDocstring(lines, startLine);
            
            models.push({
                type: 'model',
                name,
                filePath,
                startLine,
                endLine,
                fields,
                relationships,
                annotations: ['SQLAlchemy'],
                documentation
            });
        }
        
        return models;
    }
    
    /**
     * Find end of Python class using indentation
     */
    private findPythonClassEnd(lines: string[], startLine: number): number {
        const line = lines[startLine - 1];
        const match = line.match(/^(\s*)/);
        const baseIndent = match ? match[1].length : 0;
        
        for (let i = startLine; i < lines.length; i++) {
            const currentLine = lines[i];
            if (currentLine.trim() === '') {continue;}
            
            const currentMatch = currentLine.match(/^(\s*)/);
            if (currentMatch && currentMatch[1].length <= baseIndent && currentLine.trim() !== '') {
                return i;
            }
        }
        
        return lines.length;
    }
    
    /**
     * Extract methods from a Python class
     */
    private extractClassMethods(lines: string[], startLine: number, endLine: number): string[] {
        const methods: string[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i];
            const methodMatch = line.match(/def\s+(\w+)\s*\(/);
            if (methodMatch && !methodMatch[1].startsWith('_')) {
                methods.push(methodMatch[1]);
            }
        }
        
        return methods;
    }
    
    /**
     * Extract dependencies from __init__ method
     */
    private extractPythonDependencies(lines: string[], startLine: number, endLine: number): string[] {
        const dependencies: string[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i];
            
            // Look for __init__ parameters
            if (line.includes('def __init__')) {
                const paramMatch = line.match(/def __init__\s*\(\s*self\s*,?\s*([^)]*)\)/);
                if (paramMatch) {
                    const params = paramMatch[1].split(',');
                    for (const param of params) {
                        const typeMatch = param.match(/(\w+)\s*:\s*(\w+)/);
                        if (typeMatch) {
                            dependencies.push(typeMatch[2]);
                        }
                    }
                }
            }
        }
        
        return dependencies;
    }
    
    /**
     * Extract Django model fields
     */
    private extractDjangoFields(lines: string[], startLine: number, endLine: number): FieldInfo[] {
        const fields: FieldInfo[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            const fieldMatch = line.match(/(\w+)\s*=\s*models\.(\w+Field)\s*\(/);
            if (fieldMatch) {
                fields.push({
                    name: fieldMatch[1],
                    type: fieldMatch[2],
                    annotations: ['Django']
                });
            }
        }
        
        return fields;
    }
    
    /**
     * Extract Django model relationships
     */
    private extractDjangoRelationships(lines: string[], startLine: number, endLine: number): string[] {
        const relationships: string[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            
            const fkMatch = line.match(/(\w+)\s*=\s*models\.ForeignKey\s*\(\s*['"]?(\w+)['"]?/);
            if (fkMatch) {
                relationships.push(`ForeignKey -> ${fkMatch[2]}`);
            }
            
            const m2mMatch = line.match(/(\w+)\s*=\s*models\.ManyToManyField\s*\(\s*['"]?(\w+)['"]?/);
            if (m2mMatch) {
                relationships.push(`ManyToMany -> ${m2mMatch[2]}`);
            }
            
            const o2oMatch = line.match(/(\w+)\s*=\s*models\.OneToOneField\s*\(\s*['"]?(\w+)['"]?/);
            if (o2oMatch) {
                relationships.push(`OneToOne -> ${o2oMatch[2]}`);
            }
        }
        
        return relationships;
    }
    
    /**
     * Extract Pydantic model fields
     */
    private extractPydanticFields(lines: string[], startLine: number, endLine: number): FieldInfo[] {
        const fields: FieldInfo[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Match name: Type or name: Type = default
            const fieldMatch = line.match(/^(\w+)\s*:\s*([^=\n]+)(?:\s*=)?/);
            if (fieldMatch && !line.startsWith('class') && !line.startsWith('def')) {
                fields.push({
                    name: fieldMatch[1],
                    type: fieldMatch[2].trim(),
                    annotations: ['Pydantic']
                });
            }
        }
        
        return fields;
    }
    
    /**
     * Extract SQLAlchemy model fields
     */
    private extractSQLAlchemyFields(lines: string[], startLine: number, endLine: number): FieldInfo[] {
        const fields: FieldInfo[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            
            const columnMatch = line.match(/(\w+)\s*=\s*(?:db\.)?Column\s*\(\s*(?:db\.)?(\w+)/);
            if (columnMatch) {
                fields.push({
                    name: columnMatch[1],
                    type: columnMatch[2],
                    annotations: ['SQLAlchemy', 'Column']
                });
            }
        }
        
        return fields;
    }
    
    /**
     * Extract SQLAlchemy relationships
     */
    private extractSQLAlchemyRelationships(lines: string[], startLine: number, endLine: number): string[] {
        const relationships: string[] = [];
        
        for (let i = startLine; i < endLine && i < lines.length; i++) {
            const line = lines[i].trim();
            
            const relMatch = line.match(/(\w+)\s*=\s*(?:db\.)?relationship\s*\(\s*['"](\w+)['"]/);
            if (relMatch) {
                relationships.push(`relationship -> ${relMatch[2]}`);
            }
            
            const fkMatch = line.match(/ForeignKey\s*\(\s*['"]([^'"]+)['"]/);
            if (fkMatch) {
                relationships.push(`ForeignKey -> ${fkMatch[1]}`);
            }
        }
        
        return relationships;
    }
}

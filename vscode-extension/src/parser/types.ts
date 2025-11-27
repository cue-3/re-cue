/**
 * Types for Code Parsing
 * 
 * Defines shared types and interfaces for the code parsing system.
 */

/**
 * Types of code elements that can be detected
 */
export type CodeElementType = 
    | 'endpoint' 
    | 'service' 
    | 'model' 
    | 'controller' 
    | 'method'
    | 'class'
    | 'function';

/**
 * HTTP method for endpoints
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';

/**
 * Parameter information for methods and endpoints
 */
export interface Parameter {
    name: string;
    type: string;
    description?: string;
    required?: boolean;
}

/**
 * Code element with location information
 */
export interface CodeElement {
    /** Type of code element */
    type: CodeElementType;
    /** Name of the element */
    name: string;
    /** Absolute file path */
    filePath: string;
    /** 1-based start line number */
    startLine: number;
    /** 1-based end line number */
    endLine: number;
    /** Annotations/decorators found on this element */
    annotations?: string[];
    /** Parameters for methods and endpoints */
    parameters?: Parameter[];
    /** Return type for methods */
    returnType?: string;
    /** Documentation comment if present */
    documentation?: string;
}

/**
 * Endpoint-specific element with HTTP method and path
 */
export interface EndpointElement extends CodeElement {
    type: 'endpoint';
    /** HTTP method (GET, POST, etc.) */
    httpMethod: HttpMethod;
    /** URL path pattern */
    path: string;
    /** Response types */
    responses?: string[];
}

/**
 * Service element with dependency information
 */
export interface ServiceElement extends CodeElement {
    type: 'service';
    /** Methods provided by the service */
    methods: string[];
    /** Dependencies injected into the service */
    dependencies: string[];
}

/**
 * Model element with fields and relationships
 */
export interface ModelElement extends CodeElement {
    type: 'model';
    /** Fields in the model */
    fields: FieldInfo[];
    /** Relationships to other models */
    relationships: string[];
}

/**
 * Field information for models
 */
export interface FieldInfo {
    name: string;
    type: string;
    annotations?: string[];
    description?: string;
}

/**
 * Controller element grouping endpoints
 */
export interface ControllerElement extends CodeElement {
    type: 'controller';
    /** Base path for all endpoints in this controller */
    basePath?: string;
    /** Endpoints defined in this controller */
    endpoints: EndpointElement[];
}

/**
 * Code index structure for efficient querying
 */
export interface CodeIndex {
    /** All elements by unique key (filePath:line:name) */
    elements: Map<string, CodeElement>;
    /** Map from file path to elements in that file */
    fileToElements: Map<string, CodeElement[]>;
    /** Reverse index from element name to file paths */
    nameToFiles: Map<string, string[]>;
    /** Endpoints indexed by path */
    endpointsByPath: Map<string, EndpointElement[]>;
    /** Services indexed by name */
    servicesByName: Map<string, ServiceElement[]>;
    /** Models indexed by name */
    modelsByName: Map<string, ModelElement[]>;
}

/**
 * Supported programming languages
 */
export type SupportedLanguage = 'java' | 'typescript' | 'javascript' | 'python' | 'ruby' | 'csharp';

/**
 * Parse result from a language extractor
 */
export interface ParseResult {
    /** Language that was parsed */
    language: SupportedLanguage;
    /** File path that was parsed */
    filePath: string;
    /** All code elements found */
    elements: CodeElement[];
    /** Parse errors if any */
    errors?: string[];
}

/**
 * Use case information for cross-referencing
 */
export interface UseCaseInfo {
    id: string;
    name: string;
    primaryActor: string;
    systemBoundary?: string;
    preconditions: string[];
    mainScenario: string[];
    postconditions: string[];
    extensions: string[];
    filePath?: string;
    line?: number;
}

/**
 * Actor information for cross-referencing
 */
export interface ActorInfo {
    id: string;
    name: string;
    type: 'human' | 'system' | 'external';
    description?: string;
    roles: string[];
    identifiedFrom: string;
}

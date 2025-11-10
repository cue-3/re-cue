"""
Core analyzer module for discovering project components.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from .utils import log_info


class SecurityPatternAnalyzer:
    """Analyzes Spring Security patterns to identify actors and their roles."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the security pattern analyzer."""
        self.verbose = verbose
        
        # Spring Security annotation patterns
        self.security_patterns = {
            'preauthorize_role': re.compile(r'@PreAuthorize\s*\(\s*["\']hasRole\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'preauthorize_authority': re.compile(r'@PreAuthorize\s*\(\s*["\']hasAuthority\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'secured_single': re.compile(r'@Secured\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
            'secured_multiple': re.compile(r'@Secured\s*\(\s*\{\s*([^}]+)\s*\}', re.IGNORECASE),
            'roles_allowed': re.compile(r'@RolesAllowed\s*\(\s*["\']?([^"\')\s]+)', re.IGNORECASE),
            'permit_all': re.compile(r'@PermitAll|permitAll\(\)', re.IGNORECASE),
            'deny_all': re.compile(r'@DenyAll|denyAll\(\)', re.IGNORECASE),
        }
        
        # Role classification patterns
        self.role_classifications = {
            'admin': ['ADMIN', 'ADMINISTRATOR', 'ROOT', 'SUPER', 'MANAGER'],
            'user': ['USER', 'MEMBER', 'CUSTOMER', 'CLIENT'],
            'moderator': ['MODERATOR', 'MOD', 'EDITOR'],
            'guest': ['GUEST', 'ANONYMOUS', 'PUBLIC'],
            'system': ['SYSTEM', 'SERVICE', 'API', 'INTERNAL'],
        }
    
    def analyze_security_annotations(self, java_files: List[Path]) -> List[Dict]:
        """Analyze Java files for Spring Security annotations."""
        actors = []
        roles_found = set()
        
        for java_file in java_files:
            try:
                content = java_file.read_text(encoding='utf-8')
                file_roles = self._extract_roles_from_content(content, java_file)
                roles_found.update(file_roles)
                
            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze {java_file.name}: {e}")
                continue
        
        # Convert roles to actors
        for role in roles_found:
            actor = self._create_actor_from_role(role)
            if actor and not any(a['name'] == actor['name'] for a in actors):
                actors.append(actor)
        
        return actors
    
    def _extract_roles_from_content(self, content: str, java_file: Path) -> List[str]:
        """Extract roles from Java file content."""
        roles = []
        
        # Extract roles from @PreAuthorize with hasRole
        for match in self.security_patterns['preauthorize_role'].finditer(content):
            role = match.group(1).strip()
            roles.append(role)
            if self.verbose:
                log_info(f"  Found role '{role}' in @PreAuthorize: {java_file.name}")
        
        # Extract authorities from @PreAuthorize with hasAuthority
        for match in self.security_patterns['preauthorize_authority'].finditer(content):
            authority = match.group(1).strip()
            roles.append(authority)
            if self.verbose:
                log_info(f"  Found authority '{authority}' in @PreAuthorize: {java_file.name}")
        
        # Extract roles from @Secured (single role)
        for match in self.security_patterns['secured_single'].finditer(content):
            role = match.group(1).strip()
            roles.append(role)
            if self.verbose:
                log_info(f"  Found role '{role}' in @Secured: {java_file.name}")
        
        # Extract roles from @Secured (multiple roles)
        for match in self.security_patterns['secured_multiple'].finditer(content):
            roles_text = match.group(1)
            # Parse multiple roles like "ROLE_ADMIN", "ROLE_USER"
            role_matches = re.findall(r'["\']([^"\']+)["\']', roles_text)
            for role in role_matches:
                roles.append(role.strip())
                if self.verbose:
                    log_info(f"  Found role '{role}' in @Secured array: {java_file.name}")
        
        # Extract roles from @RolesAllowed
        for match in self.security_patterns['roles_allowed'].finditer(content):
            role = match.group(1).strip().strip('"\'')
            roles.append(role)
            if self.verbose:
                log_info(f"  Found role '{role}' in @RolesAllowed: {java_file.name}")
        
        # Check for public endpoints
        if self.security_patterns['permit_all'].search(content):
            roles.append('PUBLIC')
            if self.verbose:
                log_info(f"  Found public access in: {java_file.name}")
        
        return roles
    
    def _create_actor_from_role(self, role: str) -> Optional[Dict]:
        """Create an actor from a role/authority string."""
        # Clean up role name (remove ROLE_ prefix if present)
        clean_role = role.replace('ROLE_', '').strip()
        
        if not clean_role or clean_role in ['', 'null', 'undefined']:
            return None
        
        # Classify the role
        actor_type = self._classify_role(clean_role)
        access_level = self._determine_access_level(clean_role)
        
        # Generate human-readable name
        display_name = self._generate_display_name(clean_role)
        
        return {
            'name': display_name,
            'type': actor_type,
            'access_level': access_level,
            'roles': [role],
            'identified_from': [f"Security annotation: {role}"]
        }
    
    def _classify_role(self, role: str) -> str:
        """Classify a role into actor types."""
        role_upper = role.upper()
        
        for actor_type, keywords in self.role_classifications.items():
            if any(keyword in role_upper for keyword in keywords):
                if actor_type == 'guest':
                    return 'end_user'
                elif actor_type == 'system':
                    return 'external_system'
                else:
                    return 'internal_user'
        
        # Default classification
        return 'end_user'
    
    def _determine_access_level(self, role: str) -> str:
        """Determine access level from role."""
        role_upper = role.upper()
        
        if any(keyword in role_upper for keyword in ['ADMIN', 'ROOT', 'SUPER']):
            return 'admin'
        elif any(keyword in role_upper for keyword in ['MANAGER', 'MODERATOR', 'EDITOR']):
            return 'privileged'
        elif any(keyword in role_upper for keyword in ['SYSTEM', 'SERVICE', 'API']):
            return 'api_integration'
        elif any(keyword in role_upper for keyword in ['PUBLIC', 'GUEST', 'ANONYMOUS']):
            return 'public'
        else:
            return 'authenticated'
    
    def _generate_display_name(self, role: str) -> str:
        """Generate a human-readable display name from role."""
        # Convert from SCREAMING_SNAKE_CASE to Title Case
        words = role.replace('_', ' ').replace('-', ' ').split()
        return ' '.join(word.capitalize() for word in words)
    
    def analyze_spring_security_config(self, config_files: List[Path]) -> List[Dict]:
        """Analyze Spring Security configuration files for additional actor information."""
        actors = []
        
        for config_file in config_files:
            try:
                if config_file.suffix in ['.java', '.xml', '.yml', '.yaml', '.properties']:
                    content = config_file.read_text(encoding='utf-8')
                    config_actors = self._extract_actors_from_config(content, config_file)
                    actors.extend(config_actors)
                    
            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze config {config_file.name}: {e}")
                continue
        
        return actors
    
    def _extract_actors_from_config(self, content: str, config_file: Path) -> List[Dict]:
        """Extract actor information from configuration files."""
        actors = []
        
        # Look for role hierarchy definitions
        role_hierarchy_pattern = re.compile(r'roleHierarchy.*?=.*?([A-Z_]+(?:\s*>\s*[A-Z_]+)*)', re.IGNORECASE | re.DOTALL)
        for match in role_hierarchy_pattern.finditer(content):
            hierarchy_text = match.group(1)
            roles = re.findall(r'[A-Z_]+', hierarchy_text)
            
            for role in roles:
                actor = self._create_actor_from_role(role)
                if actor:
                    actor['identified_from'].append(f"Security config: {config_file.name}")
                    actors.append(actor)
        
        # Look for user details service configurations
        user_details_pattern = re.compile(r'withUser\s*\(\s*["\']([^"\']+)["\'].*?roles?\s*\(\s*["\']([^"\']+)', re.IGNORECASE)
        for match in user_details_pattern.finditer(content):
            username = match.group(1)
            role = match.group(2)
            
            actor = self._create_actor_from_role(role)
            if actor:
                actor['identified_from'].append(f"User config: {config_file.name}")
                actors.append(actor)
        
        return actors


class ExternalSystemDetector:
    """Detects external systems and third-party integrations."""
    
    def __init__(self, verbose: bool = False):
        """Initialize the external system detector."""
        self.verbose = verbose
        
        # Patterns for detecting external system integrations
        self.integration_patterns = {
            'rest_client': re.compile(r'@RestTemplate|WebClient|RestClient|HttpClient|OkHttpClient', re.IGNORECASE),
            'message_queue': re.compile(r'@RabbitListener|@KafkaListener|@JmsListener|MessageProducer|@Queue', re.IGNORECASE),
            'database_external': re.compile(r'jdbc:[^:]+://([^/:]+)', re.IGNORECASE),
            'web_service': re.compile(r'@WebServiceClient|@Service.*Client|SoapClient', re.IGNORECASE),
            'cache_system': re.compile(r'@Cacheable|RedisTemplate|JedisPool|HazelcastInstance', re.IGNORECASE),
            'payment_gateway': re.compile(r'stripe|paypal|square|braintree|worldpay', re.IGNORECASE),
            'notification': re.compile(r'twilio|sendgrid|mailgun|sns|ses', re.IGNORECASE),
            'cloud_services': re.compile(r'amazonaws|azure|gcp|firebase|cloudinary', re.IGNORECASE),
        }
        
        # URL patterns for common services
        self.url_patterns = {
            'stripe': re.compile(r'api\.stripe\.com', re.IGNORECASE),
            'paypal': re.compile(r'api\.paypal\.com|api\.sandbox\.paypal\.com', re.IGNORECASE),
            'twilio': re.compile(r'api\.twilio\.com', re.IGNORECASE),
            'sendgrid': re.compile(r'api\.sendgrid\.com', re.IGNORECASE),
            'aws': re.compile(r'amazonaws\.com', re.IGNORECASE),
            'github': re.compile(r'api\.github\.com', re.IGNORECASE),
            'slack': re.compile(r'hooks\.slack\.com|slack\.com/api', re.IGNORECASE),
            'google': re.compile(r'googleapis\.com', re.IGNORECASE),
        }
    
    def detect_external_systems(self, java_files: List[Path], config_files: List[Path] = None) -> List[Dict]:
        """Detect external systems from Java files and configuration."""
        external_systems = []
        
        # Analyze Java files
        for java_file in java_files:
            try:
                content = java_file.read_text(encoding='utf-8')
                systems = self._analyze_java_file(content, java_file)
                external_systems.extend(systems)
                
            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze {java_file.name}: {e}")
                continue
        
        # Analyze configuration files if provided
        if config_files:
            for config_file in config_files:
                try:
                    content = config_file.read_text(encoding='utf-8')
                    systems = self._analyze_config_file(content, config_file)
                    external_systems.extend(systems)
                    
                except Exception as e:
                    if self.verbose:
                        log_info(f"Warning: Could not analyze config {config_file.name}: {e}")
                    continue
        
        # Deduplicate external systems
        unique_systems = []
        system_names_seen = set()
        
        for system in external_systems:
            if system['name'] not in system_names_seen:
                system_names_seen.add(system['name'])
                unique_systems.append(system)
            else:
                # Merge evidence
                existing = next(s for s in unique_systems if s['name'] == system['name'])
                for evidence in system['identified_from']:
                    if evidence not in existing['identified_from']:
                        existing['identified_from'].append(evidence)
        
        return unique_systems
    
    def _analyze_java_file(self, content: str, java_file: Path) -> List[Dict]:
        """Analyze Java file for external system integrations."""
        systems = []
        
        # Check for REST client patterns
        if self.integration_patterns['rest_client'].search(content):
            # Extract URLs to identify specific services
            url_pattern = re.compile(r'["\']https?://([^/"\']+)[^"\']*["\']')
            urls = url_pattern.findall(content)
            
            for url in urls:
                system_name = self._infer_system_name_from_url(url)
                if system_name:
                    systems.append({
                        'name': system_name,
                        'type': 'external_system',
                        'access_level': 'api_integration',
                        'integration_type': 'rest_api',
                        'identified_from': [f"REST client in {java_file.name}"]
                    })
                    if self.verbose:
                        log_info(f"  Found external REST API: {system_name} in {java_file.name}")
        
        # Check for message queue integrations
        if self.integration_patterns['message_queue'].search(content):
            queue_names = re.findall(r'queue\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            for queue in queue_names:
                system_name = f"Message Queue ({queue})"
                systems.append({
                    'name': system_name,
                    'type': 'external_system',
                    'access_level': 'api_integration',
                    'integration_type': 'message_queue',
                    'identified_from': [f"Message queue in {java_file.name}"]
                })
                if self.verbose:
                    log_info(f"  Found message queue: {system_name} in {java_file.name}")
        
        # Check for external database connections
        db_matches = self.integration_patterns['database_external'].findall(content)
        for db_host in db_matches:
            if not any(local in db_host.lower() for local in ['localhost', '127.0.0.1', '0.0.0.0']):
                system_name = f"External Database ({db_host})"
                systems.append({
                    'name': system_name,
                    'type': 'external_system',
                    'access_level': 'api_integration',
                    'integration_type': 'database',
                    'identified_from': [f"Database connection in {java_file.name}"]
                })
                if self.verbose:
                    log_info(f"  Found external database: {system_name} in {java_file.name}")
        
        # Check for specific service patterns
        for service_type, pattern in self.integration_patterns.items():
            if service_type in ['payment_gateway', 'notification', 'cloud_services']:
                if pattern.search(content):
                    system_name = f"{service_type.replace('_', ' ').title()} Service"
                    systems.append({
                        'name': system_name,
                        'type': 'external_system',
                        'access_level': 'api_integration',
                        'integration_type': service_type,
                        'identified_from': [f"{service_type} pattern in {java_file.name}"]
                    })
                    if self.verbose:
                        log_info(f"  Found {service_type}: {system_name} in {java_file.name}")
        
        return systems
    
    def _analyze_config_file(self, content: str, config_file: Path) -> List[Dict]:
        """Analyze configuration files for external system references."""
        systems = []
        
        # Look for external URLs in configuration
        url_pattern = re.compile(r'["\']?https?://([^/"\']+)[^"\']*["\']?')
        urls = url_pattern.findall(content)
        
        for url in urls:
            if not any(local in url.lower() for local in ['localhost', '127.0.0.1', '0.0.0.0']):
                system_name = self._infer_system_name_from_url(url)
                if system_name:
                    systems.append({
                        'name': system_name,
                        'type': 'external_system',
                        'access_level': 'api_integration',
                        'integration_type': 'configuration',
                        'identified_from': [f"Configuration in {config_file.name}"]
                    })
                    if self.verbose:
                        log_info(f"  Found external system in config: {system_name} in {config_file.name}")
        
        # Look for database connection strings
        db_pattern = re.compile(r'jdbc:[^:]+://([^/:]+)', re.IGNORECASE)
        db_hosts = db_pattern.findall(content)
        
        for db_host in db_hosts:
            if not any(local in db_host.lower() for local in ['localhost', '127.0.0.1', '0.0.0.0']):
                system_name = f"External Database ({db_host})"
                systems.append({
                    'name': system_name,
                    'type': 'external_system',
                    'access_level': 'api_integration',
                    'integration_type': 'database',
                    'identified_from': [f"Database config in {config_file.name}"]
                })
                if self.verbose:
                    log_info(f"  Found external database in config: {system_name} in {config_file.name}")
        
        return systems
    
    def _infer_system_name_from_url(self, url: str) -> Optional[str]:
        """Infer system name from URL."""
        url_lower = url.lower()
        
        # Check against known service patterns
        for service, pattern in self.url_patterns.items():
            if pattern.search(url):
                return self._get_service_display_name(service)
        
        # Generic domain-based naming
        if '.' in url:
            domain_parts = url.split('.')
            
            # Handle common patterns like api.service.com -> Service API
            if len(domain_parts) >= 2:
                if domain_parts[0] == 'api':
                    service_name = domain_parts[1].title()
                    return f"{service_name} API"
                else:
                    # Use the main domain name
                    main_domain = domain_parts[-2] if len(domain_parts) > 1 else domain_parts[0]
                    return f"{main_domain.title()} Service"
        
        return None
    
    def _get_service_display_name(self, service: str) -> str:
        """Get display name for known services."""
        service_names = {
            'stripe': 'Stripe Payment Gateway',
            'paypal': 'PayPal Payment Gateway',
            'twilio': 'Twilio SMS Service',
            'sendgrid': 'SendGrid Email Service',
            'aws': 'AWS Services',
            'github': 'GitHub API',
            'slack': 'Slack Integration',
            'google': 'Google APIs'
        }
        
        return service_names.get(service, f"{service.title()} Service")


class UIPatternAnalyzer:
    """Analyzes UI patterns to identify role-based access and user types"""
    
    def __init__(self):
        # Vue.js role-based patterns
        self.vue_patterns = {
            'role_checks': [
                r'v-if=".*role.*"',
                r'v-show=".*role.*"',
                r'hasRole\(', r'checkRole\(',
                r'userRole|currentRole|user\.role',
                r'isAdmin|isUser|isModerator|isGuest',
                r'\$auth\.user\.|this\.\$auth\.user'
            ],
            'permission_checks': [
                r'v-if=".*permission.*"',
                r'v-show=".*permission.*"', 
                r'hasPermission\(', r'checkPermission\(',
                r'userPermissions|permissions\.',
                r'canAccess|canView|canEdit|canDelete',
                r'ability\.can\(|this\.ability\.can\('
            ],
            'auth_guards': [
                r'beforeRouteEnter|beforeRouteUpdate',
                r'requiresAuth|requiresRole|requiresPermission',
                r'authGuard|roleGuard|permissionGuard',
                r'meta:\s*{\s*requiresAuth',
                r'meta:\s*{\s*roles:'
            ]
        }
        
        # React role-based patterns
        self.react_patterns = {
            'role_checks': [
                r'user\.role|currentUser\.role|authUser\.role',
                r'hasRole\(|checkRole\(|userHasRole\(',
                r'isAdmin|isUser|isModerator|isGuest',
                r'roles\.includes\(|role\s*===|role\s*!==',
                r'useAuth\(\)|useUser\(\)|useRole\(\)'
            ],
            'permission_checks': [
                r'permissions\.includes\(|permission\s*===',
                r'hasPermission\(|checkPermission\(',
                r'canAccess|canView|canEdit|canDelete',
                r'ability\.can\(|useAbility\(\)',
                r'userPermissions|currentPermissions'
            ],
            'conditional_rendering': [
                r'&&\s*user\.role|&&\s*hasRole',
                r'&&\s*isAuthenticated|&&\s*user\.',
                r'role\s*===.*\?|permission\s*===.*\?',
                r'ProtectedRoute|PrivateRoute|RequireAuth',
                r'RoleBasedRoute|PermissionBasedRoute'
            ]
        }
        
        # Common UI role indicators
        self.common_ui_roles = {
            'admin': ['admin', 'administrator', 'super_user', 'superuser'],
            'user': ['user', 'member', 'customer', 'client'],
            'moderator': ['moderator', 'mod', 'editor', 'manager'],
            'guest': ['guest', 'visitor', 'anonymous', 'public'],
            'staff': ['staff', 'employee', 'worker', 'team'],
            'owner': ['owner', 'creator', 'author']
        }
    
    def analyze(self, file_path, content):
        """Analyze UI files for role-based patterns"""
        ui_actors = []
        
        # Determine file type
        if file_path.endswith('.vue'):
            patterns = self.vue_patterns
            framework = 'vue'
        elif file_path.endswith(('.jsx', '.tsx', '.js', '.ts')) and ('react' in content.lower() or 'jsx' in content.lower()):
            patterns = self.react_patterns  
            framework = 'react'
        else:
            return ui_actors
        
        # Extract roles from patterns
        found_roles = set()
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract potential role names from the match
                    context = content[max(0, match.start()-50):match.end()+50]
                    roles = self._extract_roles_from_context(context)
                    found_roles.update(roles)
                    
                    self._log_discovery(f"Found {framework} role pattern '{pattern}' in: {file_path}")
        
        # Convert found roles to actors
        for role in found_roles:
            actor_name = self._normalize_role_name(role)
            if actor_name:
                ui_actors.append({
                    'name': actor_name,
                    'type': 'ui_role',
                    'framework': framework,
                    'file': file_path
                })
        
        return ui_actors
    
    def _extract_roles_from_context(self, context):
        """Extract role names from the surrounding context"""
        roles = set()
        
        # Look for quoted role names
        quote_patterns = [
            r"['\"](\w+)['\"]",
            r"role\s*[=:]\s*['\"](\w+)['\"]",
            r"hasRole\s*\(\s*['\"](\w+)['\"]",
            r"includes\s*\(\s*['\"](\w+)['\"]"
        ]
        
        for pattern in quote_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                potential_role = match.group(1).lower()
                if self._is_valid_role(potential_role):
                    roles.add(potential_role)
        
        # Look for boolean role checks
        for role_type, variations in self.common_ui_roles.items():
            for variation in variations:
                if re.search(rf'\b{re.escape(variation)}\b', context, re.IGNORECASE):
                    roles.add(role_type)
        
        return roles
    
    def _is_valid_role(self, role):
        """Check if a string is likely a valid role name"""
        # Common role indicators
        role_keywords = [
            'admin', 'user', 'guest', 'moderator', 'staff', 'member',
            'customer', 'client', 'owner', 'manager', 'editor'
        ]
        
        return (len(role) > 2 and 
                any(keyword in role for keyword in role_keywords) and
                not role.isdigit())
    
    def _normalize_role_name(self, role):
        """Normalize role name to standard format"""
        # Map common role variations to standard names
        role_mappings = {
            'admin': 'Administrator',
            'administrator': 'Administrator', 
            'super_user': 'Administrator',
            'superuser': 'Administrator',
            'user': 'User',
            'member': 'User',
            'customer': 'Customer',
            'client': 'Customer',
            'moderator': 'Moderator',
            'mod': 'Moderator',
            'staff': 'Staff',
            'employee': 'Staff',
            'guest': 'Guest',
            'visitor': 'Guest',
            'anonymous': 'Guest',
            'public': 'Public',
            'owner': 'Owner',
            'manager': 'Manager',
            'editor': 'Editor'
        }
        
        return role_mappings.get(role.lower(), role.title())
    
    def _log_discovery(self, message):
        """Log pattern discovery"""
        print(f"[INFO]   {message}")


@dataclass
class Endpoint:
    """Represents an API endpoint."""
    method: str
    path: str
    controller: str
    authenticated: bool
    
    def __str__(self):
        auth = "🔒" if self.authenticated else "🌐"
        return f"{auth} {self.method} {self.path}"


@dataclass
class Model:
    """Represents a data model."""
    name: str
    fields: int
    file_path: Optional[Path] = None


@dataclass
class View:
    """Represents a UI view."""
    name: str
    file_name: str
    file_path: Optional[Path] = None


@dataclass
class Service:
    """Represents a backend service."""
    name: str
    file_path: Optional[Path] = None


@dataclass
class Actor:
    """Represents an actor in the system (user, external system, etc.)."""
    name: str
    type: str  # end_user, internal_user, external_system
    access_level: str  # public, authenticated, admin, api_integration
    identified_from: List[str] = field(default_factory=list)


@dataclass
class SystemBoundary:
    """Represents a system or subsystem boundary."""
    name: str
    components: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    type: str = "subsystem"  # primary_system, subsystem, external_system


@dataclass
class Relationship:
    """Represents a relationship between actors and systems or between systems."""
    from_entity: str
    to_entity: str
    relationship_type: str  # service_call, initiates_payment, sends_notifications, etc.
    mechanism: str  # REST API call, async_message, method_invocation, etc.
    identified_from: List[str] = field(default_factory=list)


class PackageStructureAnalyzer:
    """Analyzes package structure and project organization to identify system boundaries."""
    
    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose
        self.modules = []  # Multi-module Maven/Gradle modules
        self.package_tree = {}  # Package hierarchy
        
    def analyze_boundaries(self):
        """Analyze project structure and return system boundaries."""
        boundaries = []
        
        # Detect multi-module structure
        self._detect_modules()
        
        if self.modules:
            # Multi-module project - each module is a boundary
            boundaries.extend(self._create_module_boundaries())
        else:
            # Single module - analyze package structure
            boundaries.extend(self._analyze_package_hierarchy())
        
        # Detect microservice boundaries from configuration
        boundaries.extend(self._detect_microservice_boundaries())
        
        return boundaries
    
    def _detect_modules(self):
        """Detect Maven/Gradle multi-module structure."""
        # Look for pom.xml files with <modules> section
        pom_files = list(self.repo_root.rglob("**/pom.xml"))
        
        for pom_file in pom_files:
            try:
                content = pom_file.read_text()
                
                # Check if this is a parent POM with modules
                if '<modules>' in content:
                    module_pattern = r'<module>([^<]+)</module>'
                    module_names = re.findall(module_pattern, content)
                    
                    for module_name in module_names:
                        module_path = pom_file.parent / module_name
                        if module_path.exists():
                            self.modules.append({
                                'name': module_name,
                                'path': module_path,
                                'type': 'maven_module'
                            })
                            if self.verbose:
                                log_info(f"  Found Maven module: {module_name}", self.verbose)
            except Exception:
                continue
        
        # Look for Gradle multi-module structure (settings.gradle)
        gradle_settings = self.repo_root / "settings.gradle"
        if gradle_settings.exists():
            try:
                content = gradle_settings.read_text()
                include_pattern = r"include\s+['\"]([^'\"]+)['\"]"
                module_names = re.findall(include_pattern, content)
                
                for module_name in module_names:
                    module_name = module_name.lstrip(':').replace(':', '/')
                    module_path = self.repo_root / module_name
                    if module_path.exists():
                        self.modules.append({
                            'name': module_name,
                            'path': module_path,
                            'type': 'gradle_module'
                        })
                        if self.verbose:
                            log_info(f"  Found Gradle module: {module_name}", self.verbose)
            except Exception:
                pass
    
    def _create_module_boundaries(self):
        """Create system boundaries for each detected module."""
        boundaries = []
        
        for module in self.modules:
            # Analyze components in this module
            components = self._get_module_components(module['path'])
            
            # Determine boundary type based on module structure
            boundary_type = self._infer_boundary_type(module, components)
            
            boundaries.append(SystemBoundary(
                name=f"{module['name'].replace('-', ' ').title()} Module",
                components=components,
                interfaces=[],  # Will be populated by relationship mapping
                type=boundary_type
            ))
        
        return boundaries
    
    def _get_module_components(self, module_path: Path):
        """Get list of components (classes) in a module."""
        components = []
        java_files = list(module_path.rglob("**/*.java"))
        
        for java_file in java_files:
            # Skip test files
            if '/test/' in str(java_file) or '\\test\\' in str(java_file):
                continue
            components.append(java_file.stem)
        
        return components[:50]  # Limit to 50 for readability
    
    def _infer_boundary_type(self, module, components):
        """Infer the type of system boundary based on module characteristics."""
        module_name_lower = module['name'].lower()
        
        # Check for common patterns
        if any(keyword in module_name_lower for keyword in ['api', 'web', 'rest', 'controller']):
            return 'api_layer'
        elif any(keyword in module_name_lower for keyword in ['service', 'core', 'business']):
            return 'service_layer'
        elif any(keyword in module_name_lower for keyword in ['data', 'persistence', 'repository', 'dao']):
            return 'data_layer'
        elif any(keyword in module_name_lower for keyword in ['common', 'shared', 'util']):
            return 'shared_library'
        else:
            return 'subsystem'
    
    def _analyze_package_hierarchy(self):
        """Analyze package hierarchy to identify logical subsystems."""
        boundaries = []
        java_files = list(self.repo_root.rglob("**/*.java"))
        package_groups = {}
        
        for java_file in java_files:
            # Skip test files
            if '/test/' in str(java_file) or '\\test\\' in str(java_file):
                continue
                
            try:
                content = java_file.read_text()
                package_match = re.search(r'package\s+([^;]+);', content)
                if package_match:
                    package = package_match.group(1)
                    
                    # Analyze package structure for domain grouping
                    parts = package.split('.')
                    
                    # Try to identify domain packages (usually after base package)
                    if len(parts) >= 3:
                        # Common patterns: com.company.app.domain or com.company.domain
                        domain_candidates = []
                        
                        # Look for domain indicators
                        for i, part in enumerate(parts):
                            if part in ['controller', 'service', 'repository', 'model', 'dto', 'entity']:
                                # The part before this is likely the domain
                                if i > 0 and parts[i-1] not in ['com', 'org', 'net', 'io']:
                                    domain_candidates.append(parts[i-1])
                        
                        # If no clear domain, use the last meaningful package
                        if not domain_candidates:
                            for part in reversed(parts):
                                if part not in ['com', 'org', 'net', 'io', 'app', 'application', 'main']:
                                    domain_candidates.append(part)
                                    break
                        
                        # Group by domain
                        for domain in domain_candidates:
                            if domain not in package_groups:
                                package_groups[domain] = {
                                    'components': [],
                                    'package_prefix': package,
                                    'layers': set()
                                }
                            
                            package_groups[domain]['components'].append(java_file.stem)
                            
                            # Track architectural layers
                            if 'controller' in package:
                                package_groups[domain]['layers'].add('presentation')
                            elif 'service' in package:
                                package_groups[domain]['layers'].add('business')
                            elif 'repository' in package or 'dao' in package:
                                package_groups[domain]['layers'].add('data')
                            elif 'model' in package or 'entity' in package or 'dto' in package:
                                package_groups[domain]['layers'].add('model')
            except Exception:
                continue
        
        # Create boundaries for significant package groups
        for domain, info in package_groups.items():
            if len(info['components']) >= 2:  # Only meaningful groups
                # Determine boundary type based on layers present
                if len(info['layers']) >= 3:
                    boundary_type = 'domain_subsystem'  # Full vertical slice
                elif 'presentation' in info['layers']:
                    boundary_type = 'api_layer'
                elif 'business' in info['layers']:
                    boundary_type = 'service_layer'
                elif 'data' in info['layers']:
                    boundary_type = 'data_layer'
                else:
                    boundary_type = 'subsystem'
                
                boundaries.append(SystemBoundary(
                    name=f"{domain.replace('_', ' ').title()} Subsystem",
                    components=info['components'][:50],  # Limit for readability
                    interfaces=[],
                    type=boundary_type
                ))
        
        return boundaries
    
    def _detect_microservice_boundaries(self):
        """Detect microservice boundaries from configuration files."""
        boundaries = []
        
        # Look for spring.application.name in configuration files
        config_patterns = [
            "**/application*.properties",
            "**/application*.yml",
            "**/application*.yaml",
            "**/bootstrap*.properties",
            "**/bootstrap*.yml"
        ]
        
        service_names = set()
        
        for pattern in config_patterns:
            config_files = list(self.repo_root.rglob(pattern))
            
            for config_file in config_files:
                try:
                    content = config_file.read_text()
                    
                    # Properties format
                    app_name_match = re.search(r'spring\.application\.name\s*[=:]\s*([^\s\n]+)', content)
                    if app_name_match:
                        service_name = app_name_match.group(1).strip('"\'')
                        service_names.add(service_name)
                    
                    # YAML format
                    yaml_match = re.search(r'application:\s*\n\s*name:\s*([^\s\n]+)', content)
                    if yaml_match:
                        service_name = yaml_match.group(1).strip('"\'')
                        service_names.add(service_name)
                        
                except Exception:
                    continue
        
        # Create boundaries for detected services
        for service_name in service_names:
            boundaries.append(SystemBoundary(
                name=f"{service_name.replace('-', ' ').replace('_', ' ').title()} Service",
                components=[],  # Components will be populated from file location
                interfaces=[],
                type='microservice'
            ))
            if self.verbose:
                log_info(f"  Detected microservice: {service_name}", self.verbose)
        
        return boundaries


class CommunicationPatternDetector:
    """Detects communication patterns between system components."""
    
    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose
        
        # Communication pattern definitions
        self.rest_patterns = [
            r'RestTemplate|WebClient|@FeignClient',
            r'HttpClient|OkHttpClient',
            r'@RestController.*@RequestMapping',
            r'retrofit2?\.'
        ]
        
        self.messaging_patterns = [
            r'@RabbitListener|@KafkaListener|@JmsListener',
            r'RabbitTemplate|KafkaTemplate|JmsTemplate',
            r'@SendTo|@MessageMapping',
            r'MessageProducer|MessageConsumer'
        ]
        
        self.database_patterns = [
            r'@Repository|@Entity|@Table',
            r'JdbcTemplate|JpaRepository',
            r'EntityManager|SessionFactory',
            r'@Query\('
        ]
        
        self.event_patterns = [
            r'@EventListener|@EventHandler',
            r'ApplicationEventPublisher',
            r'@DomainEvent|@TransactionalEventListener',
            r'EventBus|EventPublisher'
        ]
    
    def detect_communication_patterns(self, java_files):
        """Detect all communication patterns in the codebase."""
        communications = []
        
        for java_file in java_files:
            try:
                content = java_file.read_text()
                
                # Detect REST communications
                rest_comms = self._detect_rest_communications(java_file, content)
                communications.extend(rest_comms)
                
                # Detect messaging
                messaging_comms = self._detect_messaging_communications(java_file, content)
                communications.extend(messaging_comms)
                
                # Detect database interactions
                db_comms = self._detect_database_communications(java_file, content)
                communications.extend(db_comms)
                
                # Detect event-driven patterns
                event_comms = self._detect_event_communications(java_file, content)
                communications.extend(event_comms)
                
            except Exception:
                continue
        
        return communications
    
    def _detect_rest_communications(self, java_file, content):
        """Detect REST API calls between services."""
        communications = []
        
        for pattern in self.rest_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Try to extract target URL
                url_pattern = r'["\']https?://([^/"\'\s]+)[^"\']*["\']'
                urls = re.findall(url_pattern, content)
                
                for url in urls:
                    if not any(local in url for local in ['localhost', '127.0.0.1', '0.0.0.0']):
                        communications.append({
                            'source': java_file.stem,
                            'target': url,
                            'type': 'rest_call',
                            'mechanism': 'HTTP/REST',
                            'file': java_file.name
                        })
                        if self.verbose:
                            log_info(f"  Found REST call: {java_file.stem} → {url}", self.verbose)
                
                # Also detect service-to-service calls via service names
                feign_match = re.search(r'@FeignClient\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
                if feign_match:
                    service_name = feign_match.group(1)
                    communications.append({
                        'source': java_file.stem,
                        'target': service_name,
                        'type': 'service_call',
                        'mechanism': 'Feign/REST',
                        'file': java_file.name
                    })
                    if self.verbose:
                        log_info(f"  Found Feign client: {java_file.stem} → {service_name}", self.verbose)
        
        return communications
    
    def _detect_messaging_communications(self, java_file, content):
        """Detect message queue communications."""
        communications = []
        
        for pattern in self.messaging_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Extract queue/topic names
                queue_pattern = r'[@(](?:queue|destination|topic)\s*=\s*["\']([^"\']+)["\']'
                queues = re.findall(queue_pattern, content, re.IGNORECASE)
                
                for queue in queues:
                    communications.append({
                        'source': java_file.stem,
                        'target': queue,
                        'type': 'message_queue',
                        'mechanism': 'Message Queue',
                        'file': java_file.name
                    })
                    if self.verbose:
                        log_info(f"  Found message queue: {java_file.stem} → {queue}", self.verbose)
        
        return communications
    
    def _detect_database_communications(self, java_file, content):
        """Detect database interactions."""
        communications = []
        
        for pattern in self.database_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Extract entity/table names
                table_match = re.search(r'@Table\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
                if table_match:
                    table_name = table_match.group(1)
                    communications.append({
                        'source': java_file.stem,
                        'target': f"Table: {table_name}",
                        'type': 'database_access',
                        'mechanism': 'JPA/JDBC',
                        'file': java_file.name
                    })
        
        return communications
    
    def _detect_event_communications(self, java_file, content):
        """Detect event-driven communications."""
        communications = []
        
        for pattern in self.event_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                # Extract event types
                event_pattern = r'@EventListener\([^)]*([A-Z]\w+Event)[^)]*\)'
                events = re.findall(event_pattern, content)
                
                for event in events:
                    communications.append({
                        'source': java_file.stem,
                        'target': event,
                        'type': 'event_driven',
                        'mechanism': 'Event Bus',
                        'file': java_file.name
                    })
                    if self.verbose:
                        log_info(f"  Found event listener: {java_file.stem} → {event}", self.verbose)
        
        return communications


class ActorSystemMapper:
    """Maps relationships between actors and system components based on security and access patterns."""
    
    def __init__(self, actors, endpoints, system_boundaries, verbose=False):
        self.actors = actors
        self.endpoints = endpoints
        self.system_boundaries = system_boundaries
        self.verbose = verbose
    
    def map_actor_relationships(self):
        """Create relationships between actors and systems."""
        relationships = []
        
        # Map actors to endpoints based on security requirements
        relationships.extend(self._map_actors_to_endpoints())
        
        # Map actors to system boundaries
        relationships.extend(self._map_actors_to_boundaries())
        
        # Map external actors to integration points
        relationships.extend(self._map_external_actors())
        
        return relationships
    
    def _map_actors_to_endpoints(self):
        """Map actors to specific endpoints based on security annotations."""
        relationships = []
        
        for actor in self.actors:
            if actor.type in ["end_user", "internal_user"]:
                # Find endpoints accessible by this actor
                accessible_endpoints = self._find_accessible_endpoints(actor)
                
                for endpoint in accessible_endpoints:
                    relationships.append({
                        'from_entity': actor.name,
                        'to_entity': endpoint.path,
                        'relationship_type': 'accesses',
                        'mechanism': f'HTTP {endpoint.method}',
                        'identified_from': [f"Security requirement in controller"]
                    })
                    
                    if self.verbose:
                        log_info(f"  Mapped: {actor.name} → {endpoint.method} {endpoint.path}", self.verbose)
        
        return relationships
    
    def _find_accessible_endpoints(self, actor):
        """Find endpoints that this actor can access based on security patterns."""
        accessible = []
        
        for endpoint in self.endpoints:
            # Check if endpoint requires authentication
            endpoint_str = str(endpoint)
            
            # Public endpoints accessible by Public actor
            if actor.name == "Public" and any(keyword in endpoint_str.lower() 
                                               for keyword in ['login', 'register', 'public', 'health']):
                accessible.append(endpoint)
            
            # Authenticated endpoints for User actors
            elif actor.name == "User" and actor.access_level in ["authenticated", "user"]:
                # Most endpoints are accessible to authenticated users
                if not any(keyword in endpoint_str.lower() for keyword in ['admin']):
                    accessible.append(endpoint)
            
            # Admin endpoints for Administrator
            elif actor.name == "Administrator" or "admin" in actor.name.lower():
                # Admins can access everything, especially admin endpoints
                accessible.append(endpoint)
        
        return accessible[:10]  # Limit for readability
    
    def _map_actors_to_boundaries(self):
        """Map actors to system boundaries."""
        relationships = []
        
        for actor in self.actors:
            if actor.type in ["end_user", "internal_user"]:
                # Find relevant system boundaries
                for boundary in self.system_boundaries:
                    # Users interact with API layers and microservices
                    if boundary.type in ['api_layer', 'microservice', 'primary_system']:
                        relationships.append({
                            'from_entity': actor.name,
                            'to_entity': boundary.name,
                            'relationship_type': 'interacts_with',
                            'mechanism': 'web_interface',
                            'identified_from': [f"Actor {actor.name} accesses {boundary.name}"]
                        })
                        
                        if self.verbose:
                            log_info(f"  Mapped: {actor.name} ↔ {boundary.name}", self.verbose)
        
        return relationships
    
    def _map_external_actors(self):
        """Map external system actors to their integration points."""
        relationships = []
        
        for actor in self.actors:
            if actor.type == "external_system":
                # External systems interact with specific boundaries
                for boundary in self.system_boundaries:
                    # External systems typically connect to API or service layers
                    if boundary.type in ['api_layer', 'service_layer']:
                        relationships.append({
                            'from_entity': actor.name,
                            'to_entity': boundary.name,
                            'relationship_type': 'integrates_with',
                            'mechanism': 'API/Service Integration',
                            'identified_from': [f"External system {actor.name} integration"]
                        })
        
        return relationships


class SystemSystemMapper:
    """Maps relationships between system components and services."""
    
    def __init__(self, system_boundaries, communications, verbose=False):
        self.system_boundaries = system_boundaries
        self.communications = communications
        self.verbose = verbose
    
    def map_system_relationships(self):
        """Create relationships between system components."""
        relationships = []
        
        # Map based on detected communications
        for comm in self.communications:
            # Create relationship from communication pattern
            relationships.append({
                'from_entity': comm['source'],
                'to_entity': comm['target'],
                'relationship_type': comm['type'],
                'mechanism': comm['mechanism'],
                'identified_from': [f"{comm['type']} in {comm['file']}"]
            })
        
        # Map boundary-to-boundary relationships
        relationships.extend(self._map_boundary_relationships())
        
        return relationships
    
    def _map_boundary_relationships(self):
        """Map relationships between system boundaries based on architectural patterns."""
        relationships = []
        
        # Standard architectural flow: API → Service → Data
        api_layers = [b for b in self.system_boundaries if b.type == 'api_layer']
        service_layers = [b for b in self.system_boundaries if b.type == 'service_layer']
        data_layers = [b for b in self.system_boundaries if b.type == 'data_layer']
        
        # API layer depends on service layer
        for api in api_layers:
            for service in service_layers:
                relationships.append({
                    'from_entity': api.name,
                    'to_entity': service.name,
                    'relationship_type': 'depends_on',
                    'mechanism': 'layered_architecture',
                    'identified_from': ['Architectural layer dependency']
                })
        
        # Service layer depends on data layer
        for service in service_layers:
            for data in data_layers:
                relationships.append({
                    'from_entity': service.name,
                    'to_entity': data.name,
                    'relationship_type': 'depends_on',
                    'mechanism': 'layered_architecture',
                    'identified_from': ['Architectural layer dependency']
                })
        
        if relationships and self.verbose:
            log_info(f"  Mapped {len(relationships)} boundary relationships", self.verbose)
        
        return relationships


@dataclass
class UseCase:
    """Represents a use case with complete scenario definition."""
    id: str
    name: str
    primary_actor: str
    secondary_actors: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    main_scenario: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    identified_from: List[str] = field(default_factory=list)


class BusinessProcessIdentifier:
    """Identifies business processes and workflows to enhance use case quality.
    
    Analyzes transaction boundaries, multi-step workflows, and business rules
    to provide better context for preconditions, postconditions, and extension scenarios.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the business process identifier.
        
        Args:
            verbose: Whether to show detailed progress
        """
        self.verbose = verbose
        
        # Transaction annotation patterns
        self.transaction_patterns = {
            'transactional': re.compile(r'@Transactional\s*(?:\(\s*([^)]+)\s*\))?', re.IGNORECASE),
            'propagation': re.compile(r'propagation\s*=\s*Propagation\.(\w+)', re.IGNORECASE),
            'isolation': re.compile(r'isolation\s*=\s*Isolation\.(\w+)', re.IGNORECASE),
            'readonly': re.compile(r'readOnly\s*=\s*(true|false)', re.IGNORECASE),
        }
        
        # Business validation patterns
        self.validation_patterns = {
            'not_null': re.compile(r'@NotNull', re.IGNORECASE),
            'not_empty': re.compile(r'@NotEmpty', re.IGNORECASE),
            'not_blank': re.compile(r'@NotBlank', re.IGNORECASE),
            'size': re.compile(r'@Size\s*\(\s*(?:min\s*=\s*(\d+))?\s*(?:,\s*)?(?:max\s*=\s*(\d+))?\s*\)', re.IGNORECASE),
            'min': re.compile(r'@Min\s*\(\s*(\d+)\s*\)', re.IGNORECASE),
            'max': re.compile(r'@Max\s*\(\s*(\d+)\s*\)', re.IGNORECASE),
            'pattern': re.compile(r'@Pattern\s*\(\s*regexp\s*=\s*"([^"]+)"', re.IGNORECASE),
            'email': re.compile(r'@Email', re.IGNORECASE),
            'valid': re.compile(r'@Valid', re.IGNORECASE),
        }
        
        # Business workflow patterns
        self.workflow_patterns = {
            'service_call': re.compile(r'(\w+Service|Repository)\.(\w+)\s*\(', re.IGNORECASE),
            'async': re.compile(r'@Async', re.IGNORECASE),
            'scheduled': re.compile(r'@Scheduled', re.IGNORECASE),
            'retry': re.compile(r'@Retryable', re.IGNORECASE),
        }
    
    def analyze_business_context(self, java_files: List[Path], endpoints: List) -> Dict:
        """Analyze business context from Java files.
        
        Args:
            java_files: List of Java files to analyze
            endpoints: List of discovered endpoints
            
        Returns:
            Dictionary containing transaction info, validation rules, and workflows
        """
        business_context = {
            'transactions': [],
            'validations': [],
            'workflows': [],
            'business_rules': []
        }
        
        for java_file in java_files:
            try:
                content = java_file.read_text(encoding='utf-8')
                
                # Analyze transactions
                transactions = self._extract_transactions(content, java_file)
                business_context['transactions'].extend(transactions)
                
                # Analyze validations
                validations = self._extract_validations(content, java_file)
                business_context['validations'].extend(validations)
                
                # Analyze workflows
                workflows = self._extract_workflows(content, java_file)
                business_context['workflows'].extend(workflows)
                
            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze business context in {java_file.name}: {e}")
                continue
        
        # Extract business rules from validations
        business_context['business_rules'] = self._derive_business_rules(
            business_context['validations']
        )
        
        if self.verbose:
            log_info(f"  Found {len(business_context['transactions'])} transaction boundaries")
            log_info(f"  Found {len(business_context['validations'])} validation rules")
            log_info(f"  Found {len(business_context['workflows'])} workflow patterns")
            log_info(f"  Derived {len(business_context['business_rules'])} business rules")
        
        return business_context
    
    def _extract_transactions(self, content: str, java_file: Path) -> List[Dict]:
        """Extract transaction boundary information from file content.
        
        Args:
            content: File content to analyze
            java_file: Path to the file being analyzed
            
        Returns:
            List of transaction information dictionaries
        """
        transactions = []
        
        # Find all @Transactional annotations
        for match in self.transaction_patterns['transactional'].finditer(content):
            transaction_info = {
                'file': java_file.name,
                'propagation': 'REQUIRED',  # Default
                'isolation': 'DEFAULT',
                'readonly': False,
                'attributes': []
            }
            
            # Extract transaction attributes if present
            attributes_text = match.group(1) if match.group(1) else ""
            
            # Check for propagation
            prop_match = self.transaction_patterns['propagation'].search(attributes_text)
            if prop_match:
                transaction_info['propagation'] = prop_match.group(1)
                transaction_info['attributes'].append(f"propagation={prop_match.group(1)}")
            
            # Check for isolation
            iso_match = self.transaction_patterns['isolation'].search(attributes_text)
            if iso_match:
                transaction_info['isolation'] = iso_match.group(1)
                transaction_info['attributes'].append(f"isolation={iso_match.group(1)}")
            
            # Check for readonly
            readonly_match = self.transaction_patterns['readonly'].search(attributes_text)
            if readonly_match:
                transaction_info['readonly'] = readonly_match.group(1).lower() == 'true'
                transaction_info['attributes'].append(f"readOnly={readonly_match.group(1)}")
            
            # Try to find the method name
            # Look ahead for method signature
            remaining_content = content[match.end():]
            method_match = re.search(r'(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(', remaining_content[:200])
            if method_match:
                transaction_info['method'] = method_match.group(1)
            
            transactions.append(transaction_info)
            
            if self.verbose:
                log_info(f"  Found transaction in {java_file.name}: {transaction_info.get('method', 'unknown')}")
        
        return transactions
    
    def _extract_validations(self, content: str, java_file: Path) -> List[Dict]:
        """Extract validation annotations and rules from file content.
        
        Args:
            content: File content to analyze
            java_file: Path to the file being analyzed
            
        Returns:
            List of validation rule dictionaries
        """
        validations = []
        
        # Find @NotNull annotations
        for match in self.validation_patterns['not_null'].finditer(content):
            validation = self._create_validation_rule(
                'not_null', 'Field must not be null', content, match, java_file
            )
            if validation:
                validations.append(validation)
        
        # Find @NotEmpty annotations
        for match in self.validation_patterns['not_empty'].finditer(content):
            validation = self._create_validation_rule(
                'not_empty', 'Field must not be empty', content, match, java_file
            )
            if validation:
                validations.append(validation)
        
        # Find @NotBlank annotations
        for match in self.validation_patterns['not_blank'].finditer(content):
            validation = self._create_validation_rule(
                'not_blank', 'Field must not be blank', content, match, java_file
            )
            if validation:
                validations.append(validation)
        
        # Find @Size annotations
        for match in self.validation_patterns['size'].finditer(content):
            min_val = match.group(1) if match.group(1) else None
            max_val = match.group(2) if match.group(2) else None
            
            constraints = []
            if min_val:
                constraints.append(f"minimum length {min_val}")
            if max_val:
                constraints.append(f"maximum length {max_val}")
            
            description = f"Field size must be {' and '.join(constraints)}"
            validation = self._create_validation_rule(
                'size', description, content, match, java_file
            )
            if validation:
                validation['min'] = min_val
                validation['max'] = max_val
                validations.append(validation)
        
        # Find @Min annotations
        for match in self.validation_patterns['min'].finditer(content):
            min_val = match.group(1)
            validation = self._create_validation_rule(
                'min', f"Value must be at least {min_val}", content, match, java_file
            )
            if validation:
                validation['min_value'] = min_val
                validations.append(validation)
        
        # Find @Max annotations
        for match in self.validation_patterns['max'].finditer(content):
            max_val = match.group(1)
            validation = self._create_validation_rule(
                'max', f"Value must be at most {max_val}", content, match, java_file
            )
            if validation:
                validation['max_value'] = max_val
                validations.append(validation)
        
        # Find @Email annotations
        for match in self.validation_patterns['email'].finditer(content):
            validation = self._create_validation_rule(
                'email', 'Field must be a valid email address', content, match, java_file
            )
            if validation:
                validations.append(validation)
        
        # Find @Pattern annotations
        for match in self.validation_patterns['pattern'].finditer(content):
            pattern = match.group(1)
            validation = self._create_validation_rule(
                'pattern', f"Field must match pattern: {pattern}", content, match, java_file
            )
            if validation:
                validation['pattern'] = pattern
                validations.append(validation)
        
        return validations
    
    def _create_validation_rule(self, rule_type: str, description: str, 
                                content: str, match, java_file: Path) -> Optional[Dict]:
        """Create a validation rule dictionary with field information.
        
        Args:
            rule_type: Type of validation rule
            description: Human-readable description
            content: File content
            match: Regex match object
            java_file: Path to the file
            
        Returns:
            Validation rule dictionary or None
        """
        # Try to find the field name after the annotation
        remaining_content = content[match.end():]
        field_match = re.search(r'(?:private|public|protected)?\s+\w+(?:<[^>]+>)?\s+(\w+)', 
                               remaining_content[:200])
        
        validation = {
            'type': rule_type,
            'description': description,
            'file': java_file.name,
        }
        
        if field_match:
            validation['field'] = field_match.group(1)
        
        return validation
    
    def _extract_workflows(self, content: str, java_file: Path) -> List[Dict]:
        """Extract multi-step workflow patterns from file content.
        
        Args:
            content: File content to analyze
            java_file: Path to the file being analyzed
            
        Returns:
            List of workflow pattern dictionaries
        """
        workflows = []
        
        # Find async operations
        for match in self.workflow_patterns['async'].finditer(content):
            # Look for method name
            remaining_content = content[match.end():]
            method_match = re.search(r'(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(', 
                                    remaining_content[:200])
            if method_match:
                workflows.append({
                    'type': 'async_operation',
                    'method': method_match.group(1),
                    'file': java_file.name,
                    'description': 'Asynchronous background operation'
                })
        
        # Find scheduled operations
        for match in self.workflow_patterns['scheduled'].finditer(content):
            remaining_content = content[match.end():]
            method_match = re.search(r'(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(', 
                                    remaining_content[:200])
            if method_match:
                workflows.append({
                    'type': 'scheduled_job',
                    'method': method_match.group(1),
                    'file': java_file.name,
                    'description': 'Scheduled background job'
                })
        
        # Find retry patterns
        for match in self.workflow_patterns['retry'].finditer(content):
            remaining_content = content[match.end():]
            method_match = re.search(r'(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(', 
                                    remaining_content[:200])
            if method_match:
                workflows.append({
                    'type': 'retryable_operation',
                    'method': method_match.group(1),
                    'file': java_file.name,
                    'description': 'Operation with automatic retry on failure'
                })
        
        # Detect service orchestration (multiple service calls in sequence)
        service_calls = list(self.workflow_patterns['service_call'].finditer(content))
        if len(service_calls) >= 3:  # At least 3 service calls suggests orchestration
            workflows.append({
                'type': 'service_orchestration',
                'service_count': len(service_calls),
                'file': java_file.name,
                'description': f'Multi-step workflow with {len(service_calls)} service calls'
            })
        
        return workflows
    
    def _derive_business_rules(self, validations: List[Dict]) -> List[Dict]:
        """Derive high-level business rules from validation annotations.
        
        Args:
            validations: List of validation rules
            
        Returns:
            List of derived business rules
        """
        business_rules = []
        
        # Group validations by file to identify business entities
        by_file = {}
        for validation in validations:
            file_name = validation['file']
            if file_name not in by_file:
                by_file[file_name] = []
            by_file[file_name].append(validation)
        
        # Derive rules from grouped validations
        for file_name, file_validations in by_file.items():
            # Extract entity name from file
            entity_match = re.search(r'(\w+)(?:DTO|Request|Command|Entity)\.java', file_name)
            entity = entity_match.group(1) if entity_match else 'Entity'
            
            # Check for required fields
            required_fields = [v for v in file_validations 
                             if v['type'] in ['not_null', 'not_empty', 'not_blank'] 
                             and 'field' in v]
            
            if len(required_fields) >= 2:
                field_names = ', '.join([v['field'] for v in required_fields[:3]])
                if len(required_fields) > 3:
                    field_names += f" and {len(required_fields) - 3} more"
                
                business_rules.append({
                    'entity': entity,
                    'rule_type': 'required_fields',
                    'description': f"{entity} must have valid {field_names}",
                    'source_file': file_name
                })
            
            # Check for size constraints
            size_constraints = [v for v in file_validations if v['type'] == 'size']
            if size_constraints:
                business_rules.append({
                    'entity': entity,
                    'rule_type': 'data_constraints',
                    'description': f"{entity} has {len(size_constraints)} size constraint(s)",
                    'source_file': file_name
                })
            
            # Check for email validation (business contact info)
            email_validations = [v for v in file_validations if v['type'] == 'email']
            if email_validations:
                business_rules.append({
                    'entity': entity,
                    'rule_type': 'contact_validation',
                    'description': f"{entity} requires valid email address",
                    'source_file': file_name
                })
        
        return business_rules
    
    def enhance_use_case_preconditions(self, use_case: Dict, 
                                       business_context: Dict) -> List[str]:
        """Enhance use case preconditions with business context.
        
        Args:
            use_case: Use case dictionary
            business_context: Business context from analyze_business_context
            
        Returns:
            Enhanced list of preconditions
        """
        preconditions = list(use_case.get('preconditions', []))
        
        # Add validation-based preconditions
        relevant_validations = [v for v in business_context['validations']
                               if self._is_relevant_to_use_case(v, use_case)]
        
        if relevant_validations:
            # Group by type
            required = [v for v in relevant_validations 
                       if v['type'] in ['not_null', 'not_empty', 'not_blank']]
            if required and len(required) > 0:
                preconditions.append(f"All required fields must be provided")
            
            size_constraints = [v for v in relevant_validations if v['type'] == 'size']
            if size_constraints:
                preconditions.append(f"Input data must meet size constraints")
            
            email = [v for v in relevant_validations if v['type'] == 'email']
            if email:
                preconditions.append(f"Email address must be valid")
        
        # Add transaction-based preconditions
        relevant_transactions = [t for t in business_context['transactions']
                                if self._is_relevant_to_use_case(t, use_case)]
        
        for transaction in relevant_transactions:
            if not transaction.get('readonly', False):
                if 'database connection must be available' not in [p.lower() for p in preconditions]:
                    preconditions.append("Database connection must be available")
                break
        
        return preconditions
    
    def enhance_use_case_postconditions(self, use_case: Dict, 
                                        business_context: Dict) -> List[str]:
        """Enhance use case postconditions with business context.
        
        Args:
            use_case: Use case dictionary
            business_context: Business context from analyze_business_context
            
        Returns:
            Enhanced list of postconditions
        """
        postconditions = list(use_case.get('postconditions', []))
        
        # Add transaction-based postconditions
        relevant_transactions = [t for t in business_context['transactions']
                                if self._is_relevant_to_use_case(t, use_case)]
        
        for transaction in relevant_transactions:
            if not transaction.get('readonly', False):
                if transaction.get('propagation') == 'REQUIRES_NEW':
                    postconditions.append("Changes are committed in separate transaction")
                else:
                    postconditions.append("Changes are persisted to database")
                break
        
        # Add workflow-based postconditions
        relevant_workflows = [w for w in business_context['workflows']
                             if self._is_relevant_to_use_case(w, use_case)]
        
        for workflow in relevant_workflows:
            if workflow['type'] == 'async_operation':
                postconditions.append("Background process is initiated")
            elif workflow['type'] == 'scheduled_job':
                postconditions.append("Scheduled task is registered")
        
        return postconditions
    
    def generate_extension_scenarios(self, use_case: Dict, 
                                     business_context: Dict) -> List[str]:
        """Generate extension scenarios based on business context.
        
        Args:
            use_case: Use case dictionary
            business_context: Business context from analyze_business_context
            
        Returns:
            List of extension scenarios
        """
        extensions = list(use_case.get('extensions', []))
        
        # Add validation failure scenarios
        relevant_validations = [v for v in business_context['validations']
                               if self._is_relevant_to_use_case(v, use_case)]
        
        if relevant_validations:
            # Group validation types
            validation_types = set(v['type'] for v in relevant_validations)
            
            if 'not_null' in validation_types or 'not_empty' in validation_types:
                extensions.append("1a. Required field missing: System shows validation error")
            
            if 'size' in validation_types:
                extensions.append("1b. Input size invalid: System shows size constraint error")
            
            if 'email' in validation_types:
                extensions.append("1c. Email format invalid: System shows email validation error")
            
            if 'pattern' in validation_types:
                extensions.append("1d. Format invalid: System shows pattern matching error")
        
        # Add transaction failure scenarios
        relevant_transactions = [t for t in business_context['transactions']
                                if self._is_relevant_to_use_case(t, use_case)]
        
        if relevant_transactions and any(not t.get('readonly', False) for t in relevant_transactions):
            extensions.append("2a. Database error: System rolls back transaction and shows error")
        
        # Add workflow-specific scenarios
        relevant_workflows = [w for w in business_context['workflows']
                             if self._is_relevant_to_use_case(w, use_case)]
        
        for workflow in relevant_workflows:
            if workflow['type'] == 'retryable_operation':
                extensions.append("3a. Operation fails: System automatically retries")
            elif workflow['type'] == 'async_operation':
                extensions.append("3b. Background process fails: System logs error and notifies admin")
        
        return extensions
    
    def _is_relevant_to_use_case(self, item: Dict, use_case: Dict) -> bool:
        """Check if a business context item is relevant to a use case.
        
        Args:
            item: Business context item (validation, transaction, etc.)
            use_case: Use case dictionary
            
        Returns:
            True if item is relevant to the use case
        """
        # Simple heuristic: check if file names or method names match
        use_case_name = use_case.get('name', '').lower()
        use_case_sources = [s.lower() for s in use_case.get('identified_from', [])]
        
        item_file = item.get('file', '').lower()
        item_method = item.get('method', '').lower()
        
        # Check if any use case source references match the item
        for source in use_case_sources:
            if item_file and item_file.replace('.java', '') in source:
                return True
            if item_method and item_method in source:
                return True
        
        # Check if use case name components match item details
        name_parts = re.findall(r'\w+', use_case_name)
        for part in name_parts:
            if len(part) > 3:  # Ignore short words
                if part in item_file or part in item_method:
                    return True
        
        return False


class ProjectAnalyzer:
    """Analyzes a project to discover its components."""
    
    def __init__(self, repo_root: Path, verbose: bool = False):
        """
        Initialize the analyzer.
        
        Args:
            repo_root: Path to the repository root
            verbose: Whether to show detailed progress
        """
        self.repo_root = repo_root
        self.verbose = verbose
        
        # Existing collections
        self.endpoints: List[Endpoint] = []
        self.models: List[Model] = []
        self.views: List[View] = []
        self.services: List[Service] = []
        self.features: List[str] = []
        
        # New use case analysis collections
        self.actors: List[Actor] = []
        self.system_boundaries: List[SystemBoundary] = []
        self.relationships: List[Relationship] = []
        self.use_cases: List[UseCase] = []
        
        # Business context for enhanced use case quality
        self.business_context: Dict = {
            'transactions': [],
            'validations': [],
            'workflows': [],
            'business_rules': []
        }
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file that should be excluded from analysis."""
        path_str = str(file_path)
        
        # Common test directory patterns
        test_dir_patterns = [
            '/test/', '/tests/', '/testing/',
            '\\test\\', '\\tests\\', '\\testing\\',
            '/src/test/', '/src/tests/',
            '\\src\\test\\', '\\src\\tests\\'
        ]
        
        # Common test file patterns
        test_file_patterns = [
            'Test.java', 'Tests.java',
            'Test.js', 'Test.ts', 'Test.jsx', 'Test.tsx',
            'test.js', 'test.ts', 'test.jsx', 'test.tsx',
            '.test.', '.spec.',
            'TestCase.java', 'IntegrationTest.java'
        ]
        
        # Check directory patterns
        if any(pattern in path_str for pattern in test_dir_patterns):
            return True
        
        # Check file name patterns
        file_name = file_path.name
        if any(pattern in file_name for pattern in test_file_patterns):
            return True
        
        return False
        
    @property
    def endpoint_count(self) -> int:
        return len(self.endpoints)
    
    @property
    def model_count(self) -> int:
        return len(self.models)
    
    @property
    def view_count(self) -> int:
        return len(self.views)
    
    @property
    def service_count(self) -> int:
        return len(self.services)
    
    @property
    def feature_count(self) -> int:
        return len(self.features)
    
    @property
    def actor_count(self) -> int:
        return len(self.actors)
    
    @property
    def system_boundary_count(self) -> int:
        return len(self.system_boundaries)
    
    @property
    def relationship_count(self) -> int:
        return len(self.relationships)
    
    @property
    def use_case_count(self) -> int:
        return len(self.use_cases)
    
    def analyze(self):
        """Run all analysis steps with progress feedback."""
        import sys
        
        print("\n🔍 Starting project analysis...\n", file=sys.stderr)
        
        # Stage 1: Endpoints
        print("📍 Stage 1/8: Discovering API endpoints...", file=sys.stderr, end=" ", flush=True)
        self.discover_endpoints()
        print(f"✓ Found {self.endpoint_count} endpoints", file=sys.stderr)
        
        # Stage 2: Models
        print("📦 Stage 2/8: Analyzing data models...", file=sys.stderr, end=" ", flush=True)
        self.discover_models()
        print(f"✓ Found {self.model_count} models", file=sys.stderr)
        
        # Stage 3: Views
        print("🎨 Stage 3/8: Discovering UI views...", file=sys.stderr, end=" ", flush=True)
        self.discover_views()
        print(f"✓ Found {self.view_count} views", file=sys.stderr)
        
        # Stage 4: Services
        print("⚙️  Stage 4/8: Detecting backend services...", file=sys.stderr, end=" ", flush=True)
        self.discover_services()
        print(f"✓ Found {self.service_count} services", file=sys.stderr)
        
        # Stage 5: Features
        print("✨ Stage 5/8: Extracting features...", file=sys.stderr, end=" ", flush=True)
        self.extract_features()
        print(f"✓ Identified {self.feature_count} features", file=sys.stderr)
        
        # Stage 6: Actors
        print("👥 Stage 6/8: Identifying actors...", file=sys.stderr, end=" ", flush=True)
        self.discover_actors()
        print(f"✓ Found {self.actor_count} actors", file=sys.stderr)
        
        # Stage 7: System Boundaries
        print("🏢 Stage 7/8: Mapping system boundaries...", file=sys.stderr, end=" ", flush=True)
        self.discover_system_boundaries()
        print(f"✓ Found {self.system_boundary_count} boundaries", file=sys.stderr)
        
        # Stage 8: Use Cases
        print("📋 Stage 8/8: Generating use cases...", file=sys.stderr, end=" ", flush=True)
        self.map_relationships()
        self.extract_use_cases()
        print(f"✓ Generated {self.use_case_count} use cases", file=sys.stderr)
        
        print("\n✅ Analysis complete!\n", file=sys.stderr)
    
    def discover_endpoints(self):
        """Discover API endpoints from Java controllers."""
        log_info("Discovering API endpoints...", self.verbose)
        
        # Find controller directories
        controller_dirs = []
        for pattern in ["controller", "controllers", "api"]:
            controller_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))
        
        # Also search for *Controller.java files
        if not controller_dirs:
            log_info("  No controller directories found, searching for *Controller.java files...", self.verbose)
            controller_files = list(self.repo_root.rglob("src/**/*Controller.java"))
            controller_dirs = list(set(f.parent for f in controller_files))
        
        if not controller_dirs:
            log_info("  No controllers found in project", self.verbose)
            return
        
        for controller_dir in controller_dirs:
            for java_file in controller_dir.glob("*Controller.java"):
                # Skip test files
                if self._is_test_file(java_file):
                    if self.verbose:
                        log_info(f"  Skipping test controller: {java_file.name}", self.verbose)
                    continue
                    
                self._analyze_controller_file(java_file)
        
        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
    
    def _analyze_controller_file(self, file_path: Path):
        """Analyze a single controller file for endpoints."""
        log_info(f"  Processing: {file_path.name}", self.verbose)
        
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return
        
        controller_name = file_path.stem.replace("Controller", "")
        
        # Extract base path from @RequestMapping
        base_path = ""
        base_match = re.search(r'@RequestMapping\("([^"]*)"\)', content)
        if base_match:
            base_path = base_match.group(1)
        
        # Find all endpoint methods
        mapping_pattern = r'@(Get|Post|Put|Delete|Patch)Mapping(?:\("([^"]*)"\))?'
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.search(mapping_pattern, line)
            if match:
                method = match.group(1).upper()
                path = match.group(2) or ""
                full_path = base_path + path
                
                # Check for authentication in nearby lines (10 lines before)
                authenticated = False
                start_line = max(0, i - 10)
                for check_line in lines[start_line:i]:
                    if "@PreAuthorize" in check_line:
                        authenticated = True
                        break
                
                endpoint = Endpoint(
                    method=method,
                    path=full_path,
                    controller=controller_name,
                    authenticated=authenticated
                )
                self.endpoints.append(endpoint)
                log_info(f"    → {endpoint}", self.verbose)
    
    def discover_models(self):
        """Discover data models."""
        log_info("Discovering data models...", self.verbose)
        
        # Find model directories
        model_dirs = []
        for pattern in ["model", "models", "entity", "entities", "domain"]:
            model_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))
        
        if not model_dirs:
            log_info("  No model directories found", self.verbose)
            return
        
        for model_dir in model_dirs:
            for java_file in model_dir.glob("*.java"):
                self._analyze_model_file(java_file)
        
        log_info(f"Found {self.model_count} models", self.verbose)
    
    def _analyze_model_file(self, file_path: Path):
        """Analyze a single model file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return
        
        model_name = file_path.stem
        
        # Count private fields
        field_count = len(re.findall(r'^\s*private\s+', content, re.MULTILINE))
        
        model = Model(name=model_name, fields=field_count, file_path=file_path)
        self.models.append(model)
    
    def discover_views(self):
        """Discover Vue.js views and components."""
        log_info("Discovering Vue.js views...", self.verbose)
        
        # Find view directories
        view_dirs = []
        for pattern in ["views", "pages", "screens", "components"]:
            view_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))
        
        if not view_dirs:
            log_info("  No view directories found", self.verbose)
            return
        
        for view_dir in view_dirs:
            # Find Vue files
            for vue_file in view_dir.glob("*.vue"):
                view_name = vue_file.stem.replace("View", "")
                view = View(name=view_name, file_name=vue_file.name, file_path=vue_file)
                self.views.append(view)
            
            # Find React/JSX files
            for ext in ["*.jsx", "*.tsx", "*.js"]:
                for js_file in view_dir.glob(ext):
                    view_name = js_file.stem
                    view = View(name=view_name, file_name=js_file.name, file_path=js_file)
                    self.views.append(view)
        
        log_info(f"Found {self.view_count} views", self.verbose)
    
    def discover_services(self):
        """Discover backend services."""
        log_info("Discovering services...", self.verbose)
        
        # Find service directories
        service_dirs = []
        for pattern in ["service", "services"]:
            service_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))
        
        # Also search for *Service.java files
        if not service_dirs:
            log_info("  No service directories found, searching for *Service.java files...", self.verbose)
            service_files = list(self.repo_root.rglob("src/**/*Service.java"))
            service_dirs = list(set(f.parent for f in service_files))
        
        if not service_dirs:
            log_info("  No services found in project", self.verbose)
            return
        
        for service_dir in service_dirs:
            for java_file in service_dir.glob("*Service.java"):
                # Skip test files
                if self._is_test_file(java_file):
                    if self.verbose:
                        log_info(f"  Skipping test file: {java_file.name}", self.verbose)
                    continue
                    
                service = Service(name=java_file.stem, file_path=java_file)
                self.services.append(service)
        
        log_info(f"Found {self.service_count} services", self.verbose)
    
    def extract_features(self):
        """Extract features from README.md."""
        log_info("Extracting features from README...", self.verbose)
        
        readme = self.repo_root / "README.md"
        if not readme.exists():
            log_info("README.md not found", self.verbose)
            return
        
        try:
            content = readme.read_text()
        except Exception as e:
            log_info(f"Error reading README: {e}", self.verbose)
            return
        
        # Extract lines between ## Features and next ##
        in_features = False
        for line in content.split('\n'):
            if re.match(r'^##\s+Features', line):
                in_features = True
                continue
            elif re.match(r'^##', line) and in_features:
                break
            elif in_features and re.match(r'^\s*[-*]\s+', line):
                feature = re.sub(r'^\s*[-*]\s+', '', line)
                self.features.append(feature)
        
        log_info(f"Found {self.feature_count} features", self.verbose)
    
    def get_project_info(self) -> Dict[str, str]:
        """Get project information from various sources."""
        info = {
            "name": self._detect_project_name(),
            "description": self._detect_project_description(),
            "type": self._detect_project_type(),
            "language": self._detect_language_version(),
            "dependencies": self._detect_dependencies(),
            "storage": self._detect_storage(),
            "testing": self._detect_testing(),
        }
        return info
    
    def _detect_project_name(self) -> str:
        """Detect the project name."""
        # Try pom.xml
        pom_files = list(self.repo_root.glob("pom.xml"))
        if pom_files:
            try:
                content = pom_files[0].read_text()
                # Try name tag first
                name_match = re.search(r'<name>([^<$]+)</name>', content)
                if name_match and not re.search(r'parentpom|framework', name_match.group(1), re.I):
                    return name_match.group(1)
                # Fall back to artifactId
                artifact_match = re.search(r'<artifactId>([^<]+)</artifactId>', content)
                if artifact_match:
                    return artifact_match.group(1)
            except Exception:
                pass
        
        # Try package.json
        pkg_files = list(self.repo_root.glob("package.json"))
        if pkg_files:
            try:
                import json
                data = json.loads(pkg_files[0].read_text())
                if "name" in data:
                    return data["name"]
            except Exception:
                pass
        
        # Fall back to directory name
        return self.repo_root.name
    
    def _detect_project_description(self) -> str:
        """Detect the project description."""
        # Try pom.xml
        pom_files = list(self.repo_root.glob("pom.xml"))
        if pom_files:
            try:
                content = pom_files[0].read_text()
                desc_match = re.search(r'<description>([^<]+)</description>', content)
                if desc_match:
                    return desc_match.group(1)
            except Exception:
                pass
        
        # Try package.json
        pkg_files = list(self.repo_root.glob("package.json"))
        if pkg_files:
            try:
                import json
                data = json.loads(pkg_files[0].read_text())
                if "description" in data:
                    return data["description"]
            except Exception:
                pass
        
        # Try README.md
        readme = self.repo_root / "README.md"
        if readme.exists():
            try:
                content = readme.read_text()
                # Get first substantial paragraph
                for line in content.split('\n'):
                    if line.strip() and not line.startswith('#') and not line.startswith('-'):
                        return line.strip()
            except Exception:
                pass
        
        return "Application for managing and processing data"
    
    def _detect_project_type(self) -> str:
        """Detect the project type (api, web, frontend, single)."""
        has_backend = (
            list(self.repo_root.rglob("pom.xml")) or
            list(self.repo_root.rglob("src/**/*Controller.java")) or
            (self.repo_root / "requirements.txt").exists()
        )
        
        has_frontend = (
            list(self.repo_root.rglob("*.vue")) or
            list(self.repo_root.rglob("*.jsx")) or
            list(self.repo_root.rglob("*.tsx"))
        )
        
        if has_backend and has_frontend:
            return "web"
        elif has_backend:
            return "api"
        elif has_frontend:
            return "frontend"
        else:
            return "single"
    
    def _detect_language_version(self) -> str:
        """Detect the language and version."""
        # Check for Java version in pom.xml
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                version_match = re.search(r'<java\.version>([^<]+)</java\.version>', content)
                if version_match:
                    return f"Java {version_match.group(1)}"
            except Exception:
                pass
        
        # Check for Node.js version in package.json
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json
                data = json.loads(pkg_file.read_text())
                if "engines" in data and "node" in data["engines"]:
                    return f"Node.js {data['engines']['node']}"
            except Exception:
                pass
        
        # Fallback based on file types
        if list(self.repo_root.rglob("*.java")):
            return "Java (version not specified)"
        elif list(self.repo_root.rglob("*.ts")) or list(self.repo_root.rglob("*.js")):
            return "JavaScript/TypeScript (version not specified)"
        elif list(self.repo_root.rglob("*.py")):
            return "Python (version not specified)"
        
        return "NEEDS CLARIFICATION"
    
    def _detect_dependencies(self) -> str:
        """Detect primary dependencies."""
        deps = []
        
        # Backend dependencies from pom.xml
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                if "spring-boot-starter-web" in content:
                    deps.append("Spring Boot")
                if "spring-boot-starter-security" in content:
                    deps.append("Spring Security")
                if "spring-boot-starter-data-mongodb" in content:
                    deps.append("Spring Data MongoDB")
                if "spring-boot-starter-data-jpa" in content:
                    deps.append("Spring Data JPA")
            except Exception:
                pass
        
        # Frontend dependencies from package.json
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json
                data = json.loads(pkg_file.read_text())
                deps_dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "vue" in deps_dict:
                    version = deps_dict["vue"].strip("^~")
                    deps.append(f"Vue.js {version}")
                if "react" in deps_dict:
                    version = deps_dict["react"].strip("^~")
                    deps.append(f"React {version}")
                if "@angular/core" in deps_dict:
                    deps.append("Angular")
                if "pinia" in deps_dict:
                    deps.append("Pinia")
                if "tailwindcss" in deps_dict:
                    deps.append("Tailwind CSS")
            except Exception:
                pass
        
        return ", ".join(sorted(set(deps))) if deps else "NEEDS CLARIFICATION"
    
    def _detect_storage(self) -> str:
        """Detect storage technology."""
        storage_types = []
        
        # Check pom.xml files
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                if "mongodb" in content:
                    storage_types.append("MongoDB")
                if "postgresql" in content:
                    storage_types.append("PostgreSQL")
                if "mysql" in content:
                    storage_types.append("MySQL")
                if "<artifactId>h2</artifactId>" in content:
                    storage_types.append("H2")
            except Exception:
                pass
        
        # Check package.json files
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json
                data = json.loads(pkg_file.read_text())
                deps_dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "mongodb" in deps_dict or "mongoose" in deps_dict:
                    storage_types.append("MongoDB")
                if "pg" in deps_dict or "postgres" in deps_dict:
                    storage_types.append("PostgreSQL")
                if "mysql" in deps_dict:
                    storage_types.append("MySQL")
                if "redis" in deps_dict:
                    storage_types.append("Redis")
            except Exception:
                pass
        
        return ", ".join(sorted(set(storage_types))) if storage_types else "N/A"
    
    def _detect_testing(self) -> str:
        """Detect testing frameworks."""
        testing_frameworks = []
        
        # Check pom.xml files for Java testing
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                if "junit-jupiter" in content:
                    testing_frameworks.append("JUnit 5")
                elif "<artifactId>junit</artifactId>" in content:
                    testing_frameworks.append("JUnit 4")
                if "mockito" in content:
                    testing_frameworks.append("Mockito")
                if "testng" in content:
                    testing_frameworks.append("TestNG")
            except Exception:
                pass
        
        # Check package.json files for JS testing
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json
                data = json.loads(pkg_file.read_text())
                deps_dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                if "vitest" in deps_dict:
                    testing_frameworks.append("Vitest")
                if "jest" in deps_dict:
                    testing_frameworks.append("Jest")
                if "mocha" in deps_dict:
                    testing_frameworks.append("Mocha")
                if "@vue/test-utils" in deps_dict:
                    testing_frameworks.append("Vue Test Utils")
                if "@testing-library/react" in deps_dict:
                    testing_frameworks.append("React Testing Library")
                if "cypress" in deps_dict:
                    testing_frameworks.append("Cypress")
                if "playwright" in deps_dict:
                    testing_frameworks.append("Playwright")
            except Exception:
                pass
        
        return ", ".join(sorted(set(testing_frameworks))) if testing_frameworks else "NEEDS CLARIFICATION"

    def discover_actors(self):
        """Discover actors from various sources in the codebase."""
        log_info("Discovering actors...", self.verbose)
        
        # Clear existing actors
        self.actors.clear()
        
        # Discover from security configurations
        self._discover_security_actors()
        
        # Discover from external API integrations
        self._discover_external_actors()
        
        # Discover from UI patterns
        self._discover_ui_actors()
        
        log_info(f"Found {self.actor_count} actors", self.verbose)

    def discover_system_boundaries(self):
        """Identify system and subsystem boundaries."""
        log_info("Discovering system boundaries...", self.verbose)
        
        # Clear existing boundaries
        self.system_boundaries.clear()
        
        # Analyze package structure for boundaries
        self._analyze_package_boundaries()
        
        # Analyze configuration-based boundaries
        self._analyze_configuration_boundaries()
        
        log_info(f"Found {self.system_boundary_count} system boundaries", self.verbose)

    def map_relationships(self):
        """Map relationships between actors and systems."""
        log_info("Mapping relationships...", self.verbose)
        
        # Clear existing relationships
        self.relationships.clear()
        
        # Map actor-to-system relationships
        self._map_actor_system_relationships()
        
        # Map system-to-system relationships
        self._map_system_system_relationships()
        
        log_info(f"Found {self.relationship_count} relationships", self.verbose)

    def extract_use_cases(self):
        """Extract use cases from discovered patterns."""
        log_info("Extracting use cases...", self.verbose)
        
        # Clear existing use cases
        self.use_cases.clear()
        
        # Analyze business context for enhanced use case quality
        log_info("Analyzing business context...", self.verbose)
        business_identifier = BusinessProcessIdentifier(verbose=self.verbose)
        
        # Get all Java files (excluding tests)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]
        
        # Analyze business context
        self.business_context = business_identifier.analyze_business_context(
            java_files, self.endpoints
        )
        
        # Extract use cases from controllers and services
        self._extract_controller_use_cases()
        
        # Extract use cases from UI workflows
        self._extract_ui_use_cases()
        
        # Enhance use cases with business context
        log_info("Enhancing use cases with business context...", self.verbose)
        for use_case in self.use_cases:
            # Convert UseCase to dict for enhancement
            use_case_dict = {
                'name': use_case.name,
                'preconditions': use_case.preconditions,
                'postconditions': use_case.postconditions,
                'extensions': use_case.extensions,
                'identified_from': use_case.identified_from
            }
            
            # Enhance with business context
            use_case.preconditions = business_identifier.enhance_use_case_preconditions(
                use_case_dict, self.business_context
            )
            use_case.postconditions = business_identifier.enhance_use_case_postconditions(
                use_case_dict, self.business_context
            )
            use_case.extensions = business_identifier.generate_extension_scenarios(
                use_case_dict, self.business_context
            )
        
        log_info(f"Found {self.use_case_count} use cases", self.verbose)

    # Private helper methods for use case analysis
    
    def _discover_security_actors(self):
        """Discover actors from Spring Security patterns using SecurityPatternAnalyzer."""
        # Initialize the security pattern analyzer
        security_analyzer = SecurityPatternAnalyzer(verbose=self.verbose)
        
        # Find Java files to analyze (exclude test files)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]
        
        if self.verbose:
            excluded_count = len(all_java_files) - len(java_files)
            if excluded_count > 0:
                log_info(f"  Excluded {excluded_count} test files from security actor detection", self.verbose)
        
        # Analyze security annotations
        annotation_actors = security_analyzer.analyze_security_annotations(java_files)
        
        # Find configuration files
        config_files = []
        config_files.extend(self.repo_root.rglob("**/SecurityConfig.java"))
        config_files.extend(self.repo_root.rglob("**/WebSecurityConfig.java"))
        config_files.extend(self.repo_root.rglob("**/application*.yml"))
        config_files.extend(self.repo_root.rglob("**/application*.yaml"))
        config_files.extend(self.repo_root.rglob("**/application*.properties"))
        
        # Analyze configuration files
        config_actors = security_analyzer.analyze_spring_security_config(config_files)
        
        # Combine all actors and convert to Actor dataclass instances
        all_actor_dicts = annotation_actors + config_actors
        
        # Convert dictionary representations to Actor instances and deduplicate
        actor_names_seen = set()
        
        for actor_dict in all_actor_dicts:
            actor_name = actor_dict['name']
            
            # Skip duplicates
            if actor_name in actor_names_seen:
                # Find existing actor and merge evidence
                existing_actor = next((a for a in self.actors if a.name == actor_name), None)
                if existing_actor:
                    # Merge identified_from lists
                    for evidence in actor_dict['identified_from']:
                        if evidence not in existing_actor.identified_from:
                            existing_actor.identified_from.append(evidence)
                continue
            
            actor_names_seen.add(actor_name)
            
            # Create new Actor instance
            self.actors.append(Actor(
                name=actor_name,
                type=actor_dict['type'],
                access_level=actor_dict['access_level'],
                identified_from=actor_dict['identified_from']
            ))

    def _discover_external_actors(self):
        """Discover external system actors using ExternalSystemDetector."""
        # Initialize the external system detector
        external_detector = ExternalSystemDetector(verbose=self.verbose)
        
        # Find files to analyze (exclude test files)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]
        
        if self.verbose:
            excluded_count = len(all_java_files) - len(java_files)
            if excluded_count > 0:
                log_info(f"  Excluded {excluded_count} test files from external system detection", self.verbose)
        
        # Find configuration files
        config_files = []
        config_files.extend(self.repo_root.rglob("**/application*.yml"))
        config_files.extend(self.repo_root.rglob("**/application*.yaml"))
        config_files.extend(self.repo_root.rglob("**/application*.properties"))
        config_files.extend(self.repo_root.rglob("**/pom.xml"))
        config_files.extend(self.repo_root.rglob("**/build.gradle"))
        
        # Detect external systems
        external_systems = external_detector.detect_external_systems(java_files, config_files)
        
        # Convert to Actor instances and add to actors list
        for system_dict in external_systems:
            # Check if actor already exists
            existing = next((a for a in self.actors if a.name == system_dict['name']), None)
            
            if not existing:
                self.actors.append(Actor(
                    name=system_dict['name'],
                    type=system_dict['type'],
                    access_level=system_dict['access_level'],
                    identified_from=system_dict['identified_from']
                ))
            else:
                # Merge evidence
                for evidence in system_dict['identified_from']:
                    if evidence not in existing.identified_from:
                        existing.identified_from.append(evidence)

    def _discover_ui_actors(self):
        """Discover actors from UI patterns using UIPatternAnalyzer."""
        analyzer = UIPatternAnalyzer()
        
        # Look for Vue.js files (exclude node_modules)
        vue_files = [f for f in self.repo_root.rglob("**/*.vue") if 'node_modules' not in str(f)]
        
        # Look for React files (JSX, TSX, JS, TS with React patterns, exclude node_modules)
        react_files = []
        for pattern in ["**/*.jsx", "**/*.tsx", "**/*.js", "**/*.ts"]:
            react_files.extend([f for f in self.repo_root.rglob(pattern) if 'node_modules' not in str(f)])
        
        ui_files = vue_files + react_files
        
        for ui_file in ui_files:
            try:
                content = ui_file.read_text()
                
                # Analyze UI patterns
                ui_actors = analyzer.analyze(str(ui_file), content)
                
                for ui_actor in ui_actors:
                    actor_name = ui_actor['name']
                    existing = next((a for a in self.actors if a.name == actor_name), None)
                    
                    if not existing:
                        self.actors.append(Actor(
                            name=actor_name,
                            type="end_user",
                            access_level=self._classify_access_level(actor_name),
                            identified_from=[f"UI {ui_actor['framework']} pattern in {ui_file.name}"]
                        ))
                        if self.verbose:
                            log_info(f"  Found UI role '{actor_name}' in: {ui_file.name}")
                    else:
                        source = f"UI {ui_actor['framework']} pattern in {ui_file.name}"
                        if source not in existing.identified_from:
                            existing.identified_from.append(source)
            
            except Exception:
                continue

    def _analyze_package_boundaries(self):
        """Analyze package structure to identify system boundaries using PackageStructureAnalyzer."""
        package_analyzer = PackageStructureAnalyzer(self.repo_root, self.verbose)
        boundaries = package_analyzer.analyze_boundaries()
        
        # Add detected boundaries to our collection
        self.system_boundaries.extend(boundaries)
        
        if self.verbose:
            log_info(f"  Detected {len(boundaries)} boundaries from package analysis", self.verbose)

    def _analyze_configuration_boundaries(self):
        """Analyze configuration files for system boundaries."""
        # Look for microservice boundaries via configuration
        config_files = list(self.repo_root.rglob("**/application*.properties")) + \
                      list(self.repo_root.rglob("**/application*.yml"))
        
        for config_file in config_files:
            try:
                content = config_file.read_text()
                # Look for spring.application.name which indicates service boundaries
                app_name_match = re.search(r'spring\.application\.name\s*=\s*([^\s]+)', content)
                if app_name_match:
                    service_name = app_name_match.group(1).strip('"\'')
                    self.system_boundaries.append(SystemBoundary(
                        name=f"{service_name.title()} Service",
                        components=[],  # Will be populated based on file location
                        interfaces=[],
                        type="primary_system"
                    ))
            except Exception:
                continue

    def _map_actor_system_relationships(self):
        """Map relationships between actors and systems using ActorSystemMapper."""
        # Initialize the actor-system mapper
        mapper = ActorSystemMapper(
            actors=self.actors,
            endpoints=self.endpoints,
            system_boundaries=self.system_boundaries,
            verbose=self.verbose
        )
        
        # Get relationship mappings
        actor_relationships = mapper.map_actor_relationships()
        
        # Convert to Relationship objects
        for rel_dict in actor_relationships:
            self.relationships.append(Relationship(
                from_entity=rel_dict['from_entity'],
                to_entity=rel_dict['to_entity'],
                relationship_type=rel_dict['relationship_type'],
                mechanism=rel_dict['mechanism'],
                identified_from=rel_dict['identified_from']
            ))
        
        if self.verbose and actor_relationships:
            log_info(f"  Mapped {len(actor_relationships)} actor-system relationships", self.verbose)

    def _map_system_system_relationships(self):
        """Map relationships between systems using CommunicationPatternDetector and SystemSystemMapper."""
        # Get all Java files (excluding tests)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]
        
        # Initialize communication detector
        comm_detector = CommunicationPatternDetector(self.repo_root, self.verbose)
        
        # Detect all communication patterns
        communications = comm_detector.detect_communication_patterns(java_files)
        
        # Initialize system-system mapper
        system_mapper = SystemSystemMapper(
            system_boundaries=self.system_boundaries,
            communications=communications,
            verbose=self.verbose
        )
        
        # Get all system relationships
        system_relationships = system_mapper.map_system_relationships()
        
        # Convert to Relationship objects
        for rel_dict in system_relationships:
            self.relationships.append(Relationship(
                from_entity=rel_dict['from_entity'],
                to_entity=rel_dict['to_entity'],
                relationship_type=rel_dict['relationship_type'],
                mechanism=rel_dict['mechanism'],
                identified_from=rel_dict['identified_from']
            ))
        
        # Also look for service injection patterns (internal dependencies)
        for java_file in java_files:
            try:
                content = java_file.read_text()
                # Look for service injection patterns that indicate dependencies
                service_pattern = r'(\w+Service)\s+\w+;'
                services = re.findall(service_pattern, content)
                
                if services:
                    from_service = java_file.stem
                    for service in services:
                        self.relationships.append(Relationship(
                            from_entity=from_service,
                            to_entity=service,
                            relationship_type="service_dependency",
                            mechanism="dependency_injection",
                            identified_from=[f"Service dependency in {java_file.name}"]
                        ))
            except Exception:
                continue
        
        if self.verbose:
            log_info(f"  Detected {len(communications)} communication patterns", self.verbose)
            log_info(f"  Mapped {len(system_relationships)} system relationships", self.verbose)

    def _extract_controller_use_cases(self):
        """Extract use cases from controller methods."""
        controller_files = list(self.repo_root.rglob("**/*Controller.java"))
        
        for controller_file in controller_files:
            try:
                content = controller_file.read_text()
                controller_name = controller_file.stem.replace('Controller', '')
                
                # Find REST mapping methods
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'@(?:Get|Post|Put|Delete|Patch)Mapping', line):
                        # Look for the next public method
                        for j in range(i + 1, min(i + 15, len(lines))):
                            # Skip annotation lines
                            if re.match(r'\s*@\w+', lines[j]) or not lines[j].strip():
                                continue
                            method_match = re.search(r'public\s+\S+\s+(\w+)\s*\(', lines[j])
                            if method_match:
                                method_name = method_match.group(1)
                                use_case = self._create_use_case_from_method(
                                    method_name, controller_name, controller_file
                                )
                                if use_case:
                                    self.use_cases.append(use_case)
                                break
            except Exception:
                continue

    def _extract_ui_use_cases(self):
        """Extract use cases from UI workflows."""
        # This is a placeholder for UI-based use case extraction
        # In a full implementation, this would analyze Vue/React components
        # for user interaction patterns and workflows
        pass

    def _create_use_case_from_method(self, method_name: str, controller_name: str, source_file: Path) -> Optional[UseCase]:
        """Create a use case from a controller method."""
        use_case_name = self._method_to_use_case_name(method_name, controller_name)
        primary_actor = self._infer_primary_actor_for_method(method_name)
        
        # Generate scenario steps
        main_scenario = self._generate_main_scenario(method_name, controller_name)
        preconditions = self._generate_preconditions(method_name)
        postconditions = self._generate_postconditions(method_name)
        
        return UseCase(
            id=f"UC-{len(self.use_cases) + 1:03d}",
            name=use_case_name,
            primary_actor=primary_actor,
            secondary_actors=[],
            preconditions=preconditions,
            postconditions=postconditions,
            main_scenario=main_scenario,
            extensions=[],
            identified_from=[f"Controller method: {source_file.name}.{method_name}()"]
        )

    # Helper methods for actor and use case processing
    
    def _normalize_role_name(self, role: str) -> str:
        """Normalize role name to standard format."""
        role = re.sub(r'^ROLE_', '', role)
        return role.replace('_', ' ').title()

    def _classify_actor_type(self, role: str) -> str:
        """Classify actor type based on role name."""
        role_lower = role.lower()
        
        if any(keyword in role_lower for keyword in ['admin', 'administrator', 'manager']):
            return "internal_user"
        elif any(keyword in role_lower for keyword in ['system', 'service', 'api']):
            return "external_system"
        else:
            return "end_user"

    def _classify_access_level(self, role: str) -> str:
        """Classify access level based on role name."""
        role_lower = role.lower()
        
        if any(keyword in role_lower for keyword in ['admin', 'super']):
            return "admin"
        elif any(keyword in role_lower for keyword in ['guest', 'anonymous', 'public']):
            return "public"
        else:
            return "authenticated"

    def _infer_system_name(self, url: str) -> str:
        """Infer system name from URL."""
        url_lower = url.lower()
        
        if 'stripe' in url_lower:
            return "Payment Gateway (Stripe)"
        elif 'paypal' in url_lower:
            return "Payment Gateway (PayPal)"
        elif 'twilio' in url_lower:
            return "SMS Service (Twilio)"
        elif 'sendgrid' in url_lower:
            return "Email Service (SendGrid)"
        elif 'amazonaws' in url_lower:
            return "AWS Services"
        else:
            domain = url.split('.')[0] if '.' in url else url
            return f"External API ({domain.title()})"

    def _method_to_use_case_name(self, method_name: str, controller_name: str) -> str:
        """Convert method name to use case name."""
        method_words = re.sub(r'([A-Z])', r' \1', method_name).strip()
        
        method_mappings = {
            'create': 'Create',
            'register': 'Register',
            'login': 'Login',
            'logout': 'Logout',
            'update': 'Update',
            'delete': 'Delete',
            'get': 'View',
            'list': 'List',
            'search': 'Search'
        }
        
        for old, new in method_mappings.items():
            if method_words.lower().startswith(old):
                method_words = method_words.replace(old, new, 1)
                break
        
        return f"{method_words.title()} {controller_name}"

    def _infer_primary_actor_for_method(self, method_name: str) -> str:
        """Infer the primary actor for a method."""
        # Check if we have specific actors identified
        if self.actors:
            # Use the first non-external actor as default
            user_actors = [a for a in self.actors if a.type in ["end_user", "internal_user"]]
            if user_actors:
                return user_actors[0].name
        
        return "User"  # Default fallback

    def _generate_main_scenario(self, method_name: str, controller_name: str) -> List[str]:
        """Generate main scenario steps for a use case."""
        entity = controller_name.lower()
        
        if method_name.lower().startswith('create'):
            return [
                f"User navigates to {entity} creation page",
                f"User enters {entity} details",
                f"System validates input data",
                f"System creates new {entity}",
                f"System confirms successful creation"
            ]
        elif method_name.lower().startswith(('get', 'view')):
            return [
                f"User requests to view {entity}",
                f"System retrieves {entity} data",
                f"System displays {entity} information"
            ]
        elif method_name.lower().startswith('update'):
            return [
                f"User selects {entity} to update",
                f"User modifies {entity} details",
                f"System validates changes",
                f"System updates {entity} data",
                f"System confirms successful update"
            ]
        elif method_name.lower().startswith('delete'):
            return [
                f"User selects {entity} to delete",
                f"System requests confirmation",
                f"User confirms deletion",
                f"System removes {entity}",
                f"System confirms successful deletion"
            ]
        else:
            return [
                f"User initiates {entity} operation",
                f"System processes request",
                f"System returns result"
            ]

    def _generate_preconditions(self, method_name: str) -> List[str]:
        """Generate preconditions for a use case."""
        if method_name.lower().startswith(('update', 'delete', 'get')):
            return ["Entity must exist in the system", "User must have appropriate permissions"]
        else:
            return ["User must have appropriate permissions"]

    def _generate_postconditions(self, method_name: str) -> List[str]:
        """Generate postconditions for a use case."""
        if method_name.lower().startswith('create'):
            return ["New entity is created in the system", "User receives confirmation"]
        elif method_name.lower().startswith('update'):
            return ["Entity data is updated in the system", "User receives confirmation"]
        elif method_name.lower().startswith('delete'):
            return ["Entity is removed from the system", "User receives confirmation"]
        else:
            return ["Operation completes successfully", "User receives appropriate response"]

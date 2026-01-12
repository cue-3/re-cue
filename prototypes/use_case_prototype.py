#!/usr/bin/env python3
"""
Prototype Use Case Analyzer for RE-cue
Demonstrates the concept of use case creation from existing codebases.

This is a simplified prototype to validate the approach before full implementation.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Actor:
    name: str
    type: str  # end_user, internal_user, external_system
    access_level: str  # public, authenticated, admin, api_integration
    identified_from: List[str] = field(default_factory=list)


@dataclass
class UseCase:
    id: str
    name: str
    primary_actor: str
    secondary_actors: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    main_scenario: List[str] = field(default_factory=list)
    identified_from: List[str] = field(default_factory=list)


class UseCasePrototypeAnalyzer:
    """Prototype analyzer for use case creation."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.actors: List[Actor] = []
        self.use_cases: List[UseCase] = []
    
    def analyze(self) -> Dict:
        """Run prototype analysis and return results."""
        print("🔍 Running Use Case Prototype Analysis...")
        
        # Step 1: Discover actors
        print("👥 Discovering actors...")
        self._discover_actors()
        
        # Step 2: Extract use cases
        print("📋 Extracting use cases...")
        self._extract_use_cases()
        
        # Step 3: Generate results
        results = {
            "analysis_date": datetime.now().isoformat(),
            "repository": str(self.repo_root),
            "actors": [self._actor_to_dict(actor) for actor in self.actors],
            "use_cases": [self._use_case_to_dict(uc) for uc in self.use_cases],
            "summary": {
                "total_actors": len(self.actors),
                "total_use_cases": len(self.use_cases),
                "actor_types": self._count_actor_types(),
            }
        }
        
        print(f"✅ Analysis complete: {len(self.actors)} actors, {len(self.use_cases)} use cases")
        return results
    
    def _discover_actors(self):
        """Discover actors from various sources."""
        # From Spring Security annotations
        self._discover_security_actors()
        
        # From external API integrations
        self._discover_external_actors()
        
        # From UI patterns (basic)
        self._discover_ui_actors()
    
    def _discover_security_actors(self):
        """Discover actors from Spring Security patterns."""
        java_files = list(self.repo_root.rglob("**/*.java"))
        print(f"  Found {len(java_files)} Java files to analyze")
        
        for java_file in java_files:
            try:
                content = java_file.read_text()
                
                # Look for @PreAuthorize annotations
                preauth_pattern = r'@PreAuthorize\("hasRole\(\'([^\']+)\'\)"\)'
                matches = re.findall(preauth_pattern, content)
                
                # Also look for hasAuthority pattern
                auth_pattern = r'@PreAuthorize\("hasAuthority\(\'([^\']+)\'\)"\)'
                auth_matches = re.findall(auth_pattern, content)
                
                all_matches = matches + auth_matches
                if all_matches:
                    print(f"  Found security annotations in {java_file.name}: {all_matches}")
                
                for role in all_matches:
                    actor_name = self._normalize_role_name(role)
                    actor_type = self._classify_actor_type(role)
                    access_level = self._classify_access_level(role)
                    
                    # Check if actor already exists
                    existing = next((a for a in self.actors if a.name == actor_name), None)
                    if not existing:
                        self.actors.append(Actor(
                            name=actor_name,
                            type=actor_type,
                            access_level=access_level,
                            identified_from=[f"Security annotation in {java_file.name}"]
                        ))
                    else:
                        existing.identified_from.append(f"Security annotation in {java_file.name}")
                
                # Look for role enums
                enum_pattern = r'enum\s+\w*Role\w*\s*\{([^}]+)\}'
                enum_matches = re.findall(enum_pattern, content)
                
                for enum_content in enum_matches:
                    roles = [role.strip().rstrip(',') for role in enum_content.split('\n') if role.strip()]
                    for role in roles:
                        if role and not role.startswith('//'):
                            actor_name = self._normalize_role_name(role)
                            actor_type = self._classify_actor_type(role)
                            access_level = self._classify_access_level(role)
                            
                            existing = next((a for a in self.actors if a.name == actor_name), None)
                            if not existing:
                                self.actors.append(Actor(
                                    name=actor_name,
                                    type=actor_type,
                                    access_level=access_level,
                                    identified_from=[f"Role enum in {java_file.name}"]
                                ))
            
            except Exception:
                continue  # Skip files we can't read
    
    def _discover_external_actors(self):
        """Discover external system actors."""
        java_files = list(self.repo_root.rglob("**/*.java"))
        
        for java_file in java_files:
            try:
                content = java_file.read_text()
                
                # Look for REST client patterns
                if re.search(r'@RestTemplate|WebClient|RestClient', content):
                    # Extract URLs to infer external systems
                    url_pattern = r'["\']https?://([^/"\']+)'
                    urls = re.findall(url_pattern, content)
                    
                    for url in urls:
                        system_name = self._infer_system_name(url)
                        existing = next((a for a in self.actors if a.name == system_name), None)
                        if not existing:
                            self.actors.append(Actor(
                                name=system_name,
                                type="external_system",
                                access_level="api_integration",
                                identified_from=[f"REST client in {java_file.name}"]
                            ))
            
            except Exception:
                continue
    
    def _discover_ui_actors(self):
        """Discover actors from UI patterns (basic implementation)."""
        # Look for Vue.js files with role-based patterns
        vue_files = list(self.repo_root.rglob("**/*.vue"))
        
        for vue_file in vue_files:
            try:
                content = vue_file.read_text()
                
                # Look for v-if role checks
                role_pattern = r'v-if=".*(?:role|user).*===.*["\']([^"\']+)["\']'
                matches = re.findall(role_pattern, content)
                
                for role in matches:
                    actor_name = self._normalize_role_name(role)
                    existing = next((a for a in self.actors if a.name == actor_name), None)
                    if not existing:
                        self.actors.append(Actor(
                            name=actor_name,
                            type="end_user",
                            access_level="authenticated",
                            identified_from=[f"UI role check in {vue_file.name}"]
                        ))
            
            except Exception:
                continue
    
    def _extract_use_cases(self):
        """Extract use cases from controller methods."""
        controller_files = list(self.repo_root.rglob("**/*Controller.java"))
        print(f"  Found {len(controller_files)} controller files to analyze")
        
        for controller_file in controller_files:
            try:
                content = controller_file.read_text()
                
                # Extract controller name
                controller_name = controller_file.stem.replace('Controller', '')
                
                # Look for REST mapping annotations
                mapping_methods = []
                
                # Find @PostMapping, @GetMapping, etc. followed by method definitions
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'@(?:Get|Post|Put|Delete|Patch)Mapping', line):
                        # Look for the next public method within the next few lines (skip annotations)
                        for j in range(i + 1, min(i + 15, len(lines))):
                            # Skip annotation lines and empty lines
                            if re.match(r'\s*@\w+', lines[j]) or not lines[j].strip():
                                continue
                            method_match = re.search(r'public\s+\S+\s+(\w+)\s*\(', lines[j])
                            if method_match:
                                method_name = method_match.group(1)
                                mapping_methods.append(method_name)
                                break
                
                if mapping_methods:
                    print(f"  Found methods in {controller_file.name}: {mapping_methods[:5]}")  # Show first 5
                
                for method in mapping_methods:
                    use_case = self._create_use_case_from_method(
                        method, 
                        controller_name, 
                        controller_file
                    )
                    if use_case:
                        self.use_cases.append(use_case)
            
            except Exception as e:
                print(f"  Error processing {controller_file.name}: {e}")
                continue
    
    def _create_use_case_from_method(self, method_name: str, controller_name: str, source_file: Path) -> Optional[UseCase]:
        """Create a use case from a controller method."""
        # Generate use case name
        use_case_name = self._method_to_use_case_name(method_name, controller_name)
        
        # Infer primary actor (simplified)
        primary_actor = "User"  # Default, could be enhanced with security analysis
        
        # Generate basic scenario steps
        main_scenario = self._generate_basic_scenario(method_name, controller_name)
        
        # Generate basic preconditions and postconditions
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
            identified_from=[f"Controller method: {source_file.name}.{method_name}()"]
        )
    
    def _normalize_role_name(self, role: str) -> str:
        """Normalize role name to standard format."""
        # Remove common prefixes
        role = re.sub(r'^ROLE_', '', role)
        
        # Convert to title case
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
        # Simple heuristics for common services
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
            # Extract domain and capitalize
            domain = url.split('.')[0] if '.' in url else url
            return f"External API ({domain.title()})"
    
    def _method_to_use_case_name(self, method_name: str, controller_name: str) -> str:
        """Convert method name to use case name."""
        # Convert camelCase to words
        method_words = re.sub(r'([A-Z])', r' \1', method_name).strip()
        
        # Common method mappings
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
        
        # Apply mappings
        for old, new in method_mappings.items():
            if method_words.lower().startswith(old):
                method_words = method_words.replace(old, new, 1)
                break
        
        return f"{method_words.title()} {controller_name}"
    
    def _generate_basic_scenario(self, method_name: str, controller_name: str) -> List[str]:
        """Generate basic scenario steps."""
        entity = controller_name.lower()
        
        if method_name.lower().startswith('create'):
            return [
                f"User navigates to {entity} creation page",
                f"User enters {entity} details",
                "System validates input data",
                f"System creates new {entity}",
                "System confirms successful creation"
            ]
        elif method_name.lower().startswith('get') or method_name.lower().startswith('view'):
            return [
                f"User requests to view {entity}",
                f"System retrieves {entity} data",
                f"System displays {entity} information"
            ]
        elif method_name.lower().startswith('update'):
            return [
                f"User selects {entity} to update",
                f"User modifies {entity} details",
                "System validates changes",
                f"System updates {entity} data",
                "System confirms successful update"
            ]
        elif method_name.lower().startswith('delete'):
            return [
                f"User selects {entity} to delete",
                "System requests confirmation",
                "User confirms deletion",
                f"System removes {entity}",
                "System confirms successful deletion"
            ]
        else:
            return [
                f"User initiates {entity} operation",
                "System processes request",
                "System returns result"
            ]
    
    def _generate_preconditions(self, method_name: str) -> List[str]:
        """Generate basic preconditions."""
        if method_name.lower().startswith(('update', 'delete', 'get')):
            return ["Entity must exist in the system", "User must have appropriate permissions"]
        else:
            return ["User must have appropriate permissions"]
    
    def _generate_postconditions(self, method_name: str) -> List[str]:
        """Generate basic postconditions."""
        if method_name.lower().startswith('create'):
            return ["New entity is created in the system", "User receives confirmation"]
        elif method_name.lower().startswith('update'):
            return ["Entity data is updated in the system", "User receives confirmation"]
        elif method_name.lower().startswith('delete'):
            return ["Entity is removed from the system", "User receives confirmation"]
        else:
            return ["Operation completes successfully", "User receives appropriate response"]
    
    def _count_actor_types(self) -> Dict[str, int]:
        """Count actors by type."""
        counts = {"end_user": 0, "internal_user": 0, "external_system": 0}
        for actor in self.actors:
            if actor.type in counts:
                counts[actor.type] += 1
        return counts
    
    def _actor_to_dict(self, actor: Actor) -> Dict:
        """Convert actor to dictionary."""
        return {
            "name": actor.name,
            "type": actor.type,
            "access_level": actor.access_level,
            "identified_from": actor.identified_from
        }
    
    def _use_case_to_dict(self, use_case: UseCase) -> Dict:
        """Convert use case to dictionary."""
        return {
            "id": use_case.id,
            "name": use_case.name,
            "primary_actor": use_case.primary_actor,
            "secondary_actors": use_case.secondary_actors,
            "preconditions": use_case.preconditions,
            "postconditions": use_case.postconditions,
            "main_scenario": use_case.main_scenario,
            "identified_from": use_case.identified_from
        }
    
    def generate_markdown_report(self) -> str:
        """Generate a markdown report of the use case analysis."""
        date = datetime.now().strftime("%Y-%m-%d")
        
        output = [
            "# Use Case Analysis Report (Prototype)",
            "",
            f"**Generated**: {date}",
            f"**Repository**: {self.repo_root.name}",
            f"**Actors Found**: {len(self.actors)}",
            f"**Use Cases Found**: {len(self.use_cases)}",
            "",
            "---",
            "",
            "## Actors",
            "",
        ]
        
        # Group actors by type
        actor_groups = {}
        for actor in self.actors:
            if actor.type not in actor_groups:
                actor_groups[actor.type] = []
            actor_groups[actor.type].append(actor)
        
        for actor_type, actors in actor_groups.items():
            output.append(f"### {actor_type.replace('_', ' ').title()} Actors")
            output.append("")
            for actor in actors:
                output.append(f"- **{actor.name}** ({actor.access_level})")
                for source in actor.identified_from[:2]:  # Limit to 2 sources
                    output.append(f"  - Identified from: {source}")
            output.append("")
        
        output.extend([
            "---",
            "",
            "## Use Cases",
            "",
        ])
        
        for use_case in self.use_cases:
            output.extend([
                f"### {use_case.id}: {use_case.name}",
                "",
                f"**Primary Actor**: {use_case.primary_actor}",
                "",
                "**Preconditions**:",
            ])
            
            for condition in use_case.preconditions:
                output.append(f"- {condition}")
            
            output.extend([
                "",
                "**Main Success Scenario**:",
            ])
            
            for i, step in enumerate(use_case.main_scenario, 1):
                output.append(f"{i}. {step}")
            
            output.extend([
                "",
                "**Postconditions**:",
            ])
            
            for condition in use_case.postconditions:
                output.append(f"- {condition}")
            
            output.extend([
                "",
                "**Identified From**:",
            ])
            
            for source in use_case.identified_from:
                output.append(f"- {source}")
            
            output.extend(["", "---", ""])
        
        output.extend([
            "",
            "## Summary",
            "",
            f"This prototype analysis identified {len(self.actors)} actors and {len(self.use_cases)} use cases",
            "from the existing codebase. This demonstrates the feasibility of automated use case",
            "generation for reverse engineering legacy applications.",
            "",
            "**Note**: This is a prototype implementation. The full implementation will include",
            "more sophisticated pattern recognition, system boundary analysis, and relationship mapping.",
        ])
        
        return "\n".join(output)


def main():
    """Main function for prototype testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python use_case_prototype.py <repository_path>")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    # Run analysis
    analyzer = UseCasePrototypeAnalyzer(repo_path)
    results = analyzer.analyze()
    
    # Generate outputs
    print("\n" + "="*80)
    print("JSON RESULTS:")
    print("="*80)
    print(json.dumps(results, indent=2))
    
    print("\n" + "="*80)
    print("MARKDOWN REPORT:")
    print("="*80)
    print(analyzer.generate_markdown_report())
    
    # Save outputs
    output_dir = repo_path / "use-case-prototype-output"
    output_dir.mkdir(exist_ok=True)
    
    (output_dir / "use-case-analysis.json").write_text(json.dumps(results, indent=2))
    (output_dir / "use-case-report.md").write_text(analyzer.generate_markdown_report())
    
    print(f"\n✅ Outputs saved to: {output_dir}")


if __name__ == "__main__":
    main()
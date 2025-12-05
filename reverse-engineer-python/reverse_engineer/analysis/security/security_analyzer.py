"""
SecurityPatternAnalyzer - Analysis component.
"""

import re
from pathlib import Path
from typing import Optional

from ...utils import log_info


class SecurityPatternAnalyzer:
    """Analyzes Spring Security patterns to identify actors and their roles."""

    def __init__(self, verbose: bool = False):
        """Initialize the security pattern analyzer."""
        self.verbose = verbose

        # Spring Security annotation patterns
        self.security_patterns = {
            "preauthorize_role": re.compile(
                r'@PreAuthorize\s*\(\s*["\']hasRole\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE
            ),
            "preauthorize_authority": re.compile(
                r'@PreAuthorize\s*\(\s*["\']hasAuthority\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE
            ),
            "secured_single": re.compile(r'@Secured\s*\(\s*["\']([^"\']+)["\']', re.IGNORECASE),
            "secured_multiple": re.compile(r"@Secured\s*\(\s*\{\s*([^}]+)\s*\}", re.IGNORECASE),
            "roles_allowed": re.compile(r'@RolesAllowed\s*\(\s*["\']?([^"\')\s]+)', re.IGNORECASE),
            "permit_all": re.compile(r"@PermitAll|permitAll\(\)", re.IGNORECASE),
            "deny_all": re.compile(r"@DenyAll|denyAll\(\)", re.IGNORECASE),
        }

        # Role classification patterns
        self.role_classifications = {
            "admin": ["ADMIN", "ADMINISTRATOR", "ROOT", "SUPER", "MANAGER"],
            "user": ["USER", "MEMBER", "CUSTOMER", "CLIENT"],
            "moderator": ["MODERATOR", "MOD", "EDITOR"],
            "guest": ["GUEST", "ANONYMOUS", "PUBLIC"],
            "system": ["SYSTEM", "SERVICE", "API", "INTERNAL"],
        }

    def analyze_security_annotations(self, java_files: list[Path]) -> list[dict]:
        """Analyze Java files for Spring Security annotations."""
        actors = []
        roles_found = set()

        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")
                file_roles = self._extract_roles_from_content(content, java_file)
                roles_found.update(file_roles)

            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze {java_file.name}: {e}")
                continue

        # Convert roles to actors
        for role in roles_found:
            actor = self._create_actor_from_role(role)
            if actor and not any(a["name"] == actor["name"] for a in actors):
                actors.append(actor)

        return actors

    def _extract_roles_from_content(self, content: str, java_file: Path) -> list[str]:
        """Extract roles from Java file content."""
        roles = []

        # Extract roles from @PreAuthorize with hasRole
        for match in self.security_patterns["preauthorize_role"].finditer(content):
            role = match.group(1).strip()
            roles.append(role)
            if self.verbose:
                log_info(f"  Found role '{role}' in @PreAuthorize: {java_file.name}")

        # Extract authorities from @PreAuthorize with hasAuthority
        for match in self.security_patterns["preauthorize_authority"].finditer(content):
            authority = match.group(1).strip()
            roles.append(authority)
            if self.verbose:
                log_info(f"  Found authority '{authority}' in @PreAuthorize: {java_file.name}")

        # Extract roles from @Secured (single role)
        for match in self.security_patterns["secured_single"].finditer(content):
            role = match.group(1).strip()
            roles.append(role)
            if self.verbose:
                log_info(f"  Found role '{role}' in @Secured: {java_file.name}")

        # Extract roles from @Secured (multiple roles)
        for match in self.security_patterns["secured_multiple"].finditer(content):
            roles_text = match.group(1)
            # Parse multiple roles like "ROLE_ADMIN", "ROLE_USER"
            role_matches = re.findall(r'["\']([^"\']+)["\']', roles_text)
            for role in role_matches:
                roles.append(role.strip())
                if self.verbose:
                    log_info(f"  Found role '{role}' in @Secured array: {java_file.name}")

        # Extract roles from @RolesAllowed
        for match in self.security_patterns["roles_allowed"].finditer(content):
            role = match.group(1).strip().strip("\"'")
            roles.append(role)
            if self.verbose:
                log_info(f"  Found role '{role}' in @RolesAllowed: {java_file.name}")

        # Check for public endpoints
        if self.security_patterns["permit_all"].search(content):
            roles.append("PUBLIC")
            if self.verbose:
                log_info(f"  Found public access in: {java_file.name}")

        return roles

    def _create_actor_from_role(self, role: str) -> Optional[dict]:
        """Create an actor from a role/authority string."""
        # Clean up role name (remove ROLE_ prefix if present)
        clean_role = role.replace("ROLE_", "").strip()

        if not clean_role or clean_role in ["", "null", "undefined"]:
            return None

        # Classify the role
        actor_type = self._classify_role(clean_role)
        access_level = self._determine_access_level(clean_role)

        # Generate human-readable name
        display_name = self._generate_display_name(clean_role)

        return {
            "name": display_name,
            "type": actor_type,
            "access_level": access_level,
            "roles": [role],
            "identified_from": [f"Security annotation: {role}"],
        }

    def _classify_role(self, role: str) -> str:
        """Classify a role into actor types."""
        role_upper = role.upper()

        for actor_type, keywords in self.role_classifications.items():
            if any(keyword in role_upper for keyword in keywords):
                if actor_type == "guest":
                    return "end_user"
                elif actor_type == "system":
                    return "external_system"
                else:
                    return "internal_user"

        # Default classification
        return "end_user"

    def _determine_access_level(self, role: str) -> str:
        """Determine access level from role."""
        role_upper = role.upper()

        if any(keyword in role_upper for keyword in ["ADMIN", "ROOT", "SUPER"]):
            return "admin"
        elif any(keyword in role_upper for keyword in ["MANAGER", "MODERATOR", "EDITOR"]):
            return "privileged"
        elif any(keyword in role_upper for keyword in ["SYSTEM", "SERVICE", "API"]):
            return "api_integration"
        elif any(keyword in role_upper for keyword in ["PUBLIC", "GUEST", "ANONYMOUS"]):
            return "public"
        else:
            return "authenticated"

    def _generate_display_name(self, role: str) -> str:
        """Generate a human-readable display name from role."""
        # Convert from SCREAMING_SNAKE_CASE to Title Case
        words = role.replace("_", " ").replace("-", " ").split()
        return " ".join(word.capitalize() for word in words)

    def analyze_spring_security_config(self, config_files: list[Path]) -> list[dict]:
        """Analyze Spring Security configuration files for additional actor information."""
        actors = []

        for config_file in config_files:
            try:
                if config_file.suffix in [".java", ".xml", ".yml", ".yaml", ".properties"]:
                    content = config_file.read_text(encoding="utf-8")
                    config_actors = self._extract_actors_from_config(content, config_file)
                    actors.extend(config_actors)

            except Exception as e:
                if self.verbose:
                    log_info(f"Warning: Could not analyze config {config_file.name}: {e}")
                continue

        return actors

    def _extract_actors_from_config(self, content: str, config_file: Path) -> list[dict]:
        """Extract actor information from configuration files."""
        actors = []

        # Look for role hierarchy definitions
        role_hierarchy_pattern = re.compile(
            r"roleHierarchy.*?=.*?([A-Z_]+(?:\s*>\s*[A-Z_]+)*)", re.IGNORECASE | re.DOTALL
        )
        for match in role_hierarchy_pattern.finditer(content):
            hierarchy_text = match.group(1)
            roles = re.findall(r"[A-Z_]+", hierarchy_text)

            for role in roles:
                actor = self._create_actor_from_role(role)
                if actor:
                    actor["identified_from"].append(f"Security config: {config_file.name}")
                    actors.append(actor)

        # Look for user details service configurations
        user_details_pattern = re.compile(
            r'withUser\s*\(\s*["\']([^"\']+)["\'].*?roles?\s*\(\s*["\']([^"\']+)', re.IGNORECASE
        )
        for match in user_details_pattern.finditer(content):
            match.group(1)
            role = match.group(2)

            actor = self._create_actor_from_role(role)
            if actor:
                actor["identified_from"].append(f"User config: {config_file.name}")
                actors.append(actor)

        return actors

"""
UIPatternAnalyzer - Analysis component.
"""

import re


class UIPatternAnalyzer:
    """Analyzes UI patterns to identify role-based access and user types"""

    def __init__(self):
        # Vue.js role-based patterns
        self.vue_patterns = {
            "role_checks": [
                r'v-if=".*role.*"',
                r'v-show=".*role.*"',
                r"hasRole\(",
                r"checkRole\(",
                r"userRole|currentRole|user\.role",
                r"isAdmin|isUser|isModerator|isGuest",
                r"\$auth\.user\.|this\.\$auth\.user",
            ],
            "permission_checks": [
                r'v-if=".*permission.*"',
                r'v-show=".*permission.*"',
                r"hasPermission\(",
                r"checkPermission\(",
                r"userPermissions|permissions\.",
                r"canAccess|canView|canEdit|canDelete",
                r"ability\.can\(|this\.ability\.can\(",
            ],
            "auth_guards": [
                r"beforeRouteEnter|beforeRouteUpdate",
                r"requiresAuth|requiresRole|requiresPermission",
                r"authGuard|roleGuard|permissionGuard",
                r"meta:\s*{\s*requiresAuth",
                r"meta:\s*{\s*roles:",
            ],
        }

        # React role-based patterns
        self.react_patterns = {
            "role_checks": [
                r"user\.role|currentUser\.role|authUser\.role",
                r"hasRole\(|checkRole\(|userHasRole\(",
                r"isAdmin|isUser|isModerator|isGuest",
                r"roles\.includes\(|role\s*===|role\s*!==",
                r"useAuth\(\)|useUser\(\)|useRole\(\)",
            ],
            "permission_checks": [
                r"permissions\.includes\(|permission\s*===",
                r"hasPermission\(|checkPermission\(",
                r"canAccess|canView|canEdit|canDelete",
                r"ability\.can\(|useAbility\(\)",
                r"userPermissions|currentPermissions",
            ],
            "conditional_rendering": [
                r"&&\s*user\.role|&&\s*hasRole",
                r"&&\s*isAuthenticated|&&\s*user\.",
                r"role\s*===.*\?|permission\s*===.*\?",
                r"ProtectedRoute|PrivateRoute|RequireAuth",
                r"RoleBasedRoute|PermissionBasedRoute",
            ],
        }

        # Common UI role indicators
        self.common_ui_roles = {
            "admin": ["admin", "administrator", "super_user", "superuser"],
            "user": ["user", "member", "customer", "client"],
            "moderator": ["moderator", "mod", "editor", "manager"],
            "guest": ["guest", "visitor", "anonymous", "public"],
            "staff": ["staff", "employee", "worker", "team"],
            "owner": ["owner", "creator", "author"],
        }

    def analyze(self, file_path, content):
        """Analyze UI files for role-based patterns"""
        ui_actors = []

        # Determine file type
        if file_path.endswith(".vue"):
            patterns = self.vue_patterns
            framework = "vue"
        elif file_path.endswith((".jsx", ".tsx", ".js", ".ts")) and (
            "react" in content.lower() or "jsx" in content.lower()
        ):
            patterns = self.react_patterns
            framework = "react"
        else:
            return ui_actors

        # Extract roles from patterns
        found_roles = set()

        for _category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract potential role names from the match
                    context = content[max(0, match.start() - 50) : match.end() + 50]
                    roles = self._extract_roles_from_context(context)
                    found_roles.update(roles)

                    self._log_discovery(
                        f"Found {framework} role pattern '{pattern}' in: {file_path}"
                    )

        # Convert found roles to actors
        for role in found_roles:
            actor_name = self._normalize_role_name(role)
            if actor_name:
                ui_actors.append(
                    {
                        "name": actor_name,
                        "type": "ui_role",
                        "framework": framework,
                        "file": file_path,
                    }
                )

        return ui_actors

    def _extract_roles_from_context(self, context):
        """Extract role names from the surrounding context"""
        roles = set()

        # Look for quoted role names
        quote_patterns = [
            r"['\"](\w+)['\"]",
            r"role\s*[=:]\s*['\"](\w+)['\"]",
            r"hasRole\s*\(\s*['\"](\w+)['\"]",
            r"includes\s*\(\s*['\"](\w+)['\"]",
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
                if re.search(rf"\b{re.escape(variation)}\b", context, re.IGNORECASE):
                    roles.add(role_type)

        return roles

    def _is_valid_role(self, role):
        """Check if a string is likely a valid role name"""
        # Common role indicators
        role_keywords = [
            "admin",
            "user",
            "guest",
            "moderator",
            "staff",
            "member",
            "customer",
            "client",
            "owner",
            "manager",
            "editor",
        ]

        return (
            len(role) > 2
            and any(keyword in role for keyword in role_keywords)
            and not role.isdigit()
        )

    def _normalize_role_name(self, role):
        """Normalize role name to standard format"""
        # Map common role variations to standard names
        role_mappings = {
            "admin": "Administrator",
            "administrator": "Administrator",
            "super_user": "Administrator",
            "superuser": "Administrator",
            "user": "User",
            "member": "User",
            "customer": "Customer",
            "client": "Customer",
            "moderator": "Moderator",
            "mod": "Moderator",
            "staff": "Staff",
            "employee": "Staff",
            "guest": "Guest",
            "visitor": "Guest",
            "anonymous": "Guest",
            "public": "Public",
            "owner": "Owner",
            "manager": "Manager",
            "editor": "Editor",
        }

        return role_mappings.get(role.lower(), role.title())

    def _log_discovery(self, message):
        """Log pattern discovery"""
        print(f"[INFO]   {message}")


# Dataclasses now imported from domain package (see imports at top)

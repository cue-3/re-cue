"""
Core analyzer module for discovering project components.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

from .utils import log_info


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
        
        self.endpoints: List[Endpoint] = []
        self.models: List[Model] = []
        self.views: List[View] = []
        self.services: List[Service] = []
        self.features: List[str] = []
        
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
    
    def analyze(self):
        """Run all analysis steps with progress feedback."""
        import sys
        
        print("\n🔍 Starting project analysis...\n", file=sys.stderr)
        
        # Stage 1: Endpoints
        print("📍 Stage 1/5: Discovering API endpoints...", file=sys.stderr, end=" ", flush=True)
        self.discover_endpoints()
        print(f"✓ Found {self.endpoint_count} endpoints", file=sys.stderr)
        
        # Stage 2: Models
        print("📦 Stage 2/5: Analyzing data models...", file=sys.stderr, end=" ", flush=True)
        self.discover_models()
        print(f"✓ Found {self.model_count} models", file=sys.stderr)
        
        # Stage 3: Views
        print("🎨 Stage 3/5: Discovering UI views...", file=sys.stderr, end=" ", flush=True)
        self.discover_views()
        print(f"✓ Found {self.view_count} views", file=sys.stderr)
        
        # Stage 4: Services
        print("⚙️  Stage 4/5: Detecting backend services...", file=sys.stderr, end=" ", flush=True)
        self.discover_services()
        print(f"✓ Found {self.service_count} services", file=sys.stderr)
        
        # Stage 5: Features
        print("✨ Stage 5/5: Extracting features...", file=sys.stderr, end=" ", flush=True)
        self.extract_features()
        print(f"✓ Identified {self.feature_count} features", file=sys.stderr)
        
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

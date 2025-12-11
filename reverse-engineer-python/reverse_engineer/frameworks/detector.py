"""
Technology stack detector for identifying project frameworks.
"""

import json
import re
from pathlib import Path
from typing import Optional

# Import TechStack from domain package
from ..domain import TechStack
from ..utils import log_info


class TechDetector:
    """Detects technology stack and framework from project structure."""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = Path(repo_root)
        self.verbose = verbose

        # Framework detection rules
        self.detection_rules = {
            "java_spring": {
                "name": "Java Spring Boot",
                "language": "java",
                "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
                "patterns": [
                    (r"<artifactId>spring-boot", "pom.xml"),
                    (r"org\.springframework\.boot", "build.gradle"),
                    (r"@SpringBootApplication", "**/*.java"),
                    (r"@RestController", "**/*.java"),
                ],
                "structure": ["src/main/java", "src/main/resources"],
            },
            "nodejs_express": {
                "name": "Node.js Express",
                "language": "javascript",
                "files": ["package.json"],
                "patterns": [
                    (r'"express":', "package.json"),
                    (r'require\([\'"]express[\'"]\)', "**/*.js"),
                    (r"app\.(get|post|put|delete)", "**/*.js"),
                ],
                "exclude_patterns": [
                    (r'"@nestjs/core":', "package.json"),  # Exclude if NestJS
                ],
            },
            "nodejs_nestjs": {
                "name": "NestJS",
                "language": "typescript",
                "files": ["package.json", "nest-cli.json"],
                "patterns": [
                    (r'"@nestjs/core":', "package.json"),
                    (r"@Controller\(", "**/*.ts"),
                    (r"@Module\(", "**/*.ts"),
                ],
                "structure": ["src"],
            },
            "python_django": {
                "name": "Python Django",
                "language": "python",
                "files": ["manage.py", "requirements.txt", "pyproject.toml"],
                "patterns": [
                    (r"django", "requirements.txt"),
                    (r"from django", "**/*.py"),
                    (r"django-admin", "manage.py"),
                    (r"DJANGO_SETTINGS_MODULE", "**/*.py"),
                ],
                "structure": ["*/settings.py", "*/urls.py"],
            },
            "python_flask": {
                "name": "Python Flask",
                "language": "python",
                "files": ["requirements.txt", "pyproject.toml"],
                "patterns": [
                    (r"flask", "requirements.txt"),
                    (r"from flask import", "**/*.py"),
                    (r"Flask\(__name__\)", "**/*.py"),
                    (r"@app\.route", "**/*.py"),
                ],
                "exclude_patterns": [
                    (r"django", "requirements.txt"),  # Exclude if Django
                    (r"fastapi", "requirements.txt"),  # Exclude if FastAPI
                ],
            },
            "python_fastapi": {
                "name": "Python FastAPI",
                "language": "python",
                "files": ["requirements.txt", "pyproject.toml"],
                "patterns": [
                    (r"fastapi", "requirements.txt"),
                    (r"from fastapi import", "**/*.py"),
                    (r"FastAPI\(", "**/*.py"),
                    (r"@app\.(get|post|put|delete)", "**/*.py"),
                ],
                "structure": ["app"],
            },
            "dotnet": {
                "name": "ASP.NET Core",
                "language": "csharp",
                "files": ["*.csproj", "*.sln"],
                "patterns": [
                    (r'<Project Sdk="Microsoft\.NET\.Sdk\.Web">', "*.csproj"),
                    (r"\[ApiController\]", "**/*.cs"),
                    (r"\[Route\(", "**/*.cs"),
                    (r"using Microsoft\.AspNetCore", "**/*.cs"),
                ],
                "structure": ["Controllers", "Models"],
            },
            "ruby_rails": {
                "name": "Ruby on Rails",
                "language": "ruby",
                "files": ["Gemfile", "config.ru", "Rakefile"],
                "patterns": [
                    (r'gem [\'"]rails[\'"]', "Gemfile"),
                    (r"Rails\.application", "config.ru"),
                    (r"class \w+Controller < ApplicationController", "**/*.rb"),
                ],
                "structure": ["app/controllers", "app/models", "config/routes.rb"],
            },
            "php_laravel": {
                "name": "PHP Laravel",
                "language": "php",
                "files": ["composer.json", "artisan"],
                "patterns": [
                    (r'"laravel/framework":', "composer.json"),
                    (r"Illuminate\\Foundation\\Application", "**/*.php"),
                    (r"Route::(get|post|resource)", "routes/*.php"),
                    (r"extends\s+Model", "**/*.php"),
                ],
                "structure": ["app/Http/Controllers", "app/Models", "routes/web.php"],
            },
        }

    def detect(self) -> TechStack:
        """
        Detect the technology stack of the project.

        Returns:
            TechStack: Detected technology information
        """
        log_info("Detecting technology stack...", self.verbose)

        scores = {}
        indicators = {}

        # Score each framework
        for framework_id, rules in self.detection_rules.items():
            score, found_indicators = self._score_framework(framework_id, rules)
            scores[framework_id] = score
            indicators[framework_id] = found_indicators

            if self.verbose and score > 0:
                log_info(f"  {rules['name']}: {score:.2f} confidence", self.verbose)

        # Get best match
        if not scores or max(scores.values()) == 0:
            log_info("  ⚠️  Could not detect framework, defaulting to Java Spring", self.verbose)
            return TechStack(
                framework_id="java_spring",
                name="Java Spring Boot",
                language="java",
                confidence=0.0,
                indicators=["default"],
            )

        best_framework = max(scores, key=lambda k: scores[k])
        best_score = scores[best_framework]
        rules = self.detection_rules[best_framework]

        # Extract version if possible
        version = self._extract_version(best_framework)

        tech_stack = TechStack(
            framework_id=best_framework,
            name=rules["name"],
            language=rules["language"],
            version=version,
            confidence=best_score,
            indicators=indicators[best_framework],
        )

        log_info(f"✓ Detected: {tech_stack.name} (confidence: {best_score:.0%})", self.verbose)
        if version:
            log_info(f"  Version: {version}", self.verbose)

        return tech_stack

    def _score_framework(self, framework_id: str, rules: dict) -> tuple:
        """
        Score how well a framework matches the project.

        Returns:
            Tuple of (score, indicators_found)
        """
        score = 0.0
        indicators = []
        max_score = 0.0

        # Check for required files (0.3 weight)
        max_score += 0.3
        file_matches = 0
        for file_pattern in rules.get("files", []):
            if self._find_files(file_pattern):
                file_matches += 1
                indicators.append(f"file:{file_pattern}")

        if file_matches > 0:
            score += 0.3 * (file_matches / len(rules["files"]))

        # Check for pattern matches (0.5 weight)
        patterns = rules.get("patterns", [])
        if patterns:
            max_score += 0.5
            pattern_matches = 0
            for pattern, file_glob in patterns:
                if self._find_pattern(pattern, file_glob):
                    pattern_matches += 1
                    indicators.append(f"pattern:{pattern[:30]}")

            if pattern_matches > 0:
                score += 0.5 * (pattern_matches / len(patterns))

        # Check directory structure (0.2 weight)
        structure = rules.get("structure", [])
        if structure:
            max_score += 0.2
            structure_matches = 0
            for dir_pattern in structure:
                if self._find_files(dir_pattern):
                    structure_matches += 1
                    indicators.append(f"structure:{dir_pattern}")

            if structure_matches > 0:
                score += 0.2 * (structure_matches / len(structure))

        # Check for exclude patterns (negative scoring)
        exclude_patterns = rules.get("exclude_patterns", [])
        for pattern, file_glob in exclude_patterns:
            if self._find_pattern(pattern, file_glob):
                score = 0.0
                indicators = [f"excluded:{pattern[:30]}"]
                break

        # Normalize score
        if max_score > 0:
            score = score / max_score

        return score, indicators

    def _find_files(self, pattern: str) -> list[Path]:
        """Find files matching pattern in repository."""
        try:
            matches = list(self.repo_root.glob(pattern))
            # Also try rglob for recursive patterns
            if not matches and "**" not in pattern:
                matches = list(self.repo_root.rglob(pattern))
            return matches
        except Exception as e:
            log_info(f"  Error searching for {pattern}: {e}", self.verbose)
            return []

    def _find_pattern(self, pattern: str, file_glob: str) -> bool:
        """Search for pattern in files matching glob."""
        try:
            files = self._find_files(file_glob)
            regex = re.compile(pattern, re.IGNORECASE)

            for file_path in files[:10]:  # Limit to first 10 files for performance
                if not file_path.is_file():
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if regex.search(content):
                        return True
                except Exception:
                    continue

            return False
        except Exception as e:
            log_info(f"  Error searching pattern {pattern}: {e}", self.verbose)
            return False

    def _extract_version(self, framework_id: str) -> Optional[str]:
        """Extract framework version from project files."""
        try:
            if framework_id == "java_spring":
                return self._extract_java_version()
            elif framework_id.startswith("nodejs_"):
                return self._extract_nodejs_version()
            elif framework_id.startswith("python_"):
                return self._extract_python_version(framework_id)
            elif framework_id == "dotnet":
                return self._extract_dotnet_version()
            elif framework_id == "ruby_rails":
                return self._extract_ruby_version()
            elif framework_id == "php_laravel":
                return self._extract_laravel_version()
        except Exception as e:
            log_info(f"  Could not extract version: {e}", self.verbose)

        return None

    def _extract_java_version(self) -> Optional[str]:
        """Extract Spring Boot version from pom.xml or build.gradle."""
        # Try pom.xml
        pom_files = list(self.repo_root.glob("pom.xml"))
        if pom_files:
            content = pom_files[0].read_text()
            match = re.search(r"<spring-boot\.version>([^<]+)</spring-boot\.version>", content)
            if match:
                return match.group(1)
            match = re.search(r"<version>([^<]+)</version>.*spring-boot", content, re.DOTALL)
            if match:
                return match.group(1)

        # Try build.gradle
        gradle_files = list(self.repo_root.glob("build.gradle*"))
        if gradle_files:
            content = gradle_files[0].read_text()
            match = re.search(
                r'org\.springframework\.boot[\'"]?\s*version\s*[\'"]([^\'\"]+)', content
            )
            if match:
                return match.group(1)

        return None

    def _extract_nodejs_version(self) -> Optional[str]:
        """Extract Node.js framework version from package.json."""
        package_json = self.repo_root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                # Look for express or @nestjs/core
                for pkg in ["express", "@nestjs/core"]:
                    if pkg in deps:
                        version = deps[pkg].lstrip("^~>=")
                        return version
            except Exception:
                pass

        return None

    def _extract_python_version(self, framework_id: str) -> Optional[str]:
        """Extract Python framework version from requirements.txt."""
        requirements = self.repo_root / "requirements.txt"
        if requirements.exists():
            content = requirements.read_text()

            framework_name = framework_id.replace("python_", "")
            match = re.search(rf"{framework_name}==([0-9.]+)", content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_dotnet_version(self) -> Optional[str]:
        """Extract .NET version from .csproj file."""
        csproj_files = list(self.repo_root.rglob("*.csproj"))
        if csproj_files:
            content = csproj_files[0].read_text()
            match = re.search(r"<TargetFramework>([^<]+)</TargetFramework>", content)
            if match:
                return match.group(1)

        return None

    def _extract_ruby_version(self) -> Optional[str]:
        """Extract Rails version from Gemfile."""
        gemfile = self.repo_root / "Gemfile"
        if gemfile.exists():
            content = gemfile.read_text()
            match = re.search(r'gem [\'"]rails[\'"],\s*[\'"]([^\'\"]+)[\'"]', content)
            if match:
                return match.group(1)

        return None

    def _extract_laravel_version(self) -> Optional[str]:
        """Extract Laravel version from composer.json."""
        composer_json = self.repo_root / "composer.json"
        if composer_json.exists():
            try:
                data = json.loads(composer_json.read_text())
                require = data.get("require", {})

                if "laravel/framework" in require:
                    version = require["laravel/framework"]
                    # Remove version constraints (^, ~, >=, etc.)
                    version = re.sub(r"[^\d.].*", "", version.lstrip("^~>="))
                    return version
            except Exception:
                pass

        return None

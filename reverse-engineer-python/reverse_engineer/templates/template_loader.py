"""Template loading system with framework-specific override support."""

from pathlib import Path
from typing import Optional
import re


class TemplateLoader:
    """Loads templates with framework-specific override support.
    
    This class implements a template hierarchy where framework-specific
    templates can override common templates. The fallback logic ensures
    that if a framework-specific template doesn't exist, the common
    template is used instead.
    
    Template Hierarchy:
    1. Framework-specific template (e.g., frameworks/java_spring/endpoint_section.md)
    2. Common template (e.g., common/phase1-structure.md)
    
    Usage:
        loader = TemplateLoader(framework_id='java_spring')
        template = loader.load('endpoint_section.md')
    """
    
    def __init__(self, framework_id: Optional[str] = None):
        """Initialize template loader.
        
        Args:
            framework_id: Framework identifier (e.g., 'java_spring', 'nodejs_express')
                         If None, only common templates will be used.
        """
        self.framework_id = framework_id
        self.template_dir = Path(__file__).parent
        self.common_dir = self.template_dir / "common"
        
        if framework_id:
            # Map framework_id to template directory
            # nodejs_express, nodejs_nestjs -> nodejs
            # python_django, python_flask, python_fastapi -> python
            if framework_id.startswith('nodejs_'):
                self.framework_dir = self.template_dir / "frameworks" / "nodejs"
            elif framework_id.startswith('python_'):
                self.framework_dir = self.template_dir / "frameworks" / "python"
            else:
                # java_spring -> java_spring
                self.framework_dir = self.template_dir / "frameworks" / framework_id
        else:
            self.framework_dir = None
    
    def load(self, template_name: str) -> str:
        """Load a template with fallback logic.
        
        Tries to load framework-specific template first, falls back to common template.
        
        Args:
            template_name: Name of template file (e.g., 'endpoint_section.md')
        
        Returns:
            Template content as string
        
        Raises:
            FileNotFoundError: If template not found in either location
        """
        # Try framework-specific template first
        if self.framework_dir:
            framework_template = self._try_load_framework_template(template_name)
            if framework_template is not None:
                return framework_template
        
        # Fall back to common template
        return self._load_common_template(template_name)
    
    def _try_load_framework_template(self, template_name: str) -> Optional[str]:
        """Try to load framework-specific template.
        
        Args:
            template_name: Name of template file
        
        Returns:
            Template content if found, None otherwise
        """
        if not self.framework_dir or not self.framework_dir.exists():
            return None
        
        template_path = self.framework_dir / template_name
        
        if template_path.exists() and template_path.is_file():
            return template_path.read_text(encoding='utf-8')
        
        return None
    
    def _load_common_template(self, template_name: str) -> str:
        """Load common template.
        
        Args:
            template_name: Name of template file
        
        Returns:
            Template content
        
        Raises:
            FileNotFoundError: If template not found
        """
        template_path = self.common_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(
                f"Template '{template_name}' not found in common templates.\n"
                f"Expected path: {template_path}"
            )
        
        return template_path.read_text(encoding='utf-8')
    
    def exists(self, template_name: str) -> bool:
        """Check if a template exists (framework-specific or common).
        
        Args:
            template_name: Name of template file
        
        Returns:
            True if template exists, False otherwise
        """
        # Check framework-specific first
        if self.framework_dir:
            framework_path = self.framework_dir / template_name
            if framework_path.exists():
                return True
        
        # Check common
        common_path = self.common_dir / template_name
        return common_path.exists()
    
    def list_available(self, include_common: bool = True, 
                      include_framework: bool = True) -> dict:
        """List all available templates.
        
        Args:
            include_common: Include common templates
            include_framework: Include framework-specific templates
        
        Returns:
            Dict with 'common' and 'framework' keys containing lists of template names
        """
        result = {'common': [], 'framework': []}
        
        if include_common and self.common_dir.exists():
            result['common'] = [
                f.name for f in self.common_dir.glob('*.md')
                if f.is_file()
            ]
        
        if include_framework and self.framework_dir and self.framework_dir.exists():
            result['framework'] = [
                f.name for f in self.framework_dir.glob('*.md')
                if f.is_file()
            ]
        
        return result
    
    def apply_variables(self, template: str, **variables) -> str:
        """Apply variables to template.
        
        Replaces {variable_name} placeholders with provided values.
        
        Args:
            template: Template string with {placeholders}
            **variables: Variable name-value pairs
        
        Returns:
            Template with variables replaced
        """
        result = template
        
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            # Convert value to string, handle None
            str_value = str(value) if value is not None else ""
            result = result.replace(placeholder, str_value)
        
        return result
    
    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get the actual path of a template (framework-specific or common).
        
        Args:
            template_name: Name of template file
        
        Returns:
            Path to template file, or None if not found
        """
        # Check framework-specific first
        if self.framework_dir:
            framework_path = self.framework_dir / template_name
            if framework_path.exists():
                return framework_path
        
        # Check common
        common_path = self.common_dir / template_name
        if common_path.exists():
            return common_path
        
        return None
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TemplateLoader(framework_id='{self.framework_id}', "
            f"common_dir='{self.common_dir}', "
            f"framework_dir='{self.framework_dir}')"
        )

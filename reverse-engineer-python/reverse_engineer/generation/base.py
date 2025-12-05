"""
Base generator class for all document generators.
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer


class BaseGenerator:
    """Base class for all generators."""

    def __init__(self, analyzer: "ProjectAnalyzer"):
        """
        Initialize the generator.

        Args:
            analyzer: ProjectAnalyzer instance with discovered components
        """
        self.analyzer = analyzer
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate(self, *args, **kwargs) -> str:
        """
        Generate the document.

        Returns:
            Generated document as string
        """
        raise NotImplementedError("Subclasses must implement generate()")

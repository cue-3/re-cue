"""
Go web framework analyzers.

Supports:
- Gin (github.com/gin-gonic/gin)
- Echo (github.com/labstack/echo)
- Fiber (github.com/gofiber/fiber)
"""

from .echo_analyzer import EchoAnalyzer
from .fiber_analyzer import FiberAnalyzer
from .gin_analyzer import GinAnalyzer

__all__ = ["GinAnalyzer", "EchoAnalyzer", "FiberAnalyzer"]

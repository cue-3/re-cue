"""
Go web framework analyzers.

Supports:
- Gin (github.com/gin-gonic/gin)
- Echo (github.com/labstack/echo)
- Fiber (github.com/gofiber/fiber)
"""

from .gin_analyzer import GinAnalyzer
from .echo_analyzer import EchoAnalyzer
from .fiber_analyzer import FiberAnalyzer

__all__ = ["GinAnalyzer", "EchoAnalyzer", "FiberAnalyzer"]

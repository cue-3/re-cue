"""
Workflow pattern analysis module.

This module provides workflow pattern detection capabilities for identifying
multi-step business workflows including async operations, scheduled tasks,
event-driven patterns, state machines, and saga patterns.
"""

from .workflow_analyzer import WorkflowAnalyzer

__all__ = ["WorkflowAnalyzer"]

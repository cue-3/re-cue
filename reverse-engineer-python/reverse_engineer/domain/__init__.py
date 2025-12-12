"""
Core domain models for RE-cue.

This package contains pure domain models with no dependencies on other
reverse_engineer modules, following domain-driven design principles.
"""

from .analysis_result import AnalysisResult
from .entities import (
    Actor,
    Endpoint,
    Model,
    Relationship,
    Service,
    SystemBoundary,
    UseCase,
    View,
)
from .git import (
    BlameEntry,
    BlameResult,
    BranchInfo,
    ChangedFile,
    Changelog,
    ChangelogEntry,
    CommitInfo,
    FileChangeType,
    GitAnalysisResult,
    TagInfo,
)
from .journey import (
    Epic,
    JourneyMap,
    JourneyStage,
    Touchpoint,
    UserJourney,
    UserStory,
)
from .tech_stack import TechStack
from .test_scenario import (
    ApiTestCase,
    CoverageMapping,
    IntegrationTestSuite,
    TestData,
    TestScenario,
    TestStep,
)
from .traceability import (
    CodeLink,
    ImpactAnalysis,
    ImpactedItem,
    TestLink,
    TraceabilityEntry,
    TraceabilityMatrix,
)
from .transaction import (
    NestedTransaction,
    RollbackRule,
    TransactionAnalysisResult,
    TransactionBoundary,
    TransactionIsolation,
    TransactionPattern,
    TransactionPropagation,
)
from .progress import (
    AnalysisProgress,
    AnalysisStage,
    FileProgress,
    ProgressCallback,
    ProgressStatus,
    ProgressSummary,
    StageProgress,
)
from .use_case_model import EditableUseCase
from .workflow import (
    AsyncOperation,
    EventListener,
    SagaPattern,
    SagaStep,
    ScheduledTask,
    ScheduleType,
    StateMachine,
    StateTransition,
    WorkflowAnalysisResult,
    WorkflowPattern,
    WorkflowStep,
    WorkflowType,
)

__all__ = [
    # Core entities
    "Endpoint",
    "Model",
    "View",
    "Service",
    "Actor",
    "SystemBoundary",
    "Relationship",
    "UseCase",
    # Tech stack
    "TechStack",
    # Containers
    "AnalysisResult",
    # Use case models
    "EditableUseCase",
    # Test scenario models
    "TestData",
    "TestStep",
    "ApiTestCase",
    "TestScenario",
    "CoverageMapping",
    "IntegrationTestSuite",
    # Traceability models
    "CodeLink",
    "TestLink",
    "TraceabilityEntry",
    "ImpactedItem",
    "ImpactAnalysis",
    "TraceabilityMatrix",
    # Journey models
    "Touchpoint",
    "JourneyStage",
    "UserJourney",
    "UserStory",
    "Epic",
    "JourneyMap",
    # Git models
    "FileChangeType",
    "ChangedFile",
    "CommitInfo",
    "BlameEntry",
    "BlameResult",
    "BranchInfo",
    "TagInfo",
    "ChangelogEntry",
    "Changelog",
    "GitAnalysisResult",
    # Transaction models
    "TransactionPropagation",
    "TransactionIsolation",
    "RollbackRule",
    "TransactionBoundary",
    "NestedTransaction",
    "TransactionPattern",
    "TransactionAnalysisResult",
    # Progress tracking models
    "AnalysisStage",
    "ProgressStatus",
    "FileProgress",
    "StageProgress",
    "AnalysisProgress",
    "ProgressCallback",
    "ProgressSummary",
    # Workflow models
    "WorkflowType",
    "ScheduleType",
    "AsyncOperation",
    "ScheduledTask",
    "EventListener",
    "StateTransition",
    "StateMachine",
    "SagaStep",
    "SagaPattern",
    "WorkflowStep",
    "WorkflowPattern",
    "WorkflowAnalysisResult",
]

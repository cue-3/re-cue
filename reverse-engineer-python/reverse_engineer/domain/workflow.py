"""
Workflow pattern domain models for RE-cue.

These dataclasses represent multi-step workflow patterns discovered
during code analysis, including async operations, scheduled tasks,
event-driven workflows, state machines, and saga patterns.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class WorkflowType(Enum):
    """Types of workflow patterns."""

    ASYNC = "async"  # @Async asynchronous operations
    SCHEDULED = "scheduled"  # @Scheduled background jobs
    EVENT_DRIVEN = "event_driven"  # @EventListener event handlers
    STATE_MACHINE = "state_machine"  # State transition patterns
    SAGA = "saga"  # Saga pattern with compensation
    ORCHESTRATION = "orchestration"  # Multi-step service orchestration


class ScheduleType(Enum):
    """Types of scheduled task configurations."""

    CRON = "cron"  # Cron expression
    FIXED_RATE = "fixed_rate"  # Fixed rate execution
    FIXED_DELAY = "fixed_delay"  # Fixed delay between executions
    INITIAL_DELAY = "initial_delay"  # Initial delay before first execution


@dataclass
class AsyncOperation:
    """Represents an asynchronous operation detected in code."""

    method_name: str
    class_name: str
    file_path: Optional[Path] = None
    line_number: int = 0

    # Async configuration
    executor: str = "default"  # Thread pool executor name
    return_type: str = "void"  # Return type (void, Future, CompletableFuture)

    # Analysis metadata
    annotation_text: str = ""
    identified_from: list[str] = field(default_factory=list)

    @property
    def is_fire_and_forget(self) -> bool:
        """Check if this is a fire-and-forget async operation."""
        return self.return_type == "void"


@dataclass
class ScheduledTask:
    """Represents a scheduled task detected in code."""

    method_name: str
    class_name: str
    file_path: Optional[Path] = None
    line_number: int = 0

    # Schedule configuration
    schedule_type: ScheduleType = ScheduleType.CRON
    cron_expression: str = ""
    fixed_rate_ms: int = -1  # milliseconds
    fixed_delay_ms: int = -1  # milliseconds
    initial_delay_ms: int = -1  # milliseconds
    time_unit: str = "MILLISECONDS"

    # Analysis metadata
    annotation_text: str = ""
    identified_from: list[str] = field(default_factory=list)

    @property
    def schedule_description(self) -> str:
        """Get human-readable schedule description."""
        if self.schedule_type == ScheduleType.CRON:
            return f"Cron: {self.cron_expression}"
        elif self.schedule_type == ScheduleType.FIXED_RATE:
            return f"Every {self.fixed_rate_ms}ms"
        elif self.schedule_type == ScheduleType.FIXED_DELAY:
            return f"Delay {self.fixed_delay_ms}ms between executions"
        return "Unknown schedule"


@dataclass
class EventListener:
    """Represents an event listener detected in code."""

    method_name: str
    class_name: str
    file_path: Optional[Path] = None
    line_number: int = 0

    # Event configuration
    event_types: list[str] = field(default_factory=list)  # Event class names
    condition: str = ""  # SpEL condition expression
    is_transactional: bool = False  # @TransactionalEventListener
    phase: str = ""  # Transaction phase (AFTER_COMMIT, AFTER_ROLLBACK, etc.)

    # Analysis metadata
    annotation_text: str = ""
    identified_from: list[str] = field(default_factory=list)

    @property
    def is_conditional(self) -> bool:
        """Check if listener has a condition."""
        return bool(self.condition)


@dataclass
class StateTransition:
    """Represents a state transition in a state machine."""

    from_state: str
    to_state: str
    trigger: str  # Event or action that triggers transition
    guard: str = ""  # Condition for transition
    action: str = ""  # Action performed during transition


@dataclass
class StateMachine:
    """Represents a state machine pattern detected in code."""

    name: str
    class_name: str
    file_path: Optional[Path] = None

    # State machine definition
    states: list[str] = field(default_factory=list)
    initial_state: str = ""
    final_states: list[str] = field(default_factory=list)
    transitions: list[StateTransition] = field(default_factory=list)

    # Implementation details
    state_enum: str = ""  # Enum class name for states
    state_field: str = ""  # Field that holds current state

    @property
    def transition_count(self) -> int:
        """Get number of transitions."""
        return len(self.transitions)


@dataclass
class SagaStep:
    """Represents a step in a saga pattern."""

    step_name: str
    method_name: str
    compensation_method: str = ""  # Compensating transaction method
    description: str = ""


@dataclass
class SagaPattern:
    """Represents a saga pattern for distributed transactions."""

    name: str
    class_name: str
    file_path: Optional[Path] = None

    # Saga definition
    steps: list[SagaStep] = field(default_factory=list)
    orchestrator_method: str = ""  # Method that orchestrates the saga

    # Pattern characteristics
    is_choreography: bool = False  # True for event-based, False for orchestration
    compensation_strategy: str = "backward"  # backward or forward recovery

    @property
    def step_count(self) -> int:
        """Get number of steps in saga."""
        return len(self.steps)

    @property
    def has_compensation(self) -> bool:
        """Check if saga has compensation logic."""
        return any(step.compensation_method for step in self.steps)


@dataclass
class WorkflowStep:
    """Represents a single step in a multi-step workflow."""

    step_number: int
    description: str
    method_name: str
    service_class: str = ""
    is_async: bool = False
    is_transactional: bool = False
    depends_on: list[int] = field(default_factory=list)  # Step dependencies


@dataclass
class WorkflowPattern:
    """Represents a detected workflow pattern in the codebase."""

    pattern_type: WorkflowType
    name: str
    description: str
    class_name: str = ""
    file_path: Optional[Path] = None

    # Pattern-specific details
    steps: list[WorkflowStep] = field(default_factory=list)
    async_operations: list[AsyncOperation] = field(default_factory=list)
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    event_listeners: list[EventListener] = field(default_factory=list)
    state_machine: Optional[StateMachine] = None
    saga: Optional[SagaPattern] = None

    # Recommendations
    recommendation: str = ""
    complexity_score: int = 1  # 1-5, higher is more complex

    @property
    def step_count(self) -> int:
        """Get number of steps in workflow."""
        return len(self.steps)


@dataclass
class WorkflowAnalysisResult:
    """Result of workflow pattern analysis."""

    project_name: str = ""
    async_operations: list[AsyncOperation] = field(default_factory=list)
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    event_listeners: list[EventListener] = field(default_factory=list)
    state_machines: list[StateMachine] = field(default_factory=list)
    saga_patterns: list[SagaPattern] = field(default_factory=list)
    workflow_patterns: list[WorkflowPattern] = field(default_factory=list)

    # Statistics
    total_async_ops: int = 0
    total_scheduled_tasks: int = 0
    total_event_listeners: int = 0
    transactional_listeners_count: int = 0
    total_state_machines: int = 0
    total_sagas: int = 0
    total_workflows: int = 0

    def compute_statistics(self) -> None:
        """Compute statistics from detected patterns."""
        self.total_async_ops = len(self.async_operations)
        self.total_scheduled_tasks = len(self.scheduled_tasks)
        self.total_event_listeners = len(self.event_listeners)
        self.transactional_listeners_count = sum(
            1 for listener in self.event_listeners if listener.is_transactional
        )
        self.total_state_machines = len(self.state_machines)
        self.total_sagas = len(self.saga_patterns)
        self.total_workflows = len(self.workflow_patterns)

    @property
    def has_async_patterns(self) -> bool:
        """Check if any async patterns were detected."""
        return self.total_async_ops > 0

    @property
    def has_scheduled_patterns(self) -> bool:
        """Check if any scheduled patterns were detected."""
        return self.total_scheduled_tasks > 0

    @property
    def has_event_driven_patterns(self) -> bool:
        """Check if any event-driven patterns were detected."""
        return self.total_event_listeners > 0

    @property
    def complexity_summary(self) -> str:
        """Get a summary of workflow complexity."""
        patterns = []
        if self.has_async_patterns:
            patterns.append(f"{self.total_async_ops} async")
        if self.has_scheduled_patterns:
            patterns.append(f"{self.total_scheduled_tasks} scheduled")
        if self.has_event_driven_patterns:
            patterns.append(f"{self.total_event_listeners} event-driven")
        if self.total_state_machines > 0:
            patterns.append(f"{self.total_state_machines} state machines")
        if self.total_sagas > 0:
            patterns.append(f"{self.total_sagas} sagas")

        if not patterns:
            return "No workflow patterns detected"
        return ", ".join(patterns)

"""
WorkflowAnalyzer - Detects and documents multi-step workflow patterns.

This module provides workflow pattern detection capabilities including:
- @Async annotation analysis (Spring)
- @Scheduled task detection with cron/rate/delay parsing
- @EventListener and @TransactionalEventListener detection
- State machine pattern identification
- Saga pattern detection for distributed transactions
- Multi-step orchestration workflow identification
"""

import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

from ...domain.workflow import (
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
    WorkflowType,
)
from ...utils import log_info


class WorkflowAnalyzer:
    """
    Analyzes multi-step workflow patterns in Java Spring applications.

    This analyzer detects various workflow patterns:
    - Async operations (@Async)
    - Scheduled tasks (@Scheduled)
    - Event-driven flows (@EventListener, @TransactionalEventListener)
    - State machine patterns
    - Saga patterns for distributed transactions
    """

    # Regex patterns for workflow annotation parsing
    ASYNC_PATTERN = re.compile(r"@Async\s*(?:\(([^)]*)\))?", re.MULTILINE)

    SCHEDULED_PATTERN = re.compile(r"@Scheduled\s*\(([^)]+)\)", re.MULTILINE | re.DOTALL)

    # Scheduled attribute patterns
    CRON_PATTERN = re.compile(r'cron\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    FIXED_RATE_PATTERN = re.compile(r"fixedRate\s*=\s*(\d+)", re.IGNORECASE)
    FIXED_DELAY_PATTERN = re.compile(r"fixedDelay\s*=\s*(\d+)", re.IGNORECASE)
    INITIAL_DELAY_PATTERN = re.compile(r"initialDelay\s*=\s*(\d+)", re.IGNORECASE)
    TIME_UNIT_PATTERN = re.compile(r"timeUnit\s*=\s*TimeUnit\.(\w+)", re.IGNORECASE)

    # Event listener patterns
    EVENT_LISTENER_PATTERN = re.compile(r"@EventListener\s*(?:\(([^)]*)\))?", re.MULTILINE)
    TRANSACTIONAL_EVENT_LISTENER_PATTERN = re.compile(
        r"@TransactionalEventListener\s*\(([^)]+)\)", re.MULTILINE | re.DOTALL
    )

    # Event attributes
    EVENT_CLASSES_PATTERN = re.compile(r"(?:classes\s*=\s*)?\{?\s*([A-Z]\w+\.class[^}]*)\}?")
    EVENT_CONDITION_PATTERN = re.compile(r'condition\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    EVENT_PHASE_PATTERN = re.compile(r"phase\s*=\s*TransactionPhase\.(\w+)", re.IGNORECASE)

    # State machine patterns
    STATE_ENUM_PATTERN = re.compile(r"enum\s+(\w+State)\s*\{([^}]+)\}", re.MULTILINE | re.DOTALL)
    STATE_FIELD_PATTERN = re.compile(r"private\s+(\w+State)\s+(\w+)", re.MULTILINE)
    STATE_TRANSITION_PATTERN = re.compile(
        r"currentState\s*==\s*\w+\.(\w+).*?currentState\s*=\s*\w+\.(\w+)",
        re.MULTILINE | re.DOTALL,
    )

    # Saga patterns - methods with compensating transactions
    SAGA_STEP_PATTERN = re.compile(
        r"public\s+\w+\s+(\w+)\([^)]*\).*?compensate(\w+)", re.MULTILINE | re.DOTALL
    )

    # Pattern for class and method names
    CLASS_PATTERN = re.compile(r"(?:public\s+)?(?:abstract\s+)?class\s+(\w+)", re.MULTILINE)
    METHOD_PATTERN = re.compile(
        r"(?:public|protected|private)?\s*(?:static\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)",
        re.MULTILINE,
    )

    def __init__(self, repo_root: Path, verbose: bool = False):
        """
        Initialize the WorkflowAnalyzer.

        Args:
            repo_root: Root path of the repository to analyze
            verbose: Enable verbose logging
        """
        self.repo_root = repo_root
        self.verbose = verbose
        self._async_operations: list[AsyncOperation] = []
        self._scheduled_tasks: list[ScheduledTask] = []
        self._event_listeners: list[EventListener] = []
        self._state_machines: list[StateMachine] = []
        self._saga_patterns: list[SagaPattern] = []

    def analyze(self) -> WorkflowAnalysisResult:
        """
        Perform full workflow pattern analysis.

        Returns:
            WorkflowAnalysisResult with all detected workflow patterns
        """
        log_info("Starting workflow pattern analysis...", self.verbose)

        # Find all Java files
        java_files = self._find_java_files()
        log_info(f"  Found {len(java_files)} Java files to analyze", self.verbose)

        # Analyze each file for workflow patterns
        for java_file in java_files:
            self._analyze_file(java_file)

        log_info(
            f"  Detected {len(self._async_operations)} async operations", self.verbose
        )
        log_info(
            f"  Detected {len(self._scheduled_tasks)} scheduled tasks", self.verbose
        )
        log_info(
            f"  Detected {len(self._event_listeners)} event listeners", self.verbose
        )
        log_info(
            f"  Detected {len(self._state_machines)} state machines", self.verbose
        )
        log_info(
            f"  Detected {len(self._saga_patterns)} saga patterns", self.verbose
        )

        # Identify high-level workflow patterns
        workflow_patterns = self._identify_workflow_patterns()

        # Build and return result
        result = WorkflowAnalysisResult(
            project_name=self.repo_root.name,
            async_operations=self._async_operations,
            scheduled_tasks=self._scheduled_tasks,
            event_listeners=self._event_listeners,
            state_machines=self._state_machines,
            saga_patterns=self._saga_patterns,
            workflow_patterns=workflow_patterns,
        )
        result.compute_statistics()

        log_info(f"Workflow analysis complete: {result.complexity_summary}", self.verbose)

        return result

    def _find_java_files(self) -> list[Path]:
        """Find all Java files in the repository."""
        java_files = []
        try:
            for file_path in self.repo_root.rglob("*.java"):
                # Skip test files
                if self._is_test_file(file_path):
                    continue
                # Skip build directories
                if any(
                    part in file_path.parts
                    for part in ["target", "build", ".gradle", "node_modules"]
                ):
                    continue
                java_files.append(file_path)
        except (PermissionError, OSError) as e:
            log_info(f"  Warning: Could not scan some directories: {e}", self.verbose)
        return java_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        path_str = str(file_path).lower()
        name = file_path.name.lower()
        return "/test/" in path_str or "/tests/" in path_str or "test" in name or "spec" in name

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Java file for workflow patterns."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            log_info(f"  Warning: Could not read {file_path}: {e}", self.verbose)
            return

        # Extract class name
        class_match = self.CLASS_PATTERN.search(content)
        class_name = class_match.group(1) if class_match else file_path.stem

        # Find all workflow patterns
        lines = content.split("\n")

        # Detect async operations
        for i, line in enumerate(lines):
            if "@Async" in line:
                async_op = self._parse_async_annotation(lines, i, class_name, file_path)
                if async_op:
                    self._async_operations.append(async_op)

        # Detect scheduled tasks
        for i, line in enumerate(lines):
            if "@Scheduled" in line:
                scheduled = self._parse_scheduled_annotation(lines, i, class_name, file_path)
                if scheduled:
                    self._scheduled_tasks.append(scheduled)

        # Detect event listeners
        for i, line in enumerate(lines):
            if "@EventListener" in line or "@TransactionalEventListener" in line:
                listener = self._parse_event_listener_annotation(lines, i, class_name, file_path)
                if listener:
                    self._event_listeners.append(listener)

        # Detect state machines
        state_machine = self._detect_state_machine(content, class_name, file_path)
        if state_machine:
            self._state_machines.append(state_machine)

        # Detect saga patterns
        saga = self._detect_saga_pattern(content, class_name, file_path)
        if saga:
            self._saga_patterns.append(saga)

    def _parse_async_annotation(
        self, lines: list[str], annotation_line_idx: int, class_name: str, file_path: Path
    ) -> Optional[AsyncOperation]:
        """Parse an @Async annotation and create an AsyncOperation."""
        annotation_text = lines[annotation_line_idx].strip()

        # Handle multi-line annotations
        idx = annotation_line_idx
        paren_count = annotation_text.count("(") - annotation_text.count(")")
        while paren_count > 0 and idx + 1 < len(lines):
            idx += 1
            annotation_text += " " + lines[idx].strip()
            paren_count = annotation_text.count("(") - annotation_text.count(")")

        # Find the method this annotation applies to
        method_name = self._find_annotated_method(lines, idx)
        if not method_name:
            return None

        # Parse executor if specified
        executor = "default"
        match = re.search(r'@Async\s*\(\s*["\']([^"\']+)["\']', annotation_text)
        if match:
            executor = match.group(1)

        # Try to determine return type from method signature
        return_type = "void"
        for i in range(idx + 1, min(len(lines), idx + 5)):
            method_line = lines[i].strip()
            if method_line and not method_line.startswith("@"):
                # Match return type in method signature more precisely
                method_sig_match = re.match(
                    r"(?:public|protected|private)?\s*(?:static\s+)?"
                    r"((?:CompletableFuture|Future)<[^>]+>|\w+)\s+\w+\s*\(",
                    method_line,
                )
                if method_sig_match:
                    ret_type = method_sig_match.group(1)
                    if "CompletableFuture" in ret_type:
                        return_type = "CompletableFuture"
                    elif "Future" in ret_type:
                        return_type = "Future"
                break

        return AsyncOperation(
            method_name=method_name,
            class_name=class_name,
            file_path=file_path,
            line_number=annotation_line_idx + 1,
            executor=executor,
            return_type=return_type,
            annotation_text=annotation_text,
            identified_from=[f"{file_path.name}:{annotation_line_idx + 1}"],
        )

    def _parse_scheduled_annotation(
        self, lines: list[str], annotation_line_idx: int, class_name: str, file_path: Path
    ) -> Optional[ScheduledTask]:
        """Parse a @Scheduled annotation and create a ScheduledTask."""
        annotation_text = lines[annotation_line_idx].strip()

        # Handle multi-line annotations
        idx = annotation_line_idx
        paren_count = annotation_text.count("(") - annotation_text.count(")")
        while paren_count > 0 and idx + 1 < len(lines):
            idx += 1
            annotation_text += " " + lines[idx].strip()
            paren_count = annotation_text.count("(") - annotation_text.count(")")

        # Find the method this annotation applies to
        method_name = self._find_annotated_method(lines, idx)
        if not method_name:
            return None

        # Parse schedule configuration
        # Priority: cron > fixedRate > fixedDelay (Spring's precedence)
        schedule_type = ScheduleType.CRON  # Default
        cron_expr = ""
        fixed_rate = -1
        fixed_delay = -1
        initial_delay = -1
        time_unit = "MILLISECONDS"

        # Check for cron expression (highest priority)
        cron_match = self.CRON_PATTERN.search(annotation_text)
        if cron_match:
            cron_expr = cron_match.group(1)
            schedule_type = ScheduleType.CRON
        else:
            # Check for fixed rate (second priority)
            rate_match = self.FIXED_RATE_PATTERN.search(annotation_text)
            if rate_match:
                fixed_rate = int(rate_match.group(1))
                schedule_type = ScheduleType.FIXED_RATE
            else:
                # Check for fixed delay (third priority)
                delay_match = self.FIXED_DELAY_PATTERN.search(annotation_text)
                if delay_match:
                    fixed_delay = int(delay_match.group(1))
                    schedule_type = ScheduleType.FIXED_DELAY

        # Check for initial delay (applies to rate/delay, not cron)
        initial_match = self.INITIAL_DELAY_PATTERN.search(annotation_text)
        if initial_match:
            initial_delay = int(initial_match.group(1))

        # Check for time unit
        unit_match = self.TIME_UNIT_PATTERN.search(annotation_text)
        if unit_match:
            time_unit = unit_match.group(1)

        return ScheduledTask(
            method_name=method_name,
            class_name=class_name,
            file_path=file_path,
            line_number=annotation_line_idx + 1,
            schedule_type=schedule_type,
            cron_expression=cron_expr,
            fixed_rate_ms=fixed_rate,
            fixed_delay_ms=fixed_delay,
            initial_delay_ms=initial_delay,
            time_unit=time_unit,
            annotation_text=annotation_text,
            identified_from=[f"{file_path.name}:{annotation_line_idx + 1}"],
        )

    def _parse_event_listener_annotation(
        self, lines: list[str], annotation_line_idx: int, class_name: str, file_path: Path
    ) -> Optional[EventListener]:
        """Parse an @EventListener or @TransactionalEventListener annotation."""
        annotation_text = lines[annotation_line_idx].strip()

        # Handle multi-line annotations
        idx = annotation_line_idx
        paren_count = annotation_text.count("(") - annotation_text.count(")")
        while paren_count > 0 and idx + 1 < len(lines):
            idx += 1
            annotation_text += " " + lines[idx].strip()
            paren_count = annotation_text.count("(") - annotation_text.count(")")

        # Find the method this annotation applies to
        method_name = self._find_annotated_method(lines, idx)
        if not method_name:
            return None

        # Determine if transactional
        is_transactional = "@TransactionalEventListener" in annotation_text

        # Parse event types from annotation or method parameter
        event_types = []

        # Try to extract event classes from annotation
        classes_match = self.EVENT_CLASSES_PATTERN.search(annotation_text)
        if classes_match:
            classes_str = classes_match.group(1)
            # Extract class names
            event_types = re.findall(r"([A-Z]\w+)\.class", classes_str)
        else:
            # Try to extract from method parameter
            for i in range(idx + 1, min(len(lines), idx + 5)):
                line = lines[i].strip()
                if "(" in line and ")" in line:
                    # Extract parameter type
                    param_match = re.search(r"\(([A-Z]\w+)\s+\w+\)", line)
                    if param_match:
                        event_types.append(param_match.group(1))
                    break

        # Parse condition
        condition = ""
        condition_match = self.EVENT_CONDITION_PATTERN.search(annotation_text)
        if condition_match:
            condition = condition_match.group(1)

        # Parse transaction phase
        phase = ""
        phase_match = self.EVENT_PHASE_PATTERN.search(annotation_text)
        if phase_match:
            phase = phase_match.group(1)

        return EventListener(
            method_name=method_name,
            class_name=class_name,
            file_path=file_path,
            line_number=annotation_line_idx + 1,
            event_types=event_types,
            condition=condition,
            is_transactional=is_transactional,
            phase=phase,
            annotation_text=annotation_text,
            identified_from=[f"{file_path.name}:{annotation_line_idx + 1}"],
        )

    def _detect_state_machine(
        self, content: str, class_name: str, file_path: Path
    ) -> Optional[StateMachine]:
        """Detect state machine pattern in the code."""
        # Look for state enums
        state_enum_match = self.STATE_ENUM_PATTERN.search(content)
        if not state_enum_match:
            return None

        enum_name = state_enum_match.group(1)
        enum_body = state_enum_match.group(2)

        # Extract state names - match any valid Java identifier
        states = re.findall(r"([A-Z][A-Za-z0-9_]*)\s*(?:,|;|\})", enum_body)
        if not states or len(states) < 2:
            return None

        # Look for state field
        state_field = ""
        state_field_match = self.STATE_FIELD_PATTERN.search(content)
        if state_field_match:
            state_field = state_field_match.group(2)

        # Detect state transitions
        transitions = []
        for match in self.STATE_TRANSITION_PATTERN.finditer(content):
            from_state = match.group(1)
            to_state = match.group(2)
            transitions.append(
                StateTransition(from_state=from_state, to_state=to_state, trigger="condition")
            )

        # Only return if we found meaningful transitions
        if not transitions:
            return None

        return StateMachine(
            name=f"{class_name} State Machine",
            class_name=class_name,
            file_path=file_path,
            states=states,
            initial_state=states[0] if states else "",
            state_enum=enum_name,
            state_field=state_field,
            transitions=transitions,
        )

    def _detect_saga_pattern(
        self, content: str, class_name: str, file_path: Path
    ) -> Optional[SagaPattern]:
        """Detect saga pattern with compensating transactions."""
        # Look for methods with compensation
        saga_steps = []

        # Find methods that have corresponding compensation methods
        methods = re.findall(r"public\s+\w+\s+(\w+)\s*\([^)]*\)", content)
        for method in methods:
            # Look for a corresponding compensate/rollback method
            # Use re.escape to prevent regex injection
            escaped_method = re.escape(method)
            compensation_pattern = (
                f"(compensate{escaped_method}|rollback{escaped_method}|undo{escaped_method})"
            )
            if re.search(compensation_pattern, content, re.IGNORECASE):
                saga_steps.append(
                    SagaStep(
                        step_name=method,
                        method_name=method,
                        compensation_method=f"compensate{method}",
                        description=f"Step: {method}",
                    )
                )

        # Only return if we found multiple saga steps (at least 2)
        if len(saga_steps) < 2:
            return None

        # Look for orchestrator method
        orchestrator = ""
        if re.search(r"orchestrate|execute.*saga|run.*saga", content, re.IGNORECASE):
            match = re.search(
                r"public\s+\w+\s+(orchestrate\w+|execute\w+Saga|run\w+Saga)\s*\(",
                content,
                re.IGNORECASE,
            )
            if match:
                orchestrator = match.group(1)

        return SagaPattern(
            name=f"{class_name} Saga",
            class_name=class_name,
            file_path=file_path,
            steps=saga_steps,
            orchestrator_method=orchestrator,
            is_choreography=False,  # Default to orchestration
        )

    def _find_annotated_method(self, lines: list[str], annotation_line_idx: int) -> Optional[str]:
        """Find the method that follows the annotation."""
        # Look for method signature in the next few lines
        for i in range(annotation_line_idx + 1, min(len(lines), annotation_line_idx + 5)):
            line = lines[i].strip()
            # Skip other annotations
            if line.startswith("@"):
                continue
            # Skip empty lines
            if not line:
                continue
            # Try to match method signature
            match = self.METHOD_PATTERN.search(line)
            if match:
                return match.group(1)
        return None

    def _identify_workflow_patterns(self) -> list[WorkflowPattern]:
        """Identify high-level workflow patterns from detected components."""
        patterns = []

        # Pattern: Async processing workflows
        if self._async_operations:
            async_workflow = WorkflowPattern(
                pattern_type=WorkflowType.ASYNC,
                name="Asynchronous Processing",
                description=f"Detected {len(self._async_operations)} async operations",
                async_operations=self._async_operations,
                recommendation="Ensure proper error handling and monitoring for async operations",
                complexity_score=2,
            )
            patterns.append(async_workflow)

        # Pattern: Scheduled job workflows
        if self._scheduled_tasks:
            scheduled_workflow = WorkflowPattern(
                pattern_type=WorkflowType.SCHEDULED,
                name="Scheduled Tasks",
                description=f"Detected {len(self._scheduled_tasks)} scheduled background jobs",
                scheduled_tasks=self._scheduled_tasks,
                recommendation="Monitor scheduled task execution and ensure idempotency",
                complexity_score=2,
            )
            patterns.append(scheduled_workflow)

        # Pattern: Event-driven workflows
        if self._event_listeners:
            event_workflow = WorkflowPattern(
                pattern_type=WorkflowType.EVENT_DRIVEN,
                name="Event-Driven Processing",
                description=f"Detected {len(self._event_listeners)} event listeners",
                event_listeners=self._event_listeners,
                recommendation="Ensure event ordering and idempotency for event handlers",
                complexity_score=3,
            )
            patterns.append(event_workflow)

        # Pattern: State machine workflows
        for state_machine in self._state_machines:
            sm_workflow = WorkflowPattern(
                pattern_type=WorkflowType.STATE_MACHINE,
                name=state_machine.name,
                description=f"State machine with {len(state_machine.states)} states",
                class_name=state_machine.class_name,
                file_path=state_machine.file_path,
                state_machine=state_machine,
                recommendation="Document state transitions and ensure transition validation",
                complexity_score=4,
            )
            patterns.append(sm_workflow)

        # Pattern: Saga workflows
        for saga in self._saga_patterns:
            saga_workflow = WorkflowPattern(
                pattern_type=WorkflowType.SAGA,
                name=saga.name,
                description=f"Saga pattern with {len(saga.steps)} steps",
                class_name=saga.class_name,
                file_path=saga.file_path,
                saga=saga,
                recommendation="Ensure compensation logic handles partial failures correctly",
                complexity_score=5,
            )
            patterns.append(saga_workflow)

        return patterns

    def get_async_operations(self) -> list[AsyncOperation]:
        """Get all detected async operations."""
        return self._async_operations

    def get_scheduled_tasks(self) -> list[ScheduledTask]:
        """Get all detected scheduled tasks."""
        return self._scheduled_tasks

    def get_event_listeners(self) -> list[EventListener]:
        """Get all detected event listeners."""
        return self._event_listeners

    def get_transactional_event_listeners(self) -> list[EventListener]:
        """Get event listeners that are transactional."""
        return [listener for listener in self._event_listeners if listener.is_transactional]

    def get_state_machines(self) -> list[StateMachine]:
        """Get all detected state machines."""
        return self._state_machines

    def get_saga_patterns(self) -> list[SagaPattern]:
        """Get all detected saga patterns."""
        return self._saga_patterns

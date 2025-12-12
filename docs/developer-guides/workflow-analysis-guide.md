# Workflow Pattern Analysis Guide

## Overview

The Workflow Pattern Analysis feature (ENH-ANAL-004) provides comprehensive detection and documentation of multi-step business workflows in Java Spring applications. This guide explains how to use the `WorkflowAnalyzer` to identify complex workflow patterns including async operations, scheduled tasks, event-driven flows, state machines, and saga patterns.

## Supported Workflow Patterns

### 1. Async Operations (`@Async`)

Detects asynchronous operations that run in separate threads.

**Example:**
```java
@Async
public void sendEmailNotification(String email, String message) {
    emailClient.send(email, message);
}

@Async("customExecutor")
public CompletableFuture<String> fetchDataAsync(Long id) {
    return CompletableFuture.completedFuture(dataService.fetch(id));
}
```

**Detection includes:**
- Custom executor names
- Return types (void, Future, CompletableFuture)
- Fire-and-forget vs awaitable operations

### 2. Scheduled Tasks (`@Scheduled`)

Detects background jobs with various scheduling configurations.

**Example:**
```java
@Scheduled(cron = "0 0 * * * *")
public void runHourly() {
    cleanupService.cleanup();
}

@Scheduled(fixedRate = 5000, initialDelay = 1000)
public void healthCheck() {
    monitor.ping();
}

@Scheduled(fixedDelay = 10000, timeUnit = TimeUnit.SECONDS)
public void processQueue() {
    queue.process();
}
```

**Detection includes:**
- Cron expressions
- Fixed rate execution
- Fixed delay between executions
- Initial delay configuration
- Time units

### 3. Event-Driven Workflows

Detects event listeners for event-driven architectures.

**Example:**
```java
@EventListener
public void handleOrderCreated(OrderCreatedEvent event) {
    notificationService.sendConfirmation(event.getOrderId());
}

@EventListener(condition = "#event.amount > 1000")
public void handleLargeOrder(OrderEvent event) {
    fraudDetection.check(event);
}

@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void handleAfterCommit(PaymentProcessedEvent event) {
    inventoryService.updateStock(event.getProductId());
}
```

**Detection includes:**
- Event types/classes
- Conditional listeners (SpEL expressions)
- Transaction phases (AFTER_COMMIT, AFTER_ROLLBACK, etc.)
- Distinction between regular and transactional listeners

### 4. State Machine Patterns

Detects state machine implementations with enum-based states.

**Example:**
```java
public enum OrderState {
    CREATED, PAYMENT_PENDING, PAID, SHIPPED, DELIVERED, CANCELLED
}

private OrderState currentState;

public void confirmPayment() {
    if (currentState == OrderState.PAYMENT_PENDING) {
        currentState = OrderState.PAID;
    }
}
```

**Detection includes:**
- State enumeration
- State transitions
- Current state fields

### 5. Saga Patterns

Detects saga patterns with compensating transactions for distributed workflows.

**Example:**
```java
public void orchestrateOrder(OrderRequest request) {
    try {
        reserveInventory(request);
        processPayment(request);
        createShipment(request);
    } catch (Exception e) {
        compensateOrder(request);
    }
}

public void reserveInventory(OrderRequest request) {
    inventoryService.reserve(request.getItems());
}

public void compensateReserveInventory(OrderRequest request) {
    inventoryService.release(request.getItems());
}
```

**Detection includes:**
- Saga steps
- Compensating transaction methods
- Orchestration methods

## Usage

### Basic Usage

```python
from pathlib import Path
from reverse_engineer.analysis.workflow import WorkflowAnalyzer

# Initialize analyzer
repo_root = Path("/path/to/spring/project")
analyzer = WorkflowAnalyzer(repo_root, verbose=True)

# Run analysis
result = analyzer.analyze()

# Access results
print(f"Found {result.total_async_ops} async operations")
print(f"Found {result.total_scheduled_tasks} scheduled tasks")
print(f"Found {result.total_event_listeners} event listeners")
print(f"Found {result.total_state_machines} state machines")
print(f"Found {result.total_sagas} saga patterns")

# Get complexity summary
print(result.complexity_summary)
```

### Accessing Specific Patterns

```python
# Get async operations
async_ops = analyzer.get_async_operations()
for op in async_ops:
    print(f"{op.class_name}.{op.method_name}")
    print(f"  Executor: {op.executor}")
    print(f"  Is fire-and-forget: {op.is_fire_and_forget}")

# Get scheduled tasks
scheduled_tasks = analyzer.get_scheduled_tasks()
for task in scheduled_tasks:
    print(f"{task.class_name}.{task.method_name}")
    print(f"  Schedule: {task.schedule_description}")

# Get event listeners
listeners = analyzer.get_event_listeners()
for listener in listeners:
    print(f"{listener.class_name}.{listener.method_name}")
    print(f"  Events: {', '.join(listener.event_types)}")
    print(f"  Transactional: {listener.is_transactional}")
    if listener.is_conditional:
        print(f"  Condition: {listener.condition}")

# Get only transactional event listeners
transactional_listeners = analyzer.get_transactional_event_listeners()

# Get state machines
state_machines = analyzer.get_state_machines()
for sm in state_machines:
    print(f"{sm.name}")
    print(f"  States: {', '.join(sm.states)}")
    print(f"  Transitions: {sm.transition_count}")

# Get saga patterns
sagas = analyzer.get_saga_patterns()
for saga in sagas:
    print(f"{saga.name}")
    print(f"  Steps: {saga.step_count}")
    print(f"  Has compensation: {saga.has_compensation}")
```

### Workflow Patterns

The analyzer also identifies high-level workflow patterns:

```python
for pattern in result.workflow_patterns:
    print(f"Pattern: {pattern.name}")
    print(f"Type: {pattern.pattern_type}")
    print(f"Description: {pattern.description}")
    print(f"Complexity: {pattern.complexity_score}/5")
    print(f"Recommendation: {pattern.recommendation}")
```

## Domain Models

### WorkflowType Enum

```python
class WorkflowType(Enum):
    ASYNC = "async"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    STATE_MACHINE = "state_machine"
    SAGA = "saga"
    ORCHESTRATION = "orchestration"
```

### ScheduleType Enum

```python
class ScheduleType(Enum):
    CRON = "cron"
    FIXED_RATE = "fixed_rate"
    FIXED_DELAY = "fixed_delay"
    INITIAL_DELAY = "initial_delay"
```

### AsyncOperation

```python
@dataclass
class AsyncOperation:
    method_name: str
    class_name: str
    file_path: Optional[Path]
    line_number: int
    executor: str  # Default: "default"
    return_type: str  # "void", "Future", "CompletableFuture"
    annotation_text: str
    identified_from: list[str]
    
    @property
    def is_fire_and_forget(self) -> bool:
        """Returns True if return_type is 'void'"""
```

### ScheduledTask

```python
@dataclass
class ScheduledTask:
    method_name: str
    class_name: str
    file_path: Optional[Path]
    line_number: int
    schedule_type: ScheduleType
    cron_expression: str
    fixed_rate_ms: int
    fixed_delay_ms: int
    initial_delay_ms: int
    time_unit: str
    annotation_text: str
    identified_from: list[str]
    
    @property
    def schedule_description(self) -> str:
        """Returns human-readable schedule description"""
```

### EventListener

```python
@dataclass
class EventListener:
    method_name: str
    class_name: str
    file_path: Optional[Path]
    line_number: int
    event_types: list[str]
    condition: str  # SpEL expression
    is_transactional: bool
    phase: str  # Transaction phase
    annotation_text: str
    identified_from: list[str]
    
    @property
    def is_conditional(self) -> bool:
        """Returns True if listener has a condition"""
```

### StateMachine

```python
@dataclass
class StateMachine:
    name: str
    class_name: str
    file_path: Optional[Path]
    states: list[str]
    initial_state: str
    final_states: list[str]
    transitions: list[StateTransition]
    state_enum: str
    state_field: str
    
    @property
    def transition_count(self) -> int:
        """Returns number of transitions"""
```

### SagaPattern

```python
@dataclass
class SagaPattern:
    name: str
    class_name: str
    file_path: Optional[Path]
    steps: list[SagaStep]
    orchestrator_method: str
    is_choreography: bool
    compensation_strategy: str
    
    @property
    def step_count(self) -> int:
        """Returns number of steps"""
    
    @property
    def has_compensation(self) -> bool:
        """Returns True if saga has compensation logic"""
```

### WorkflowAnalysisResult

```python
@dataclass
class WorkflowAnalysisResult:
    project_name: str
    async_operations: list[AsyncOperation]
    scheduled_tasks: list[ScheduledTask]
    event_listeners: list[EventListener]
    state_machines: list[StateMachine]
    saga_patterns: list[SagaPattern]
    workflow_patterns: list[WorkflowPattern]
    
    # Statistics (computed)
    total_async_ops: int
    total_scheduled_tasks: int
    total_event_listeners: int
    transactional_listeners_count: int
    total_state_machines: int
    total_sagas: int
    total_workflows: int
    
    def compute_statistics(self) -> None:
        """Computes all statistics from detected patterns"""
    
    @property
    def has_async_patterns(self) -> bool
    
    @property
    def has_scheduled_patterns(self) -> bool
    
    @property
    def has_event_driven_patterns(self) -> bool
    
    @property
    def complexity_summary(self) -> str:
        """Returns summary like: '2 async, 3 scheduled, 5 event-driven'"""
```

## Integration with Other Analyzers

The WorkflowAnalyzer complements other analysis components:

### With TransactionAnalyzer

Combine workflow and transaction analysis for complete picture:

```python
from reverse_engineer.analysis import WorkflowAnalyzer, TransactionAnalyzer

workflow_result = WorkflowAnalyzer(repo_root).analyze()
transaction_result = TransactionAnalyzer(repo_root).analyze()

# Correlate async operations with transactions
for async_op in workflow_result.async_operations:
    matching_txn = next(
        (t for t in transaction_result.boundaries 
         if t.class_name == async_op.class_name 
         and t.method_name == async_op.method_name),
        None
    )
    if matching_txn:
        print(f"{async_op.method_name} is both async and transactional")
```

### With BusinessProcessIdentifier

Workflow patterns enhance use case quality:

```python
from reverse_engineer.analysis import WorkflowAnalyzer
from reverse_engineer.analyzer import BusinessProcessIdentifier

workflow_result = WorkflowAnalyzer(repo_root).analyze()
bp_identifier = BusinessProcessIdentifier(verbose=True)

# Use workflow information to enhance use cases
if workflow_result.has_async_patterns:
    print("Use cases should document async behavior")
if workflow_result.has_event_driven_patterns:
    print("Use cases should document event flows")
```

## Testing

The workflow analyzer includes comprehensive tests:

```bash
# Run all workflow analyzer tests
python3 -m unittest tests.analysis.test_workflow_analyzer -v

# Run specific test class
python3 -m unittest tests.analysis.test_workflow_analyzer.TestAsyncDetection -v
python3 -m unittest tests.analysis.test_workflow_analyzer.TestScheduledDetection -v
python3 -m unittest tests.analysis.test_workflow_analyzer.TestEventListenerDetection -v
python3 -m unittest tests.analysis.test_workflow_analyzer.TestStateMachineDetection -v
python3 -m unittest tests.analysis.test_workflow_analyzer.TestSagaDetection -v
```

## Best Practices

### 1. Use Verbose Mode for Debugging

```python
analyzer = WorkflowAnalyzer(repo_root, verbose=True)
result = analyzer.analyze()
```

This provides detailed progress information during analysis.

### 2. Check for Specific Patterns

Before processing results, check if patterns exist:

```python
result = analyzer.analyze()

if result.has_async_patterns:
    # Handle async operations
    pass

if result.has_event_driven_patterns:
    # Handle event listeners
    pass
```

### 3. Use Complexity Score

Workflow patterns have a complexity score (1-5):

```python
for pattern in result.workflow_patterns:
    if pattern.complexity_score >= 4:
        print(f"High complexity workflow: {pattern.name}")
        print(f"Recommendation: {pattern.recommendation}")
```

### 4. Handle Empty Results

Always handle cases where no patterns are found:

```python
result = analyzer.analyze()

if result.total_workflows == 0:
    print("No workflow patterns detected")
else:
    print(f"Found {result.total_workflows} workflow patterns")
    print(result.complexity_summary)
```

## Limitations

1. **Java Spring Only**: Currently supports Java Spring Framework annotations only
2. **Pattern Matching**: Uses regex-based pattern matching; may miss complex implementations
3. **State Machines**: Detects enum-based state machines; may not detect library-based implementations
4. **Saga Detection**: Requires naming convention (compensate*/rollback*/undo* methods)

## Future Enhancements

Potential improvements include:

- Support for other frameworks (.NET, Node.js, Python)
- Detection of workflow orchestration libraries (Camunda, Temporal)
- Call graph analysis for workflow steps
- Performance impact analysis
- Workflow visualization generation

## Related Documentation

- [Transaction Analysis Guide](./transaction-analysis-guide.md)
- [Business Process Identification](./business-process-guide.md)
- [Framework Support](../frameworks/README.md)

## Support

For issues or questions:
- Check the test files for examples: `tests/analysis/test_workflow_analyzer.py`
- Review domain models: `reverse_engineer/domain/workflow.py`
- See analyzer implementation: `reverse_engineer/analysis/workflow/workflow_analyzer.py`

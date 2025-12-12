"""
Tests for WorkflowAnalyzer - Detects and documents multi-step workflow patterns.

Tests cover:
- @Async annotation detection
- @Scheduled task detection with various schedule types
- @EventListener and @TransactionalEventListener detection
- State machine pattern detection
- Saga pattern detection
- Workflow pattern identification
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from reverse_engineer.analysis.workflow import WorkflowAnalyzer
from reverse_engineer.domain import (
    AsyncOperation,
    EventListener,
    ScheduledTask,
    ScheduleType,
    WorkflowAnalysisResult,
    WorkflowType,
)


class TestWorkflowAnalyzerInit(unittest.TestCase):
    """Test WorkflowAnalyzer initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_init_basic(self):
        """Test basic initialization."""
        analyzer = WorkflowAnalyzer(self.repo_root)

        self.assertEqual(analyzer.repo_root, self.repo_root)
        self.assertFalse(analyzer.verbose)
        self.assertEqual(analyzer._async_operations, [])
        self.assertEqual(analyzer._scheduled_tasks, [])
        self.assertEqual(analyzer._event_listeners, [])

    def test_init_verbose(self):
        """Test initialization with verbose mode."""
        analyzer = WorkflowAnalyzer(self.repo_root, verbose=True)

        self.assertTrue(analyzer.verbose)


class TestAsyncDetection(unittest.TestCase):
    """Test @Async annotation detection."""

    def setUp(self):
        """Set up test fixtures with sample Java files."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example/service"
        self.service_dir.mkdir(parents=True)

        # Sample service with async operations
        self.sample_service = '''
package com.example.service;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import java.util.concurrent.CompletableFuture;

@Service
public class NotificationService {

    @Async
    public void sendEmailNotification(String email, String message) {
        // Fire-and-forget async operation
        emailClient.send(email, message);
    }

    @Async("customExecutor")
    public void processInBackground(String data) {
        // Async with custom executor
        processor.process(data);
    }

    @Async
    public CompletableFuture<String> fetchDataAsync(Long id) {
        // Async operation that returns a future
        return CompletableFuture.completedFuture(dataService.fetch(id));
    }
}
'''
        (self.service_dir / "NotificationService.java").write_text(self.sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_async_annotations(self):
        """Test detection of @Async annotations."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertIsInstance(result, WorkflowAnalysisResult)
        self.assertGreater(result.total_async_ops, 0)

    def test_detect_fire_and_forget_async(self):
        """Test detection of fire-and-forget async operation."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        send_email = next(
            (op for op in result.async_operations if op.method_name == "sendEmailNotification"),
            None,
        )
        self.assertIsNotNone(send_email)
        self.assertTrue(send_email.is_fire_and_forget)
        self.assertEqual(send_email.executor, "default")

    def test_detect_async_with_custom_executor(self):
        """Test detection of async with custom executor."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        process_bg = next(
            (op for op in result.async_operations if op.method_name == "processInBackground"),
            None,
        )
        self.assertIsNotNone(process_bg)
        self.assertEqual(process_bg.executor, "customExecutor")

    def test_detect_async_with_future(self):
        """Test detection of async operation with CompletableFuture."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        fetch_data = next(
            (op for op in result.async_operations if op.method_name == "fetchDataAsync"),
            None,
        )
        self.assertIsNotNone(fetch_data)
        self.assertFalse(fetch_data.is_fire_and_forget)
        self.assertEqual(fetch_data.return_type, "CompletableFuture")


class TestScheduledDetection(unittest.TestCase):
    """Test @Scheduled task detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example/scheduler"
        self.service_dir.mkdir(parents=True)

        # Sample service with scheduled tasks
        self.sample_service = '''
package com.example.scheduler;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import java.util.concurrent.TimeUnit;

@Component
public class ScheduledTasks {

    @Scheduled(cron = "0 0 * * * *")
    public void runHourly() {
        // Runs every hour
        cleanupService.cleanup();
    }

    @Scheduled(fixedRate = 5000)
    public void runEveryFiveSeconds() {
        // Runs every 5 seconds
        healthCheck.ping();
    }

    @Scheduled(fixedDelay = 10000)
    public void runWithDelay() {
        // Waits 10 seconds after completion
        processor.process();
    }

    @Scheduled(
        fixedRate = 60,
        initialDelay = 30,
        timeUnit = TimeUnit.SECONDS
    )
    public void runWithInitialDelay() {
        // Starts after 30 seconds, then every 60 seconds
        reporter.report();
    }

    @Scheduled(cron = "0 0 0 * * SUN")
    public void runWeekly() {
        // Runs every Sunday at midnight
        weeklyReport.generate();
    }
}
'''
        (self.service_dir / "ScheduledTasks.java").write_text(self.sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_scheduled_annotations(self):
        """Test detection of @Scheduled annotations."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertGreater(result.total_scheduled_tasks, 0)

    def test_detect_cron_schedule(self):
        """Test detection of cron-based schedule."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        hourly = next(
            (task for task in result.scheduled_tasks if task.method_name == "runHourly"),
            None,
        )
        self.assertIsNotNone(hourly)
        self.assertEqual(hourly.schedule_type, ScheduleType.CRON)
        self.assertEqual(hourly.cron_expression, "0 0 * * * *")

    def test_detect_fixed_rate_schedule(self):
        """Test detection of fixed rate schedule."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        every_five = next(
            (task for task in result.scheduled_tasks if task.method_name == "runEveryFiveSeconds"),
            None,
        )
        self.assertIsNotNone(every_five)
        self.assertEqual(every_five.schedule_type, ScheduleType.FIXED_RATE)
        self.assertEqual(every_five.fixed_rate_ms, 5000)

    def test_detect_fixed_delay_schedule(self):
        """Test detection of fixed delay schedule."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        with_delay = next(
            (task for task in result.scheduled_tasks if task.method_name == "runWithDelay"),
            None,
        )
        self.assertIsNotNone(with_delay)
        self.assertEqual(with_delay.schedule_type, ScheduleType.FIXED_DELAY)
        self.assertEqual(with_delay.fixed_delay_ms, 10000)

    def test_detect_initial_delay(self):
        """Test detection of initial delay."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        with_initial = next(
            (task for task in result.scheduled_tasks if task.method_name == "runWithInitialDelay"),
            None,
        )
        self.assertIsNotNone(with_initial)
        self.assertEqual(with_initial.initial_delay_ms, 30)
        self.assertEqual(with_initial.time_unit, "SECONDS")

    def test_schedule_description(self):
        """Test schedule description property."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        hourly = next(
            (task for task in result.scheduled_tasks if task.method_name == "runHourly"),
            None,
        )
        self.assertIsNotNone(hourly)
        self.assertIn("Cron", hourly.schedule_description)
        self.assertIn("0 0 * * * *", hourly.schedule_description)


class TestEventListenerDetection(unittest.TestCase):
    """Test event listener detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example/events"
        self.service_dir.mkdir(parents=True)

        # Sample service with event listeners
        self.sample_service = '''
package com.example.events;

import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.event.TransactionPhase;
import org.springframework.transaction.event.TransactionalEventListener;

@Component
public class OrderEventHandler {

    @EventListener
    public void handleOrderCreated(OrderCreatedEvent event) {
        // Handle order created event
        notificationService.sendConfirmation(event.getOrderId());
    }

    @EventListener(classes = {UserRegisteredEvent.class})
    public void onUserRegistered(UserRegisteredEvent event) {
        // Handle user registration
        welcomeEmail.send(event.getUserEmail());
    }

    @EventListener(condition = "#event.amount > 1000")
    public void handleLargeOrder(OrderEvent event) {
        // Only handle large orders
        fraudDetection.check(event);
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleAfterCommit(PaymentProcessedEvent event) {
        // Execute after transaction commits
        inventoryService.updateStock(event.getProductId());
    }

    @TransactionalEventListener(phase = TransactionPhase.AFTER_ROLLBACK)
    public void handleRollback(PaymentFailedEvent event) {
        // Execute after transaction rolls back
        alertService.notifyFailure(event);
    }
}
'''
        (self.service_dir / "OrderEventHandler.java").write_text(self.sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_event_listeners(self):
        """Test detection of @EventListener annotations."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertGreater(result.total_event_listeners, 0)

    def test_detect_simple_event_listener(self):
        """Test detection of simple event listener."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        order_created = next(
            (l for l in result.event_listeners if l.method_name == "handleOrderCreated"),
            None,
        )
        self.assertIsNotNone(order_created)
        self.assertFalse(order_created.is_transactional)
        self.assertIn("OrderCreatedEvent", order_created.event_types)

    def test_detect_event_listener_with_classes(self):
        """Test detection of event listener with classes attribute."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        user_reg = next(
            (l for l in result.event_listeners if l.method_name == "onUserRegistered"),
            None,
        )
        self.assertIsNotNone(user_reg)
        self.assertIn("UserRegisteredEvent", user_reg.event_types)

    def test_detect_conditional_event_listener(self):
        """Test detection of event listener with condition."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        large_order = next(
            (l for l in result.event_listeners if l.method_name == "handleLargeOrder"),
            None,
        )
        self.assertIsNotNone(large_order)
        self.assertTrue(large_order.is_conditional)
        self.assertIn("1000", large_order.condition)

    def test_detect_transactional_event_listener(self):
        """Test detection of @TransactionalEventListener."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        after_commit = next(
            (l for l in result.event_listeners if l.method_name == "handleAfterCommit"),
            None,
        )
        self.assertIsNotNone(after_commit)
        self.assertTrue(after_commit.is_transactional)
        self.assertEqual(after_commit.phase, "AFTER_COMMIT")

    def test_detect_rollback_event_listener(self):
        """Test detection of rollback event listener."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        rollback = next(
            (l for l in result.event_listeners if l.method_name == "handleRollback"),
            None,
        )
        self.assertIsNotNone(rollback)
        self.assertTrue(rollback.is_transactional)
        self.assertEqual(rollback.phase, "AFTER_ROLLBACK")

    def test_transactional_listeners_count(self):
        """Test counting of transactional event listeners."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertGreater(result.transactional_listeners_count, 0)


class TestStateMachineDetection(unittest.TestCase):
    """Test state machine pattern detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example/order"
        self.service_dir.mkdir(parents=True)

        # Sample service with state machine
        self.sample_service = '''
package com.example.order;

import org.springframework.stereotype.Service;

@Service
public class OrderStateMachine {

    public enum OrderState {
        CREATED,
        PAYMENT_PENDING,
        PAID,
        SHIPPED,
        DELIVERED,
        CANCELLED
    }

    private OrderState currentState;

    public void processPayment() {
        if (currentState == OrderState.CREATED) {
            currentState = OrderState.PAYMENT_PENDING;
        }
    }

    public void confirmPayment() {
        if (currentState == OrderState.PAYMENT_PENDING) {
            currentState = OrderState.PAID;
        }
    }

    public void ship() {
        if (currentState == OrderState.PAID) {
            currentState = OrderState.SHIPPED;
        }
    }

    public void deliver() {
        if (currentState == OrderState.SHIPPED) {
            currentState = OrderState.DELIVERED;
        }
    }

    public void cancel() {
        if (currentState == OrderState.CREATED || currentState == OrderState.PAYMENT_PENDING) {
            currentState = OrderState.CANCELLED;
        }
    }
}
'''
        (self.service_dir / "OrderStateMachine.java").write_text(self.sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_state_machine(self):
        """Test detection of state machine pattern."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertGreater(result.total_state_machines, 0)

    def test_state_machine_details(self):
        """Test state machine details."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        state_machine = result.state_machines[0]
        self.assertEqual(state_machine.state_enum, "OrderState")
        self.assertGreater(len(state_machine.states), 2)
        self.assertIn("CREATED", state_machine.states)
        self.assertIn("DELIVERED", state_machine.states)

    def test_state_transitions(self):
        """Test state transition detection."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        state_machine = result.state_machines[0]
        self.assertGreater(state_machine.transition_count, 0)


class TestSagaDetection(unittest.TestCase):
    """Test saga pattern detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example/saga"
        self.service_dir.mkdir(parents=True)

        # Sample service with saga pattern
        self.sample_service = '''
package com.example.saga;

import org.springframework.stereotype.Service;

@Service
public class OrderSaga {

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

    public void processPayment(OrderRequest request) {
        paymentService.charge(request.getAmount());
    }

    public void compensateProcessPayment(OrderRequest request) {
        paymentService.refund(request.getAmount());
    }

    public void createShipment(OrderRequest request) {
        shippingService.ship(request.getAddress());
    }

    public void compensateCreateShipment(OrderRequest request) {
        shippingService.cancel(request.getShipmentId());
    }

    private void compensateOrder(OrderRequest request) {
        compensateCreateShipment(request);
        compensateProcessPayment(request);
        compensateReserveInventory(request);
    }
}
'''
        (self.service_dir / "OrderSaga.java").write_text(self.sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_saga_pattern(self):
        """Test detection of saga pattern."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertGreater(result.total_sagas, 0)

    def test_saga_steps(self):
        """Test saga step detection."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        saga = result.saga_patterns[0]
        self.assertGreaterEqual(saga.step_count, 2)
        self.assertTrue(saga.has_compensation)

    def test_saga_orchestrator(self):
        """Test saga orchestrator detection."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        saga = result.saga_patterns[0]
        self.assertTrue(saga.orchestrator_method)


class TestWorkflowPatternIdentification(unittest.TestCase):
    """Test high-level workflow pattern identification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example"
        self.service_dir.mkdir(parents=True)

        # Create various workflow patterns
        async_service = '''
package com.example;
import org.springframework.scheduling.annotation.Async;

public class AsyncService {
    @Async
    public void asyncMethod() {}
}
'''
        (self.service_dir / "AsyncService.java").write_text(async_service)

        scheduled_service = '''
package com.example;
import org.springframework.scheduling.annotation.Scheduled;

public class ScheduledService {
    @Scheduled(cron = "0 0 * * * *")
    public void scheduledMethod() {}
}
'''
        (self.service_dir / "ScheduledService.java").write_text(scheduled_service)

        event_service = '''
package com.example;
import org.springframework.context.event.EventListener;

public class EventService {
    @EventListener
    public void handleEvent(MyEvent event) {}
}
'''
        (self.service_dir / "EventService.java").write_text(event_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_identify_async_workflow_pattern(self):
        """Test identification of async workflow pattern."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        async_pattern = next(
            (p for p in result.workflow_patterns if p.pattern_type == WorkflowType.ASYNC),
            None,
        )
        self.assertIsNotNone(async_pattern)
        self.assertGreater(len(async_pattern.async_operations), 0)

    def test_identify_scheduled_workflow_pattern(self):
        """Test identification of scheduled workflow pattern."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        scheduled_pattern = next(
            (p for p in result.workflow_patterns if p.pattern_type == WorkflowType.SCHEDULED),
            None,
        )
        self.assertIsNotNone(scheduled_pattern)
        self.assertGreater(len(scheduled_pattern.scheduled_tasks), 0)

    def test_identify_event_driven_workflow_pattern(self):
        """Test identification of event-driven workflow pattern."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        event_pattern = next(
            (p for p in result.workflow_patterns if p.pattern_type == WorkflowType.EVENT_DRIVEN),
            None,
        )
        self.assertIsNotNone(event_pattern)
        self.assertGreater(len(event_pattern.event_listeners), 0)


class TestWorkflowAnalysisResultModel(unittest.TestCase):
    """Test WorkflowAnalysisResult domain model."""

    def test_compute_statistics(self):
        """Test compute_statistics method."""
        result = WorkflowAnalysisResult(
            project_name="test-project",
            async_operations=[
                AsyncOperation(method_name="m1", class_name="C1"),
                AsyncOperation(method_name="m2", class_name="C2"),
            ],
            scheduled_tasks=[ScheduledTask(method_name="s1", class_name="C3")],
            event_listeners=[
                EventListener(method_name="e1", class_name="C4", is_transactional=True),
                EventListener(method_name="e2", class_name="C5", is_transactional=False),
            ],
        )

        result.compute_statistics()

        self.assertEqual(result.total_async_ops, 2)
        self.assertEqual(result.total_scheduled_tasks, 1)
        self.assertEqual(result.total_event_listeners, 2)
        self.assertEqual(result.transactional_listeners_count, 1)

    def test_has_pattern_properties(self):
        """Test pattern detection properties."""
        result = WorkflowAnalysisResult(
            async_operations=[AsyncOperation(method_name="m1", class_name="C1")],
            scheduled_tasks=[ScheduledTask(method_name="s1", class_name="C2")],
            event_listeners=[EventListener(method_name="e1", class_name="C3")],
        )
        result.compute_statistics()

        self.assertTrue(result.has_async_patterns)
        self.assertTrue(result.has_scheduled_patterns)
        self.assertTrue(result.has_event_driven_patterns)

    def test_complexity_summary(self):
        """Test complexity summary generation."""
        result = WorkflowAnalysisResult(
            async_operations=[AsyncOperation(method_name="m1", class_name="C1")],
            scheduled_tasks=[ScheduledTask(method_name="s1", class_name="C2")],
        )
        result.compute_statistics()

        summary = result.complexity_summary
        self.assertIn("1 async", summary)
        self.assertIn("1 scheduled", summary)


class TestEmptyRepository(unittest.TestCase):
    """Test behavior with empty repository."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_analyze_empty_repo(self):
        """Test analysis of empty repository."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertEqual(result.total_async_ops, 0)
        self.assertEqual(result.total_scheduled_tasks, 0)
        self.assertEqual(result.total_event_listeners, 0)

    def test_analyze_repo_without_workflows(self):
        """Test analysis of repo without workflow annotations."""
        service_dir = self.repo_root / "src/main/java/com/example"
        service_dir.mkdir(parents=True)

        simple_service = '''
package com.example;

public class SimpleService {
    public void doSomething() {}
}
'''
        (service_dir / "SimpleService.java").write_text(simple_service)

        analyzer = WorkflowAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertEqual(result.total_async_ops, 0)
        self.assertEqual(result.total_workflows, 0)


class TestFilterMethods(unittest.TestCase):
    """Test filter methods for workflow components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        self.service_dir = self.repo_root / "src/main/java/com/example"
        self.service_dir.mkdir(parents=True)

        sample_service = '''
package com.example;

import org.springframework.scheduling.annotation.Async;
import org.springframework.context.event.EventListener;
import org.springframework.transaction.event.TransactionalEventListener;

public class MixedService {
    @Async
    public void asyncOp() {}

    @EventListener
    public void normalEvent(Event e) {}

    @TransactionalEventListener
    public void transactionalEvent(Event e) {}
}
'''
        (self.service_dir / "MixedService.java").write_text(sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_get_async_operations(self):
        """Test getting async operations."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        analyzer.analyze()

        async_ops = analyzer.get_async_operations()
        self.assertEqual(len(async_ops), 1)
        self.assertEqual(async_ops[0].method_name, "asyncOp")

    def test_get_event_listeners(self):
        """Test getting all event listeners."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        analyzer.analyze()

        listeners = analyzer.get_event_listeners()
        self.assertEqual(len(listeners), 2)

    def test_get_transactional_event_listeners(self):
        """Test filtering transactional event listeners."""
        analyzer = WorkflowAnalyzer(self.repo_root)
        analyzer.analyze()

        transactional = analyzer.get_transactional_event_listeners()
        self.assertEqual(len(transactional), 1)
        self.assertEqual(transactional[0].method_name, "transactionalEvent")


if __name__ == "__main__":
    unittest.main()

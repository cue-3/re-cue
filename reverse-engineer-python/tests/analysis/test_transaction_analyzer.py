"""
Tests for TransactionAnalyzer - Detects and documents transaction boundaries.

Tests cover:
- @Transactional annotation detection
- Transaction propagation patterns
- Read-only vs write transaction classification
- Nested transaction detection
- Rollback scenario identification
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from reverse_engineer.analysis.transaction import TransactionAnalyzer
from reverse_engineer.domain import (
    TransactionAnalysisResult,
    TransactionBoundary,
    TransactionIsolation,
    TransactionPropagation,
)


class TestTransactionAnalyzerInit(unittest.TestCase):
    """Test TransactionAnalyzer initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_init_basic(self):
        """Test basic initialization."""
        analyzer = TransactionAnalyzer(self.repo_root)

        self.assertEqual(analyzer.repo_root, self.repo_root)
        self.assertFalse(analyzer.verbose)
        self.assertEqual(analyzer._boundaries, [])
        self.assertEqual(analyzer._nested_transactions, [])

    def test_init_verbose(self):
        """Test initialization with verbose mode."""
        analyzer = TransactionAnalyzer(self.repo_root, verbose=True)

        self.assertTrue(analyzer.verbose)


class TestTransactionAnnotationParsing(unittest.TestCase):
    """Test @Transactional annotation parsing."""

    def setUp(self):
        """Set up test fixtures with sample Java files."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Create sample Java service with transactions
        self.service_dir = self.repo_root / "src/main/java/com/example/service"
        self.service_dir.mkdir(parents=True)

        # Sample service with various @Transactional annotations
        self.sample_service = '''
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Isolation;

@Service
public class UserService {

    @Transactional
    public void createUser(String name) {
        // Creates a user with default transaction settings
    }

    @Transactional(readOnly = true)
    public User getUser(Long id) {
        // Read-only transaction
        return null;
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void sendNotification(String message) {
        // Runs in a new independent transaction
    }

    @Transactional(
        propagation = Propagation.REQUIRED,
        isolation = Isolation.SERIALIZABLE,
        timeout = 30
    )
    public void transferMoney(Long from, Long to, Double amount) {
        // Complex transaction with isolation and timeout
    }

    @Transactional(rollbackFor = {RuntimeException.class, SQLException.class})
    public void processPayment(Payment payment) {
        // Transaction with custom rollback rules
    }

    @Transactional(noRollbackFor = IllegalArgumentException.class)
    public void validateInput(String input) {
        // Transaction that does not rollback for IllegalArgumentException
    }

    @Transactional(propagation = Propagation.NESTED)
    public void nestedOperation() {
        // Runs in a nested transaction with savepoint
    }
}
'''
        (self.service_dir / "UserService.java").write_text(self.sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_transactional_annotations(self):
        """Test detection of @Transactional annotations."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertIsInstance(result, TransactionAnalysisResult)
        self.assertGreater(len(result.boundaries), 0)

    def test_detect_default_transactional(self):
        """Test detection of default @Transactional annotation."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the createUser method
        create_user = next(
            (b for b in result.boundaries if b.method_name == "createUser"),
            None
        )
        self.assertIsNotNone(create_user)
        self.assertEqual(create_user.propagation, TransactionPropagation.REQUIRED)
        self.assertFalse(create_user.read_only)

    def test_detect_read_only_transaction(self):
        """Test detection of read-only transaction."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the getUser method
        get_user = next(
            (b for b in result.boundaries if b.method_name == "getUser"),
            None
        )
        self.assertIsNotNone(get_user)
        self.assertTrue(get_user.read_only)

    def test_detect_requires_new_propagation(self):
        """Test detection of REQUIRES_NEW propagation."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the sendNotification method
        send_notification = next(
            (b for b in result.boundaries if b.method_name == "sendNotification"),
            None
        )
        self.assertIsNotNone(send_notification)
        self.assertEqual(
            send_notification.propagation,
            TransactionPropagation.REQUIRES_NEW
        )

    def test_detect_isolation_and_timeout(self):
        """Test detection of isolation level and timeout."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the transferMoney method
        transfer_money = next(
            (b for b in result.boundaries if b.method_name == "transferMoney"),
            None
        )
        self.assertIsNotNone(transfer_money)
        self.assertEqual(
            transfer_money.isolation,
            TransactionIsolation.SERIALIZABLE
        )
        self.assertEqual(transfer_money.timeout, 30)

    def test_detect_rollback_for(self):
        """Test detection of rollbackFor attribute."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the processPayment method
        process_payment = next(
            (b for b in result.boundaries if b.method_name == "processPayment"),
            None
        )
        self.assertIsNotNone(process_payment)
        self.assertGreater(len(process_payment.rollback_for), 0)

    def test_detect_no_rollback_for(self):
        """Test detection of noRollbackFor attribute."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the validateInput method
        validate_input = next(
            (b for b in result.boundaries if b.method_name == "validateInput"),
            None
        )
        self.assertIsNotNone(validate_input)
        self.assertGreater(len(validate_input.no_rollback_for), 0)

    def test_detect_nested_propagation(self):
        """Test detection of NESTED propagation."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Find the nestedOperation method
        nested_op = next(
            (b for b in result.boundaries if b.method_name == "nestedOperation"),
            None
        )
        self.assertIsNotNone(nested_op)
        self.assertEqual(nested_op.propagation, TransactionPropagation.NESTED)


class TestTransactionStatistics(unittest.TestCase):
    """Test transaction statistics computation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Create simple service with various transaction types
        self.service_dir = self.repo_root / "src/main/java/com/example/service"
        self.service_dir.mkdir(parents=True)

        sample_service = '''
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {

    @Transactional
    public void placeOrder() {}

    @Transactional(readOnly = true)
    public Object findOrders() { return null; }

    @Transactional(readOnly = true)
    public Object getOrder() { return null; }
}
'''
        (self.service_dir / "OrderService.java").write_text(sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_compute_statistics(self):
        """Test statistics computation."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertEqual(result.total_transactions, 3)
        self.assertEqual(result.read_only_count, 2)
        self.assertEqual(result.write_count, 1)

    def test_read_write_ratio(self):
        """Test read/write ratio calculation."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertEqual(result.read_write_ratio, "2:1")


class TestNestedTransactionDetection(unittest.TestCase):
    """Test nested transaction detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Create service with nested transaction patterns
        self.service_dir = self.repo_root / "src/main/java/com/example/service"
        self.service_dir.mkdir(parents=True)

        sample_service = '''
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

@Service
public class PaymentService {

    @Transactional
    public void processPayment() {
        // Main transaction
        logPayment();
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logPayment() {
        // Independent transaction for logging
    }

    @Transactional(propagation = Propagation.NESTED)
    public void validatePayment() {
        // Nested with savepoint
    }
}
'''
        (self.service_dir / "PaymentService.java").write_text(sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_detect_requires_new_nested(self):
        """Test detection of REQUIRES_NEW as potential nested transaction."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Should detect REQUIRES_NEW methods as potential nested transactions
        self.assertGreater(result.nested_count, 0)

    def test_nested_transaction_info(self):
        """Test nested transaction information."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        # Check that nested transactions have proper information
        for nested in result.nested_transactions:
            self.assertIsNotNone(nested.inner_method)
            self.assertIsNotNone(nested.propagation_type)


class TestTransactionPatternIdentification(unittest.TestCase):
    """Test transaction pattern identification."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Create service with various patterns
        self.service_dir = self.repo_root / "src/main/java/com/example/service"
        self.service_dir.mkdir(parents=True)

        sample_service = '''
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

@Service
public class ProductService {

    @Transactional(readOnly = true)
    public Object findAll() { return null; }

    @Transactional(readOnly = true)
    public Object findById() { return null; }

    @Transactional
    public void create() {}

    @Transactional
    public void update() {}

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void audit() {}

    @Transactional(rollbackFor = Exception.class)
    public void importData() {}
}
'''
        (self.service_dir / "ProductService.java").write_text(sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_identify_read_only_pattern(self):
        """Test identification of read-only service pattern."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        patterns = result.patterns
        read_only_pattern = next(
            (p for p in patterns if p.pattern_type == "read_only_service"),
            None
        )
        self.assertIsNotNone(read_only_pattern)
        self.assertGreater(len(read_only_pattern.methods), 0)

    def test_identify_write_pattern(self):
        """Test identification of write service pattern."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        patterns = result.patterns
        write_pattern = next(
            (p for p in patterns if p.pattern_type == "write_service"),
            None
        )
        self.assertIsNotNone(write_pattern)
        self.assertGreater(len(write_pattern.methods), 0)

    def test_identify_independent_transaction_pattern(self):
        """Test identification of independent transaction pattern."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        patterns = result.patterns
        independent_pattern = next(
            (p for p in patterns if p.pattern_type == "independent_transaction"),
            None
        )
        self.assertIsNotNone(independent_pattern)

    def test_identify_custom_rollback_pattern(self):
        """Test identification of custom rollback pattern."""
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        patterns = result.patterns
        rollback_pattern = next(
            (p for p in patterns if p.pattern_type == "custom_rollback"),
            None
        )
        self.assertIsNotNone(rollback_pattern)


class TestTransactionBoundaryModel(unittest.TestCase):
    """Test TransactionBoundary domain model."""

    def test_is_write_transaction(self):
        """Test is_write_transaction property."""
        boundary = TransactionBoundary(
            method_name="saveUser",
            class_name="UserService",
            read_only=False
        )
        self.assertTrue(boundary.is_write_transaction)

        boundary_readonly = TransactionBoundary(
            method_name="getUser",
            class_name="UserService",
            read_only=True
        )
        self.assertFalse(boundary_readonly.is_write_transaction)

    def test_get_rollback_rules(self):
        """Test get_rollback_rules method."""
        boundary = TransactionBoundary(
            method_name="processPayment",
            class_name="PaymentService",
            rollback_for=["RuntimeException", "SQLException"],
            no_rollback_for=["ValidationException"]
        )

        rules = boundary.get_rollback_rules()
        self.assertEqual(len(rules), 3)

        # Check rollback rules
        rollback_rules = [r for r in rules if r.rollback]
        self.assertEqual(len(rollback_rules), 2)

        # Check no-rollback rules
        no_rollback_rules = [r for r in rules if not r.rollback]
        self.assertEqual(len(no_rollback_rules), 1)


class TestTransactionAnalysisResultModel(unittest.TestCase):
    """Test TransactionAnalysisResult domain model."""

    def test_compute_metrics(self):
        """Test compute_statistics method."""
        result = TransactionAnalysisResult(
            project_name="test-project",
            boundaries=[
                TransactionBoundary(
                    method_name="read1", class_name="Svc", read_only=True
                ),
                TransactionBoundary(
                    method_name="read2", class_name="Svc", read_only=True
                ),
                TransactionBoundary(
                    method_name="write1", class_name="Svc", read_only=False
                ),
                TransactionBoundary(
                    method_name="new1",
                    class_name="Svc",
                    propagation=TransactionPropagation.REQUIRES_NEW
                ),
            ]
        )

        result.compute_statistics()

        self.assertEqual(result.total_transactions, 4)
        self.assertEqual(result.read_only_count, 2)
        self.assertEqual(result.write_count, 2)  # non-readonly, includes REQUIRES_NEW
        self.assertEqual(result.requires_new_count, 1)


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
        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertEqual(len(result.boundaries), 0)
        self.assertEqual(result.total_transactions, 0)

    def test_analyze_repo_without_transactions(self):
        """Test analysis of repo without @Transactional annotations."""
        # Create Java file without transactions
        service_dir = self.repo_root / "src/main/java/com/example/service"
        service_dir.mkdir(parents=True)

        sample_service = '''
package com.example.service;

public class SimpleService {
    public void doSomething() {}
}
'''
        (service_dir / "SimpleService.java").write_text(sample_service)

        analyzer = TransactionAnalyzer(self.repo_root)
        result = analyzer.analyze()

        self.assertEqual(len(result.boundaries), 0)


class TestFilterMethods(unittest.TestCase):
    """Test filter methods for transaction boundaries."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.temp_dir)

        # Create service with various transaction types
        self.service_dir = self.repo_root / "src/main/java/com/example/service"
        self.service_dir.mkdir(parents=True)

        sample_service = '''
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;

@Service
public class FilterExampleService {

    @Transactional(readOnly = true)
    public Object read() { return null; }

    @Transactional
    public void write() {}

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void requiresNew() {}

    @Transactional(propagation = Propagation.NESTED)
    public void nested() {}
}
'''
        (self.service_dir / "FilterExampleService.java").write_text(sample_service)

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_get_read_only_transactions(self):
        """Test filtering read-only transactions."""
        analyzer = TransactionAnalyzer(self.repo_root)
        analyzer.analyze()

        read_only = analyzer.get_read_only_transactions()
        self.assertEqual(len(read_only), 1)
        self.assertEqual(read_only[0].method_name, "read")

    def test_get_write_transactions(self):
        """Test filtering write transactions."""
        analyzer = TransactionAnalyzer(self.repo_root)
        analyzer.analyze()

        write = analyzer.get_write_transactions()
        self.assertEqual(len(write), 3)  # write, requiresNew, nested

    def test_get_transactions_by_propagation(self):
        """Test filtering by propagation type."""
        analyzer = TransactionAnalyzer(self.repo_root)
        analyzer.analyze()

        requires_new = analyzer.get_transactions_by_propagation(
            TransactionPropagation.REQUIRES_NEW
        )
        self.assertEqual(len(requires_new), 1)
        self.assertEqual(requires_new[0].method_name, "requiresNew")

        nested = analyzer.get_transactions_by_propagation(
            TransactionPropagation.NESTED
        )
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0].method_name, "nested")


if __name__ == "__main__":
    unittest.main()

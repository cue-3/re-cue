"""
Unit tests for BusinessProcessIdentifier class.
"""

import unittest
from pathlib import Path
from reverse_engineer.analyzer import BusinessProcessIdentifier


class TestBusinessProcessIdentifier(unittest.TestCase):
    """Test suite for BusinessProcessIdentifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.identifier = BusinessProcessIdentifier(verbose=False)
    
    def test_initialization(self):
        """Test BusinessProcessIdentifier initialization."""
        self.assertIsNotNone(self.identifier)
        self.assertIn('transactional', self.identifier.transaction_patterns)
        self.assertIn('not_null', self.identifier.validation_patterns)
        self.assertIn('service_call', self.identifier.workflow_patterns)
    
    def test_extract_transactions_basic(self):
        """Test basic transaction extraction."""
        content = """
        @Transactional
        public void saveUser(User user) {
            userRepository.save(user);
        }
        """
        transactions = self.identifier._extract_transactions(content, Path("TestService.java"))
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['file'], 'TestService.java')
        self.assertEqual(transactions[0]['propagation'], 'REQUIRED')
        self.assertFalse(transactions[0]['readonly'])
    
    def test_extract_transactions_readonly(self):
        """Test readonly transaction extraction."""
        content = """
        @Transactional(readOnly = true)
        public User findUser(Long id) {
            return userRepository.findById(id);
        }
        """
        transactions = self.identifier._extract_transactions(content, Path("TestService.java"))
        
        self.assertEqual(len(transactions), 1)
        self.assertTrue(transactions[0]['readonly'])
    
    def test_extract_transactions_propagation(self):
        """Test transaction with propagation."""
        content = """
        @Transactional(propagation = Propagation.REQUIRES_NEW)
        public void createAuditLog(AuditLog log) {
            auditRepository.save(log);
        }
        """
        transactions = self.identifier._extract_transactions(content, Path("TestService.java"))
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['propagation'], 'REQUIRES_NEW')
    
    def test_extract_validations_not_null(self):
        """Test @NotNull validation extraction."""
        content = """
        public class UserDTO {
            @NotNull
            private String username;
            
            @NotNull
            private String email;
        }
        """
        validations = self.identifier._extract_validations(content, Path("UserDTO.java"))
        
        self.assertEqual(len(validations), 2)
        self.assertTrue(all(v['type'] == 'not_null' for v in validations))
    
    def test_extract_validations_size(self):
        """Test @Size validation extraction."""
        content = """
        public class UserDTO {
            @Size(min = 3, max = 50)
            private String username;
        }
        """
        validations = self.identifier._extract_validations(content, Path("UserDTO.java"))
        
        self.assertEqual(len(validations), 1)
        self.assertEqual(validations[0]['type'], 'size')
        self.assertEqual(validations[0]['min'], '3')
        self.assertEqual(validations[0]['max'], '50')
    
    def test_extract_validations_email(self):
        """Test @Email validation extraction."""
        content = """
        public class UserDTO {
            @Email
            private String email;
        }
        """
        validations = self.identifier._extract_validations(content, Path("UserDTO.java"))
        
        self.assertEqual(len(validations), 1)
        self.assertEqual(validations[0]['type'], 'email')
    
    def test_extract_workflows_async(self):
        """Test async workflow extraction."""
        content = """
        @Async
        public void sendEmailNotification(String email) {
            emailService.send(email);
        }
        """
        workflows = self.identifier._extract_workflows(content, Path("NotificationService.java"))
        
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0]['type'], 'async_operation')
    
    def test_extract_workflows_scheduled(self):
        """Test scheduled workflow extraction."""
        content = """
        @Scheduled(cron = "0 0 * * * *")
        public void cleanupOldData() {
            dataRepository.deleteOld();
        }
        """
        workflows = self.identifier._extract_workflows(content, Path("CleanupService.java"))
        
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0]['type'], 'scheduled_job')
    
    def test_extract_workflows_retry(self):
        """Test retryable workflow extraction."""
        content = """
        @Retryable
        public void callExternalApi() {
            externalService.call();
        }
        """
        workflows = self.identifier._extract_workflows(content, Path("ApiService.java"))
        
        self.assertEqual(len(workflows), 1)
        self.assertEqual(workflows[0]['type'], 'retryable_operation')
    
    def test_derive_business_rules_required_fields(self):
        """Test business rule derivation from required fields."""
        validations = [
            {'type': 'not_null', 'field': 'username', 'file': 'UserDTO.java'},
            {'type': 'not_null', 'field': 'email', 'file': 'UserDTO.java'},
            {'type': 'not_blank', 'field': 'password', 'file': 'UserDTO.java'},
        ]
        
        rules = self.identifier._derive_business_rules(validations)
        
        # Should derive a required fields rule
        required_rule = next((r for r in rules if r['rule_type'] == 'required_fields'), None)
        self.assertIsNotNone(required_rule)
        self.assertEqual(required_rule['entity'], 'User')
    
    def test_derive_business_rules_email(self):
        """Test business rule derivation from email validation."""
        validations = [
            {'type': 'email', 'field': 'email', 'file': 'UserDTO.java'},
        ]
        
        rules = self.identifier._derive_business_rules(validations)
        
        # Should derive a contact validation rule
        email_rule = next((r for r in rules if r['rule_type'] == 'contact_validation'), None)
        self.assertIsNotNone(email_rule)
    
    def test_enhance_preconditions(self):
        """Test use case precondition enhancement."""
        use_case = {
            'name': 'Create User',
            'preconditions': ['User must be authenticated'],
            'identified_from': ['UserController.createUser']
        }
        
        business_context = {
            'validations': [
                {'type': 'not_null', 'field': 'username', 'file': 'UserController.java'},
                {'type': 'email', 'field': 'email', 'file': 'UserController.java'},
            ],
            'transactions': [
                {'file': 'UserController.java', 'readonly': False}
            ],
            'workflows': [],
            'business_rules': []
        }
        
        enhanced = self.identifier.enhance_use_case_preconditions(use_case, business_context)
        
        self.assertIn('User must be authenticated', enhanced)
        self.assertTrue(any('required fields' in p.lower() for p in enhanced))
        self.assertTrue(any('email' in p.lower() for p in enhanced))
        self.assertTrue(any('database' in p.lower() for p in enhanced))
    
    def test_enhance_postconditions(self):
        """Test use case postcondition enhancement."""
        use_case = {
            'name': 'Create User',
            'postconditions': ['User is created'],
            'identified_from': ['UserController.createUser']
        }
        
        business_context = {
            'validations': [],
            'transactions': [
                {'file': 'UserController.java', 'readonly': False, 'propagation': 'REQUIRED'}
            ],
            'workflows': [
                {'type': 'async_operation', 'file': 'UserController.java'}
            ],
            'business_rules': []
        }
        
        enhanced = self.identifier.enhance_use_case_postconditions(use_case, business_context)
        
        self.assertIn('User is created', enhanced)
        self.assertTrue(any('persisted' in p.lower() or 'database' in p.lower() for p in enhanced))
        self.assertTrue(any('background' in p.lower() for p in enhanced))
    
    def test_generate_extension_scenarios(self):
        """Test extension scenario generation."""
        use_case = {
            'name': 'Create User',
            'extensions': [],
            'identified_from': ['UserController.java: createUser']
        }
        
        business_context = {
            'validations': [
                {'type': 'not_null', 'field': 'username', 'file': 'UserController.java'},
                {'type': 'email', 'field': 'email', 'file': 'UserController.java'},
                {'type': 'size', 'field': 'password', 'file': 'UserController.java'},
            ],
            'transactions': [
                {'file': 'UserController.java', 'readonly': False}
            ],
            'workflows': [
                {'type': 'retryable_operation', 'file': 'UserController.java', 'method': 'createUser'}
            ],
            'business_rules': []
        }
        
        extensions = self.identifier.generate_extension_scenarios(use_case, business_context)
        
        # Should have validation failure scenarios
        self.assertTrue(any('Required field missing' in e for e in extensions))
        self.assertTrue(any('Email format invalid' in e for e in extensions))
        self.assertTrue(any('size invalid' in e.lower() for e in extensions))
        
        # Should have transaction failure scenario
        self.assertTrue(any('Database error' in e for e in extensions))
        
        # Should have retry scenario (look for 'retries' or 'retry')
        self.assertTrue(any('retr' in e.lower() for e in extensions))


if __name__ == '__main__':
    unittest.main()

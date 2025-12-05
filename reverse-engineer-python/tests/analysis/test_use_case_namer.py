"""
Unit tests for the AI-enhanced use case naming module.

Tests the UseCaseNamer class and its various naming styles,
business terminology integration, and alternative suggestions.
"""

import unittest
from pathlib import Path
import tempfile
import json

# PyYAML is a dependency of the project, but handle import gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from reverse_engineer.analysis.naming import (
    UseCaseNamer,
    NamingStyle,
    NamingConfig,
    NameSuggestion,
)


class TestNamingConfig(unittest.TestCase):
    """Test the NamingConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = NamingConfig()
        
        self.assertEqual(config.style, NamingStyle.BUSINESS)
        self.assertTrue(config.generate_alternatives)
        self.assertEqual(config.num_alternatives, 3)
        self.assertEqual(config.business_terms, {})
        self.assertEqual(config.domain_vocabulary, [])
        self.assertTrue(config.use_verb_noun_format)
        self.assertTrue(config.include_entity)
        self.assertEqual(config.capitalize_style, "title")
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = NamingConfig(
            style=NamingStyle.TECHNICAL,
            generate_alternatives=False,
            num_alternatives=5,
            business_terms={"purchase": "Acquire"},
            capitalize_style="sentence"
        )
        
        self.assertEqual(config.style, NamingStyle.TECHNICAL)
        self.assertFalse(config.generate_alternatives)
        self.assertEqual(config.num_alternatives, 5)
        self.assertEqual(config.business_terms["purchase"], "Acquire")
        self.assertEqual(config.capitalize_style, "sentence")


class TestNamingStyle(unittest.TestCase):
    """Test the NamingStyle enum."""
    
    def test_all_styles_exist(self):
        """Test that all expected naming styles exist."""
        expected_styles = ["business", "technical", "concise", "verbose", "user_centric"]
        
        for style_name in expected_styles:
            style = NamingStyle(style_name)
            self.assertIsNotNone(style)
    
    def test_style_values(self):
        """Test style enum values."""
        self.assertEqual(NamingStyle.BUSINESS.value, "business")
        self.assertEqual(NamingStyle.TECHNICAL.value, "technical")
        self.assertEqual(NamingStyle.CONCISE.value, "concise")
        self.assertEqual(NamingStyle.VERBOSE.value, "verbose")
        self.assertEqual(NamingStyle.USER_CENTRIC.value, "user_centric")


class TestNameSuggestion(unittest.TestCase):
    """Test the NameSuggestion dataclass."""
    
    def test_suggestion_creation(self):
        """Test creating a name suggestion."""
        suggestion = NameSuggestion(
            name="Create User Account",
            style=NamingStyle.BUSINESS,
            confidence=0.95,
            reasoning="Business style naming",
            is_primary=True
        )
        
        self.assertEqual(suggestion.name, "Create User Account")
        self.assertEqual(suggestion.style, NamingStyle.BUSINESS)
        self.assertEqual(suggestion.confidence, 0.95)
        self.assertTrue(suggestion.is_primary)
    
    def test_suggestion_defaults(self):
        """Test default values for name suggestion."""
        suggestion = NameSuggestion(
            name="Test Name",
            style=NamingStyle.TECHNICAL
        )
        
        self.assertEqual(suggestion.confidence, 1.0)
        self.assertEqual(suggestion.reasoning, "")
        self.assertFalse(suggestion.is_primary)


class TestUseCaseNamerBasic(unittest.TestCase):
    """Test basic UseCaseNamer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.namer = UseCaseNamer()
    
    def test_simple_create_method(self):
        """Test naming for a simple create method."""
        suggestions = self.namer.generate_name("createUser", "User")
        
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(suggestions[0].is_primary)
        self.assertIn("User", suggestions[0].name)
        # Should use business verb
        self.assertIn("Create", suggestions[0].name)
    
    def test_simple_get_method(self):
        """Test naming for a simple get method."""
        suggestions = self.namer.generate_name("getUser", "User")
        
        self.assertGreater(len(suggestions), 0)
        primary = suggestions[0]
        # Business style should convert "get" to "View"
        self.assertIn("View", primary.name)
    
    def test_crud_operations(self):
        """Test naming for standard CRUD operations."""
        crud_methods = {
            "create": "Create",
            "get": "View",
            "update": "Update",
            "delete": "Delete",
            "list": "List",
        }
        
        for method, expected_verb in crud_methods.items():
            suggestions = self.namer.generate_name(f"{method}Order", "Order")
            self.assertGreater(len(suggestions), 0, f"Should generate suggestions for {method}")
            self.assertIn(expected_verb, suggestions[0].name, 
                         f"Expected '{expected_verb}' in name for {method}")
    
    def test_authentication_methods(self):
        """Test naming for authentication-related methods."""
        auth_methods = ["login", "logout", "register", "authenticate"]
        
        for method in auth_methods:
            suggestions = self.namer.generate_name(f"{method}User", "User")
            self.assertGreater(len(suggestions), 0, f"Should generate suggestions for {method}")
            # Should have meaningful business name
            self.assertGreater(len(suggestions[0].name), 5)


class TestUseCaseNamerStyles(unittest.TestCase):
    """Test different naming styles."""
    
    def test_business_style(self):
        """Test business naming style."""
        config = NamingConfig(style=NamingStyle.BUSINESS)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createOrder", "Order")
        primary = suggestions[0]
        
        self.assertEqual(primary.style, NamingStyle.BUSINESS)
        # Business style should use business-friendly language
        self.assertIn("Create", primary.name)
        self.assertIn("Order", primary.name)
    
    def test_technical_style(self):
        """Test technical naming style."""
        config = NamingConfig(style=NamingStyle.TECHNICAL)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createOrder", "Order")
        primary = suggestions[0]
        
        self.assertEqual(primary.style, NamingStyle.TECHNICAL)
    
    def test_concise_style(self):
        """Test concise naming style."""
        config = NamingConfig(style=NamingStyle.CONCISE)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createNewOrderForCustomer", "Order")
        primary = suggestions[0]
        
        self.assertEqual(primary.style, NamingStyle.CONCISE)
        # Concise should be shorter
        self.assertLess(len(primary.name), 30)
    
    def test_verbose_style(self):
        """Test verbose naming style."""
        config = NamingConfig(style=NamingStyle.VERBOSE)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createOrder", "Order")
        primary = suggestions[0]
        
        self.assertEqual(primary.style, NamingStyle.VERBOSE)
        # Verbose should be longer and more descriptive
        self.assertGreater(len(primary.name), 10)
    
    def test_user_centric_style(self):
        """Test user-centric naming style."""
        config = NamingConfig(style=NamingStyle.USER_CENTRIC)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createOrder", "Order")
        primary = suggestions[0]
        
        self.assertEqual(primary.style, NamingStyle.USER_CENTRIC)
        # User-centric should start with "User"
        self.assertTrue(primary.name.startswith("User"))


class TestUseCaseNamerAlternatives(unittest.TestCase):
    """Test alternative name generation."""
    
    def test_generates_alternatives(self):
        """Test that alternatives are generated when configured."""
        config = NamingConfig(generate_alternatives=True, num_alternatives=3)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createUser", "User")
        
        # Should have primary + alternatives
        self.assertGreater(len(suggestions), 1)
        
        # First should be primary
        self.assertTrue(suggestions[0].is_primary)
        
        # Rest should be alternatives
        for alt in suggestions[1:]:
            self.assertFalse(alt.is_primary)
    
    def test_no_alternatives_when_disabled(self):
        """Test that no alternatives are generated when disabled."""
        config = NamingConfig(generate_alternatives=False)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createUser", "User")
        
        # Should only have primary
        self.assertEqual(len(suggestions), 1)
        self.assertTrue(suggestions[0].is_primary)
    
    def test_alternatives_have_different_styles(self):
        """Test that alternatives use different styles."""
        config = NamingConfig(generate_alternatives=True, num_alternatives=3)
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createOrder", "Order")
        
        # Alternatives should have variety
        styles = {s.style for s in suggestions}
        self.assertGreater(len(styles), 1)
    
    def test_num_alternatives_respected(self):
        """Test that the number of alternatives is respected."""
        for num in [1, 2, 4]:
            config = NamingConfig(generate_alternatives=True, num_alternatives=num)
            namer = UseCaseNamer(config=config)
            
            suggestions = namer.generate_name("updateProduct", "Product")
            
            # Should have at most primary + num_alternatives
            self.assertLessEqual(len(suggestions), 1 + num)


class TestUseCaseNamerMethodParsing(unittest.TestCase):
    """Test method name parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.namer = UseCaseNamer()
    
    def test_camel_case_parsing(self):
        """Test parsing CamelCase method names."""
        test_cases = [
            ("createUser", ("create", ["user"])),
            ("getOrderById", ("get", ["order", "by", "id"])),
            ("updateCustomerAddress", ("update", ["customer", "address"])),
        ]
        
        for method_name, expected in test_cases:
            verb, objects = self.namer._parse_method_name(method_name)
            self.assertEqual(verb, expected[0], f"Verb mismatch for {method_name}")
            self.assertEqual(objects, expected[1], f"Objects mismatch for {method_name}")
    
    def test_snake_case_parsing(self):
        """Test parsing snake_case method names."""
        test_cases = [
            ("create_user", ("create", ["user"])),
            ("get_order_by_id", ("get", ["order", "by", "id"])),
            ("update_customer_address", ("update", ["customer", "address"])),
        ]
        
        for method_name, expected in test_cases:
            verb, objects = self.namer._parse_method_name(method_name)
            self.assertEqual(verb, expected[0], f"Verb mismatch for {method_name}")
            self.assertEqual(objects, expected[1], f"Objects mismatch for {method_name}")
    
    def test_single_word_method(self):
        """Test parsing single-word method names."""
        verb, objects = self.namer._parse_method_name("process")
        
        self.assertEqual(verb, "process")
        self.assertEqual(objects, [])


class TestUseCaseNamerEntityNormalization(unittest.TestCase):
    """Test entity name normalization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.namer = UseCaseNamer()
    
    def test_controller_suffix_removal(self):
        """Test that Controller suffix is removed."""
        result = self.namer._normalize_entity("UserController")
        self.assertEqual(result, "User")
    
    def test_service_suffix_removal(self):
        """Test that Service suffix is removed."""
        result = self.namer._normalize_entity("OrderService")
        self.assertEqual(result, "Order")
    
    def test_repository_suffix_removal(self):
        """Test that Repository suffix is removed."""
        result = self.namer._normalize_entity("ProductRepository")
        self.assertEqual(result, "Product")
    
    def test_business_term_mapping(self):
        """Test that known entities get business term mapping."""
        # "customer" should stay as "Customer" based on mapping
        result = self.namer._normalize_entity("Customer")
        self.assertEqual(result, "Customer")
        
        # "cart" should map to "Shopping Cart"
        result = self.namer._normalize_entity("Cart")
        self.assertEqual(result, "Shopping Cart")
    
    def test_unknown_entity_preserved(self):
        """Test that unknown entities are preserved as-is."""
        result = self.namer._normalize_entity("Widget")
        self.assertEqual(result, "Widget")


class TestUseCaseNamerBusinessTerms(unittest.TestCase):
    """Test custom business terminology integration."""
    
    def test_custom_verb_mapping(self):
        """Test custom verb mappings."""
        config = NamingConfig(
            business_terms={"purchase": "Acquire"}
        )
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("purchaseItem", "Item")
        
        # Should use custom business term
        self.assertIn("Acquire", suggestions[0].name)
    
    def test_custom_entity_mapping(self):
        """Test custom entity mappings."""
        config = NamingConfig(
            business_terms={"widget": "Custom Widget"}
        )
        namer = UseCaseNamer(config=config)
        
        # The custom term should be available for entity normalization
        normalized = namer._normalize_entity("Widget")
        self.assertEqual(normalized, "Custom Widget")


class TestUseCaseNamerCapitalization(unittest.TestCase):
    """Test capitalization styles."""
    
    def test_title_case(self):
        """Test title case capitalization."""
        config = NamingConfig(capitalize_style="title")
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createUser", "User")
        name = suggestions[0].name
        
        # Each word should be capitalized
        for word in name.split():
            self.assertTrue(word[0].isupper() if word else True)
    
    def test_sentence_case(self):
        """Test sentence case capitalization."""
        config = NamingConfig(capitalize_style="sentence")
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createUser", "User")
        name = suggestions[0].name
        
        # First letter should be capitalized
        self.assertTrue(name[0].isupper())
    
    def test_upper_case(self):
        """Test upper case capitalization."""
        config = NamingConfig(capitalize_style="upper")
        namer = UseCaseNamer(config=config)
        
        suggestions = namer.generate_name("createUser", "User")
        name = suggestions[0].name
        
        # All letters should be uppercase
        self.assertEqual(name, name.upper())


class TestUseCaseNamerEnhancement(unittest.TestCase):
    """Test the enhance_use_case_name method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.namer = UseCaseNamer()
    
    def test_enhance_existing_name(self):
        """Test enhancing an existing use case name."""
        suggestions = self.namer.enhance_use_case_name(
            current_name="Create User",
            method_name="createUser",
            entity_name="User"
        )
        
        self.assertGreater(len(suggestions), 0)
        # Should have at least one primary suggestion
        primaries = [s for s in suggestions if s.is_primary]
        self.assertEqual(len(primaries), 1)
    
    def test_enhance_preserves_original(self):
        """Test that enhancement can preserve original name as option."""
        suggestions = self.namer.enhance_use_case_name(
            current_name="Original Custom Name",
            method_name="createUser",
            entity_name="User"
        )
        
        # Original name should be included if significantly different
        names = [s.name for s in suggestions]
        self.assertIn("Original Custom Name", names)


class TestUseCaseNamerConfigFile(unittest.TestCase):
    """Test configuration file loading."""
    
    @unittest.skipUnless(HAS_YAML, "PyYAML not installed")
    def test_load_from_yaml(self):
        """Test loading configuration from YAML file."""
        config_content = """
naming:
    style: technical
    generate_alternatives: false
    num_alternatives: 2
    capitalize_style: sentence
    business_terms:
        purchase: Acquire
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text(config_content)
            
            namer = UseCaseNamer.from_config_file(config_path)
            
            self.assertEqual(namer.config.style, NamingStyle.TECHNICAL)
            self.assertFalse(namer.config.generate_alternatives)
            self.assertEqual(namer.config.num_alternatives, 2)
            self.assertEqual(namer.config.capitalize_style, "sentence")
    
    def test_load_from_json(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "naming": {
                "style": "concise",
                "generate_alternatives": True,
                "num_alternatives": 4
            }
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"
            config_path.write_text(json.dumps(config_data))
            
            namer = UseCaseNamer.from_config_file(config_path)
            
            self.assertEqual(namer.config.style, NamingStyle.CONCISE)
            self.assertTrue(namer.config.generate_alternatives)
            self.assertEqual(namer.config.num_alternatives, 4)
    
    def test_file_not_found_error(self):
        """Test error handling for missing config file."""
        with self.assertRaises(FileNotFoundError):
            UseCaseNamer.from_config_file(Path("/nonexistent/config.yaml"))


class TestUseCaseNamerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.namer = UseCaseNamer()
    
    def test_empty_method_name(self):
        """Test handling of empty method name."""
        suggestions = self.namer.generate_name("", "User")
        
        # Should still generate something
        self.assertGreater(len(suggestions), 0)
    
    def test_empty_entity_name(self):
        """Test handling of empty entity name."""
        suggestions = self.namer.generate_name("create", "")
        
        # Should still generate something
        self.assertGreater(len(suggestions), 0)
        self.assertIn("Create", suggestions[0].name)
    
    def test_unknown_verb(self):
        """Test handling of unknown verb."""
        suggestions = self.namer.generate_name("customOperation", "Entity")
        
        # Should still generate a name
        self.assertGreater(len(suggestions), 0)
        self.assertGreater(len(suggestions[0].name), 0)
    
    def test_very_long_method_name(self):
        """Test handling of very long method names."""
        long_method = "createNewCustomerOrderWithMultipleItemsAndApplyDiscount"
        suggestions = self.namer.generate_name(long_method, "Order")
        
        # Should handle gracefully
        self.assertGreater(len(suggestions), 0)
    
    def test_special_characters_in_name(self):
        """Test handling of special characters."""
        # Numbers in method name
        suggestions = self.namer.generate_name("getUser123", "User")
        self.assertGreater(len(suggestions), 0)


class TestUseCaseNamerIntegration(unittest.TestCase):
    """Integration tests for use case namer with analyzer."""
    
    def test_can_import_from_analysis(self):
        """Test that namer can be imported from analysis package."""
        from reverse_engineer.analysis import UseCaseNamer, NamingStyle, NamingConfig
        
        namer = UseCaseNamer()
        self.assertIsNotNone(namer)
    
    def test_generate_names_for_common_patterns(self):
        """Test generating names for common coding patterns."""
        namer = UseCaseNamer()
        
        common_patterns = [
            ("findAllByCustomerId", "Order"),
            ("processPayment", "Payment"),
            ("validateEmail", "User"),
            ("sendNotification", "Notification"),
            ("calculateTotal", "Cart"),
            ("importData", "Data"),
            ("exportReport", "Report"),
            ("archiveOldRecords", "Record"),
        ]
        
        for method, entity in common_patterns:
            suggestions = namer.generate_name(method, entity)
            self.assertGreater(len(suggestions), 0, 
                             f"Should generate suggestions for {method}")
            self.assertGreater(len(suggestions[0].name), 0,
                             f"Name should not be empty for {method}")


if __name__ == '__main__':
    unittest.main()

"""Test the example Jinja2 template to demonstrate advanced features."""

import unittest
from pathlib import Path
from reverse_engineer.templates.template_loader import TemplateLoader


class TestJinja2ExampleTemplate(unittest.TestCase):
    """Test the example Jinja2 template with realistic data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
        self.templates_dir = Path(__file__).parent.parent / 'reverse_engineer' / 'templates' / 'common'
    
    def test_example_template_with_full_data(self):
        """Test the example template with complete project data."""
        if not (self.templates_dir / "example-jinja2-features.md").exists():
            self.skipTest("Example template not found")
        
        # Create realistic test data
        test_data = {
            'project_name': 'my awesome project',
            'date': '2024-11-16',
            'version': '2.1.0',
            'actor_count': 3,
            'actors': [
                {
                    'name': 'Administrator',
                    'type': 'user',
                    'access_level': 'Full',
                    'description': 'System administrator with full access'
                },
                {
                    'name': 'Customer',
                    'type': 'end_user',
                    'access_level': 'Limited',
                    'description': None
                },
                {
                    'name': 'Payment Gateway',
                    'type': 'external_system',
                    'access_level': 'API',
                    'description': 'Third-party payment processor'
                }
            ],
            'endpoints': [
                {
                    'method': 'GET',
                    'path': '/api/users',
                    'authenticated': True,
                    'description': 'List all users'
                },
                {
                    'method': 'POST',
                    'path': '/api/users',
                    'authenticated': True,
                    'description': 'Create a new user'
                },
                {
                    'method': 'GET',
                    'path': '/api/health',
                    'authenticated': False,
                    'description': 'Health check endpoint'
                },
                {
                    'method': 'PUT',
                    'path': '/api/users/{id}',
                    'authenticated': True,
                    'description': 'Update user'
                },
                {
                    'method': 'DELETE',
                    'path': '/api/users/{id}',
                    'authenticated': True,
                    'description': 'Delete user'
                }
            ],
            'models': [
                {
                    'name': 'User',
                    'fields': 8,
                    'location': 'src/models/User.java',
                    'relationships': ['hasMany:Projects', 'belongsTo:Organization']
                },
                {
                    'name': 'Project',
                    'fields': 12,
                    'location': 'src/models/Project.java',
                    'relationships': ['belongsTo:User', 'hasMany:Tasks']
                },
                {
                    'name': 'Task',
                    'fields': 6,
                    'location': 'src/models/Task.java',
                    'relationships': ['belongsTo:Project']
                }
            ],
            'test_coverage': {
                'overall': 85
            },
            'code_quality': {
                'complexity': 'Low',
                'maintainability': 'High',
                'duplication': '2%'
            },
            'recommendations': {
                'security': [
                    'Add rate limiting to public endpoints',
                    'Implement API key rotation'
                ],
                'performance': [
                    'Consider caching for frequently accessed data',
                    'Optimize database queries in User model'
                ],
                'maintainability': [
                    'Add more comprehensive logging',
                    'Document complex business logic'
                ]
            }
        }
        
        # Load and render the template
        result = self.loader.render_template('example-jinja2-features.md', **test_data)
        
        # Verify key content is present
        self.assertIn('MY AWESOME PROJECT', result)  # Filter: upper
        self.assertIn('2024-11-16', result)
        self.assertIn('Version**: 2.1.0', result)
        
        # Verify actors section
        self.assertIn('Actors (3 total)', result)
        self.assertIn('**Administrator** (User)', result)  # Filter: title
        self.assertIn('Full', result)
        self.assertIn('System administrator', result)
        self.assertIn('**Customer** (End User)', result)  # Filter: title
        self.assertIn('**Payment Gateway** (External System)', result)
        
        # Verify endpoints section
        self.assertIn('API Endpoints (5)', result)
        self.assertIn('GET', result)
        self.assertIn('POST', result)
        self.assertIn('PUT', result)
        self.assertIn('DELETE', result)
        self.assertIn('/api/users', result)
        self.assertIn('🔒 Yes', result)  # Authenticated
        self.assertIn('No', result)  # Not authenticated
        
        # Verify endpoint statistics
        self.assertIn('Total endpoints: 5', result)
        self.assertIn('Authenticated endpoints: 4', result)
        self.assertIn('Public endpoints: 1', result)
        
        # Verify HTTP method counts
        self.assertIn('**GET**: 2 endpoints', result)
        self.assertIn('**POST**: 1 endpoint', result)
        self.assertIn('**PUT**: 1 endpoint', result)
        self.assertIn('**DELETE**: 1 endpoint', result)
        
        # Verify models section
        self.assertIn('Data Models (3)', result)
        self.assertIn('1. User', result)
        self.assertIn('2. Project', result)
        self.assertIn('3. Task', result)
        self.assertIn('**Fields**: 8', result)
        self.assertIn('**Fields**: 12', result)
        self.assertIn('**Fields**: 6', result)
        
        # Verify quality metrics
        self.assertIn('Test Coverage', result)
        self.assertIn('Overall: 85%', result)
        self.assertIn('✅ **Excellent**', result)
        self.assertIn('Code Quality', result)
        self.assertIn('Complexity: Low', result)
        
        # Verify recommendations
        self.assertIn('Security', result)
        self.assertIn('Add rate limiting', result)
        self.assertIn('Performance', result)
        self.assertIn('Consider caching', result)
        self.assertIn('Maintainability', result)
        
        # Verify summary
        self.assertIn('This analysis found:', result)
        self.assertIn('3 actor(s)', result)
        self.assertIn('5 API endpoint(s)', result)
        self.assertIn('3 data model(s)', result)
    
    def test_example_template_with_empty_data(self):
        """Test the example template with minimal/empty data."""
        if not (self.templates_dir / "example-jinja2-features.md").exists():
            self.skipTest("Example template not found")
        
        # Create minimal test data
        test_data = {
            'project_name': 'empty project',
            'date': '2024-11-16',
            'actor_count': 0,
            'actors': [],
            'endpoints': [],
            'models': []
        }
        
        # Load and render the template
        result = self.loader.render_template('example-jinja2-features.md', **test_data)
        
        # Verify project name
        self.assertIn('EMPTY PROJECT', result)
        
        # Verify empty state messages
        self.assertIn('*No actors have been identified yet.*', result)
        self.assertIn('*No endpoints discovered in this project.*', result)
        self.assertIn('*No data models found.*', result)
        self.assertIn('*No recommendations at this time.*', result)
        self.assertIn('*Project analysis is incomplete. Please run a full analysis.*', result)
        
        # Verify that sections for data that doesn't exist are not shown
        self.assertNotIn('Actors (0 total)', result)  # Should use else clause
        self.assertNotIn('API Endpoints (0)', result)
        self.assertNotIn('Data Models (0)', result)
    
    def test_example_template_with_medium_coverage(self):
        """Test that template shows different messages based on test coverage."""
        if not (self.templates_dir / "example-jinja2-features.md").exists():
            self.skipTest("Example template not found")
        
        # Test with medium coverage (60-79%)
        result_medium = self.loader.render_template(
            'example-jinja2-features.md',
            project_name='test',
            date='2024-11-16',
            actor_count=0,
            actors=[],
            endpoints=[],
            models=[],
            test_coverage={'overall': 70}
        )
        
        self.assertIn('Overall: 70%', result_medium)
        self.assertIn('⚠️ **Good**', result_medium)
        self.assertIn('Consider adding more tests', result_medium)
        
        # Test with low coverage (<60%)
        result_low = self.loader.render_template(
            'example-jinja2-features.md',
            project_name='test',
            date='2024-11-16',
            actor_count=0,
            actors=[],
            endpoints=[],
            models=[],
            test_coverage={'overall': 45}
        )
        
        self.assertIn('Overall: 45%', result_low)
        self.assertIn('❌ **Needs Improvement**', result_low)
        self.assertIn('Low test coverage', result_low)


if __name__ == '__main__':
    unittest.main()

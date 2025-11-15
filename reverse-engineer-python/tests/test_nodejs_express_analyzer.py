"""
Test Node.js Express analyzer.
"""

import unittest
from pathlib import Path
import tempfile

from reverse_engineer.analyzers import NodeExpressAnalyzer


class TestNodeExpressAnalyzer(unittest.TestCase):
    """Test Node.js Express analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create basic Express structure
        self.routes_path = self.test_path / 'routes'
        self.routes_path.mkdir()
        
        self.models_path = self.test_path / 'models'
        self.models_path.mkdir()
        
        self.services_path = self.test_path / 'services'
        self.services_path.mkdir()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_discover_express_routes(self):
        """Test Express route discovery."""
        # Create sample route file
        route_content = '''const express = require('express');
const router = express.Router();

// Get all users
router.get('/users', (req, res) => {
    res.json({ users: [] });
});

// Create user
router.post('/users', authenticate, (req, res) => {
    res.json({ message: 'User created' });
});

// Update user
router.put('/users/:id', authenticate, (req, res) => {
    res.json({ message: 'User updated' });
});

module.exports = router;
'''
        
        route_file = self.routes_path / 'users.js'
        route_file.write_text(route_content)
        
        # Analyze
        analyzer = NodeExpressAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify
        self.assertEqual(len(endpoints), 3)
        self.assertEqual(endpoints[0].method, 'GET')
        self.assertEqual(endpoints[0].path, '/users')
        self.assertFalse(endpoints[0].authenticated)
        
        self.assertEqual(endpoints[1].method, 'POST')
        self.assertTrue(endpoints[1].authenticated)
        
        self.assertEqual(endpoints[2].method, 'PUT')
        self.assertTrue(endpoints[2].authenticated)
    
    def test_discover_mongoose_models(self):
        """Test Mongoose model discovery."""
        # Create sample Mongoose model
        model_content = '''const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', userSchema);
'''
        
        model_file = self.models_path / 'User.js'
        model_file.write_text(model_content)
        
        # Analyze
        analyzer = NodeExpressAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()
        
        # Verify
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].name, 'User')
        self.assertEqual(models[0].fields, 4)
    
    def test_discover_typescript_routes(self):
        """Test TypeScript route discovery."""
        # Create tsconfig.json
        tsconfig = self.test_path / 'tsconfig.json'
        tsconfig.write_text('{}')
        
        # Create TypeScript route
        route_content = '''import { Router } from 'express';
const router = Router();

router.get('/products', (req, res) => {
    res.json([]);
});

export default router;
'''
        
        route_file = self.routes_path / 'products.ts'
        route_file.write_text(route_content)
        
        # Analyze
        analyzer = NodeExpressAnalyzer(self.test_path, verbose=False)
        self.assertTrue(analyzer.is_typescript)
        
        endpoints = analyzer.discover_endpoints()
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0].path, '/products')
    
    def test_discover_services(self):
        """Test service discovery."""
        # Create service file
        service_content = '''class UserService {
    async findAll() {
        return [];
    }
    
    async findById(id) {
        return null;
    }
}

module.exports = new UserService();
'''
        
        service_file = self.services_path / 'UserService.js'
        service_file.write_text(service_content)
        
        # Analyze
        analyzer = NodeExpressAnalyzer(self.test_path, verbose=False)
        services = analyzer.discover_services()
        
        # Verify
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, 'UserService')
    
    def test_discover_actors(self):
        """Test actor discovery."""
        # Create auth middleware with roles
        auth_content = '''const roles = {
    USER: 'user',
    ADMIN: 'admin',
    MODERATOR: 'moderator'
};

module.exports = { roles };
'''
        
        auth_file = self.test_path / 'auth.js'
        auth_file.write_text(auth_content)
        
        # Analyze
        analyzer = NodeExpressAnalyzer(self.test_path, verbose=False)
        actors = analyzer.discover_actors()
        
        # Verify we found at least default actors
        self.assertGreaterEqual(len(actors), 3)
        actor_names = [a.name for a in actors]
        self.assertIn('User', actor_names)
        self.assertIn('Admin', actor_names)


if __name__ == '__main__':
    unittest.main()

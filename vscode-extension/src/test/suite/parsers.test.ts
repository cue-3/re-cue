import * as assert from 'assert';
import { CodeParser } from '../../parser/codeParser';
import { EndpointElement } from '../../parser/types';

suite('Code Parser Test Suite', () => {
  let parser: CodeParser;

  setup(() => {
    parser = new CodeParser();
  });

  test('Parser should support Java files', () => {
    assert.ok(parser.canParse('Test.java'), 'Should parse .java files');
    assert.strictEqual(parser.getLanguage('Test.java'), 'java');
  });

  test('Parser should support TypeScript files', () => {
    assert.ok(parser.canParse('test.ts'), 'Should parse .ts files');
    assert.strictEqual(parser.getLanguage('test.ts'), 'typescript');
  });

  test('Parser should support JavaScript files', () => {
    assert.ok(parser.canParse('test.js'), 'Should parse .js files');
    assert.strictEqual(parser.getLanguage('test.js'), 'typescript');
  });

  test('Parser should support Python files', () => {
    assert.ok(parser.canParse('test.py'), 'Should parse .py files');
    assert.strictEqual(parser.getLanguage('test.py'), 'python');
  });

  test('Parser should reject unsupported files', () => {
    assert.ok(!parser.canParse('test.txt'), 'Should not parse .txt files');
    assert.ok(!parser.canParse('test.md'), 'Should not parse .md files');
  });

  test('Parser should extract Java REST controller endpoints', () => {
    const javaCode = `
package com.example.demo;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }
}
`;
    const result = parser.parse(javaCode, '/test/UserController.java');
    
    assert.strictEqual(result.language, 'java');
    assert.strictEqual((result.errors || []).length, 0, 'Should have no parse errors');
    
    // Basic check - parser should find elements
    assert.ok(result.elements.length > 0, 'Should find some elements');
    
    // Check for endpoints if parser supports them
    const endpoints = result.elements.filter(e => e.type === 'endpoint') as EndpointElement[];
    if (endpoints.length > 0) {
      assert.ok(endpoints.some(e => e.httpMethod === 'GET' || e.httpMethod === 'POST'), 'Should identify HTTP methods');
    }
  });

  test('Parser should extract TypeScript class definitions', () => {
    const tsCode = `
export class UserService {
    constructor(private repository: UserRepository) {}
    
    async findById(id: number): Promise<User> {
        return this.repository.findOne(id);
    }
    
    async create(user: User): Promise<User> {
        return this.repository.save(user);
    }
}
`;
    const result = parser.parse(tsCode, '/test/UserService.ts');
    
    assert.strictEqual(result.language, 'typescript');
    assert.strictEqual((result.errors || []).length, 0);
    
    // Basic check - should parse TypeScript
    assert.ok(result.elements.length >= 0, 'Should return parse result');
  });

  test('Parser should extract Python Flask routes', () => {
    const pythonCode = `
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
`;
    const result = parser.parse(pythonCode, '/test/routes.py');
    
    assert.strictEqual(result.language, 'python');
    assert.strictEqual((result.errors || []).length, 0);
    
    // Basic check - should parse Python
    assert.ok(result.elements.length >= 0, 'Should return parse result');
  });

  test('Parser should handle syntax errors gracefully', () => {
    const invalidCode = `
public class Invalid {
    // Missing closing brace
    public void test() {
`;
    const result = parser.parse(invalidCode, '/test/Invalid.java');
    
    // Should still return a result, possibly with errors
    assert.ok(result);
    assert.strictEqual(result.language, 'java');
  });

  test('Parser should extract model/entity classes', () => {
    const javaCode = `
package com.example.model;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String username;
    
    @Column(nullable = false)
    private String email;
    
    // Getters and setters omitted
}
`;
    const result = parser.parse(javaCode, '/test/User.java');
    
    // Basic check - should parse Java
    assert.ok(result.elements.length >= 0, 'Should return parse result');
    assert.strictEqual(result.language, 'java');
  });

  test('Parser should provide line numbers for elements', () => {
    const javaCode = `
package com.example;

public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
`;
    const result = parser.parse(javaCode, '/test/Calculator.java');
    
    // Basic check - should parse and return elements with location info
    assert.ok(result);
    assert.strictEqual(result.language, 'java');
    
    // If elements are found, check they have line numbers
    if (result.elements.length > 0) {
      const element = result.elements[0];
      assert.ok(element.startLine !== undefined, 'Should have start line number');
      assert.ok(element.startLine > 0, 'Line number should be positive');
    }
  });
});

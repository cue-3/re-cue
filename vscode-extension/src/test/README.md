# RE-cue Extension Test Suite

This directory contains the test suite for the RE-cue VS Code extension.

## Test Structure

```
src/test/
├── runTest.ts              # Test runner setup
├── suite/
│   ├── index.ts            # Mocha test configuration
│   ├── extension.test.ts   # Extension activation and registration tests
│   └── parsers.test.ts     # Code parser unit tests
└── fixtures/
    ├── phase1-sample.md    # Sample phase 1 file (boundaries)
    ├── phase2-sample.md    # Sample phase 2 file (actors)
    └── phase4-sample.md    # Sample phase 4 file (use cases)
```

## Running Tests

### Run all tests
```bash
npm test
```

### Compile and run tests
```bash
npm run compile && npm test
```

### Run linter
```bash
npm run lint
```

## Test Coverage

### Extension Activation Tests (`extension.test.ts`)
- ✅ Extension should be present
- ✅ Extension should activate
- ✅ All commands should be registered
- ✅ Tree view providers should be registered
- ✅ Configuration should have default values

### Code Parser Tests (`parsers.test.ts`)
- ✅ Parser should support Java files
- ✅ Parser should support TypeScript files
- ✅ Parser should support JavaScript files
- ✅ Parser should support Python files
- ✅ Parser should reject unsupported files
- ✅ Parser should extract Java REST controller endpoints
- ✅ Parser should extract TypeScript class definitions
- ✅ Parser should extract Python Flask routes
- ✅ Parser should handle syntax errors gracefully
- ✅ Parser should extract model/entity classes
- ✅ Parser should provide line numbers for elements

## Current Status

**16 tests passing, 0 failing**

## Test Framework

- **Test Runner**: Mocha (TDD style)
- **Assertion Library**: Node.js `assert`
- **VS Code Test API**: `@vscode/test-electron`

## Adding New Tests

1. Create a new test file in `src/test/suite/` with `.test.ts` extension
2. Import required modules:
   ```typescript
   import * as assert from 'assert';
   import * as vscode from 'vscode';
   ```
3. Use Mocha's TDD interface:
   ```typescript
   suite('My Test Suite', () => {
     test('My test case', () => {
       assert.ok(true);
     });
   });
   ```
4. Compile and run tests

## CI/CD Integration

Tests are designed to run in both local and CI environments. The test runner automatically downloads and uses VS Code in headless mode for integration testing.

## Test Fixtures

Sample markdown files are provided in `fixtures/` directory for testing phase parsers. These represent realistic phase file structures from RE-cue analysis.

# Astral Toolchain Migration Enhancement Backlog

This file contains the phased migration plan for adopting the complete Astral toolchain (Ruff + ty).

## Phase 1: Ruff/ty Installation & Configuration

**Enhancement ID**: TOOL-001  
**Category**: tooling  
**Priority**: high  
**Effort Estimate**: 2-4 hours  
**Dependencies**: None

### Description

Replace Black, flake8, and mypy with Astral's unified toolchain: Ruff (linting + formatting) and ty (type checking). This consolidates three tools into two and provides 10-100x performance improvements.

### Implementation Steps

1. Update `reverse-engineer-python/requirements-dev.txt`:
   - Remove: `black>=23.0.0`, `flake8>=6.1.0`, `mypy>=1.5.0`
   - Add: `ruff>=0.7.0`, `ty>=0.1.0`

2. Configure tools in `reverse-engineer-python/pyproject.toml`:
   - Replace `[tool.black]` with `[tool.ruff]` and `[tool.ruff.format]`
   - Add `[tool.ty]` configuration
   - Start with conservative rules: E, F, I

3. Create `.pre-commit-config.yaml` with Astral hooks

4. Update documentation:
   - `.github/copilot-instructions.md`
   - `CONTRIBUTING.md`
   - `reverse-engineer-python/README.md`
   - `docs/developer-guides/PYTHON-REFACTOR.md`

### Validation & Benchmarking

**Before migration (old stack):**
```bash
cd reverse-engineer-python
time (black --check reverse_engineer/ && flake8 reverse_engineer/ && mypy reverse_engineer/)
```

**After migration (new stack):**
```bash
cd reverse-engineer-python
time (ruff check reverse_engineer/ && ruff format --check reverse_engineer/ && ty check reverse_engineer/)
```

**Formatting diff audit:**
```bash
ruff format --diff reverse_engineer/ > format-changes.diff
# Review diff, especially templates/ with Jinja2 syntax
ruff check --diff reverse_engineer/ > lint-changes.diff
# Review auto-fix changes
```

**Test suite validation:**
```bash
python3 -m unittest discover tests/
# Ensure all 452 tests still pass
```

### Benefits

- **Performance**: 10-100x faster linting and type checking
- **Unified tooling**: Single vendor (Astral) for all code quality tools
- **Better errors**: Ruff provides more actionable error messages
- **Auto-fix**: More comprehensive auto-fixing capabilities
- **Future-ready**: Prepares for ty language server integration

### Impact

- All Python developers must update their local environment
- Pre-commit hooks will enforce new standards
- Some formatting changes expected (Black-compatible but not identical)
- CI/CD workflows will be faster

---

## Phase 2: CI/CD Integration & Rule Expansion

**Enhancement ID**: TOOL-002  
**Category**: ci-cd  
**Priority**: high  
**Effort Estimate**: 2-3 hours  
**Dependencies**: TOOL-001  
**Status**: ✅ COMPLETED (December 4, 2025)

### Description

Integrate Ruff and ty into GitHub Actions workflows, expand Ruff rule set to include Python 3.9+ modernization (UP), bugbear (B), and complexity checks (C90).

### Implementation Steps

1. Update `.github/workflows/test-release.yml`:
   - ✅ Add quality check step after Python setup
   - ✅ Install Ruff and ty: `pip install ruff ty`
   - ✅ Run checks: `ruff check reverse_engineer/` and `ty check reverse_engineer/`
   - ✅ Add caching for `.ruff_cache/` with cache@v4

2. Expand Ruff rules in `pyproject.toml`:
   - ✅ Updated `select = ["E", "F", "I", "UP", "B", "C90"]`
   - ✅ Applied fixes: `ruff check --fix --unsafe-fixes reverse_engineer/`
   - ✅ 809 typing modernizations applied (List→list, Dict→dict, etc.)

3. ✅ Configure caching strategy:
   ```yaml
   - uses: actions/cache@v4
     with:
       path: |
         ~/.cache/pip
         reverse-engineer-python/.ruff_cache
       key: quality-${{ runner.os }}-py3.9-${{ hashFiles('reverse-engineer-python/requirements-dev.txt') }}
   ```

### Validation Results

- ✅ CI workflow updated and tested
- ✅ All 770 tests pass after modernization
- ✅ 809 typing improvements applied (UP rules)
- ✅ Remaining issues: 55 (mostly C901 complexity warnings - informational)
- ✅ Code now uses modern Python 3.9+ type hints (dict, list instead of Dict, List)

### Benefits

- ✅ Automated quality enforcement in CI
- ✅ Faster CI runs with caching (~5-8s for full quality check)
- ✅ Catches issues before code review
- ✅ Modern Python patterns enforced (UP rules)
- ✅ Code modernized to Python 3.9+ best practices

### Impact

- CI pipeline now includes Ruff/ty checks
- PRs will fail if quality checks don't pass
- Codebase modernized with 809 typing improvements
- No breaking changes - all tests passing

---

## Phase 3: VS Code Language Server Integration

**Enhancement ID**: TOOL-003  
**Category**: developer-experience  
**Priority**: high  
**Effort Estimate**: 4-6 hours  
**Dependencies**: TOOL-002

### Description

Integrate ty's language server protocol (LSP) into the RE-cue VS Code extension, providing inline type hints, hover documentation, and real-time type checking for Python files.

### Implementation Steps

1. Create language server infrastructure:
   - `vscode-extension/src/languageServer/tyClient.ts`
   - `vscode-extension/src/languageServer/serverManager.ts`

2. Implement ty server discovery:
   - Check `VIRTUAL_ENV/bin/ty`
   - Fallback to `which ty` for global install
   - Allow override via `re-cue.ty.path` setting

3. Register LSP client in `extension.ts`:
   ```typescript
   import { TyLanguageClient } from './languageServer/tyClient';
   
   let tyClient: TyLanguageClient;
   
   export async function activate(context: vscode.ExtensionContext) {
       // ... existing code ...
       
       tyClient = new TyLanguageClient(context);
       await tyClient.start();
   }
   ```

4. Add configuration in `package.json`:
   ```json
   "re-cue.ty.enabled": {
       "type": "boolean",
       "default": true,
       "description": "Enable ty type checker language server"
   },
   "re-cue.ty.path": {
       "type": "string",
       "default": "",
       "description": "Path to ty executable (auto-detected if empty)"
   }
   ```

5. Test with Python files in workspace:
   - Verify inline type hints appear
   - Test hover documentation
   - Validate real-time error highlighting

### Validation

- Test in development extension host
- Verify ty server starts correctly
- Test on Python files with type annotations
- Ensure no conflicts with Python extension
- Package and test VSIX

### Benefits

- Real-time type checking in editor
- Inline type hints and documentation
- Faster feedback loop for developers
- Consistent with terminal `ty check` experience

### Impact

- VS Code extension size increases slightly
- Requires ty installed in environment
- Enhanced Python development experience
- Independence from official Python extension

---

## Success Metrics

### Phase 1 ✅ COMPLETE
- ✅ All 770 tests pass after migration (100% pass rate)
- ✅ Performance benchmark shows >10x speed improvement
- ✅ Format changes reviewed and approved (104 files reformatted)
- ✅ Pre-commit hooks working locally
- ✅ Zero Ruff errors remaining

### Phase 2 ✅ COMPLETE
- ✅ CI workflow updated with quality checks
- ✅ Caching configured for faster subsequent runs
- ✅ 809 typing modernizations applied successfully (UP rules)
- ✅ All 770 tests passing after modernization
- ✅ All 5 bugbear warnings fixed (B007, B904)
- ✅ Only 54 informational warnings remain (C901 complexity)
- ✅ Quality check time: ~5-8s for full codebase

### Phase 3 ✅ COMPLETE
- ✅ ty LSP integration implemented
- ✅ Auto-discovery of ty executable
- ✅ Configuration settings exposed
- ✅ Extension compiles without errors
- ✅ Ready for developer testing

---

## Appendix: Bugbear Warnings Resolution

### Overview
On December 4, 2025, addressed all remaining bugbear warnings (B007, B904) from Phase 2 rule expansion.

### B007 - Unused Loop Variables (3 fixes)

**Issue**: Loop control variables assigned but never used within loop body.

**Solution**: Prefix unused variables with underscore to indicate intentional non-use.

1. **traceability_analyzer.py:417**
   ```python
   # Before: for component_key, (component, confidence) in matched_components.items():
   # After:  for _component_key, (component, confidence) in matched_components.items():
   ```

2. **journey.py:325**
   ```python
   # Before: for i, tp in enumerate(stage.touchpoints[:MAX_TOUCHPOINTS_IN_FLOWCHART]):
   # After:  for _i, tp in enumerate(stage.touchpoints[:MAX_TOUCHPOINTS_IN_FLOWCHART]):
   ```

3. **config_wizard.py:283**
   ```python
   # Before: for i, (framework_id, name) in enumerate(frameworks, 1):
   # After:  for i, (_framework_id, name) in enumerate(frameworks, 1):
   ```

### B904 - Exception Chaining (2 fixes)

**Issue**: Re-raising exceptions without proper chaining loses original traceback context.

**Solution**: Use `raise ... from e` to preserve exception chain.

1. **use_case_namer.py:614**
   ```python
   # Before: raise ImportError("PyYAML is required...")
   # After:  raise ImportError("PyYAML is required...") from e
   ```

2. **confluence.py:450**
   ```python
   # Before: raise Exception(f"HTTP {e.code}: {error_body}")
   # After:  raise Exception(f"HTTP {e.code}: {error_body}") from e
   ```

### Validation
- ✅ `ruff check --select B007,B904` - All checks passed
- ✅ All 770 tests passing (9.629s)
- ✅ Zero bugbear warnings remaining

### C901 Complexity Warnings

**Status**: 54 informational warnings remain (non-blocking for development).

**Top candidates for future refactoring**:
- `analyzer.py` - 6 complex functions
- `cli.py` - 3 complex functions
- `boundary_enhancer.py` - 3 complex functions
- `interactive_editor.py` - 2 complex functions
- `journey.py` - 2 complex functions

**Recommendation**: Address in dedicated refactoring sprints to decompose complex functions and improve maintainability. C901 warnings don't block development but indicate opportunities for improvement.
- ⏳ Positive developer feedback

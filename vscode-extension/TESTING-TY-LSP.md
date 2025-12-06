# Testing Guide: ty Language Server Integration

## Overview
This guide helps you test the ty language server integration in the RE-cue VS Code extension.

## Prerequisites

✅ **ty is installed**: `/Users/squick/Library/Python/3.9/bin/ty`  
✅ **ty version**: `0.0.1-alpha.31`  
✅ **Extension packaged**: Check for `.vsix` file in `vscode-extension/`

## Testing Steps

### 1. Install the Updated Extension

```bash
cd /Users/squick/workspace/cue-3/re-cue/vscode-extension
code --install-extension re-cue-0.0.9.vsix --force
```

Or press **F5** in VS Code to launch Extension Development Host.

### 2. Open the Test File

Open `test_ty_lsp.py` in the workspace root. This file contains:
- ✅ Correct type annotations
- ❌ Intentional type errors (for testing diagnostics)
- 📝 Various patterns to test hover and IntelliSense

### 3. Verify ty Server Started

**Check Output Channel:**
1. Open Command Palette (`Cmd+Shift+P`)
2. Select "Output: Focus on Output View"
3. Select "ty Language Server" from dropdown
4. Look for: `✓ ty language server started successfully`

**Expected Output:**
```
ty language server activated
Found ty at: /Users/squick/Library/Python/3.9/bin/ty
ty language server started successfully
```

**Check Status Bar:**
- Initially: `⟳ ty: starting...` (spinning icon)
- Success: `✓ ty` (check mark, auto-hides after 3s)
- Failure: `✗ ty: failed` (error icon, stays visible)

### 4. Test Configuration Settings

**Open Settings** (`Cmd+,`) and search for "ty":

**Setting 1: `re-cue.ty.enabled`**
- Default: `true`
- Test: Set to `false`, reload window → Server should NOT start
- Reset to `true`, reload window → Server should start

**Setting 2: `re-cue.ty.path`**
- Default: `""` (auto-detect)
- Test: Set to `/Users/squick/Library/Python/3.9/bin/ty` → Should use this path
- Test: Set to `/invalid/path` → Should show error notification

### 5. Test Type Checking Features

Open `test_ty_lsp.py` and test these features:

#### A. Hover Information
Hover your mouse over:
- ✅ `greet` function → Should show function signature and return type
- ✅ `User` class → Should show class definition
- ✅ `result` variable → Should infer type as `str`
- ✅ `container` variable → Should show `Container[int]`

#### B. Diagnostics (Error Highlighting)
Look for red squiggly underlines on:
- Line 23: `return "not a number"` → Type mismatch error
- Line 50: `numbers.append("string")` → Type mismatch error
- Line 90: `Container("string")` → Generic type mismatch

**View Problems Panel:**
- Press `Cmd+Shift+M` or click "Problems" in bottom panel
- Should see ty diagnostics listed

#### C. IntelliSense / Autocomplete
Try typing in the file:
- Type `user.` → Should suggest `.name`, `.age`, `.get_info()`
- Type `container.` → Should suggest `.value`, `.get()`

### 6. Test Restart Command

**Manual Restart:**
1. Open Command Palette (`Cmd+Shift+P`)
2. Type "RE-cue: Restart ty Type Checker"
3. Execute command
4. Check output: Should see "Restarting ty language server..."
5. Should see "ty language server started successfully"

### 7. Test Edge Cases

#### Test with No ty Installed
```bash
# Temporarily rename ty
sudo mv /Users/squick/Library/Python/3.9/bin/ty /Users/squick/Library/Python/3.9/bin/ty.bak

# Reload VS Code window
# Expected: Warning notification "ty type checker not found"
# Expected: Link to installation instructions

# Restore ty
sudo mv /Users/squick/Library/Python/3.9/bin/ty.bak /Users/squick/Library/Python/3.9/bin/ty
```

#### Test with Virtual Environment
```bash
cd reverse-engineer-python
python3 -m venv test_venv
source test_venv/bin/activate
pip install ty

# Open a Python file
# Expected: ty should be found in test_venv/bin/ty
```

### 8. Test Extension Deactivation

1. Disable the RE-cue extension
2. Check output: Should see "ty language server stopped"
3. Re-enable extension
4. Check output: Should see "ty language server started successfully"

### 9. Check for Conflicts

**With Python Extension:**
- Both should run simultaneously without conflicts
- Pylance handles IntelliSense, ty handles type checking
- Check that both show diagnostics appropriately

### 10. Performance Testing

Open a large Python file (e.g., `reverse-engineer-python/reverse_engineer/analyzer.py`):
- Server should start quickly (< 5 seconds)
- Hover should be responsive (< 500ms)
- Diagnostics should appear within seconds

## Expected Results Summary

| Test | Expected Behavior | Status |
|------|------------------|--------|
| Server starts | Output shows "started successfully" | ⏳ |
| Status bar | Shows ✓ ty briefly | ⏳ |
| Hover works | Shows type information | ⏳ |
| Diagnostics | Shows type errors with red underlines | ⏳ |
| Settings work | Can enable/disable, set custom path | ⏳ |
| Restart works | Server restarts on command | ⏳ |
| No conflicts | Works alongside Python extension | ⏳ |
| Error handling | Graceful failure with notifications | ⏳ |

## Troubleshooting

### Server Won't Start
- Check ty is installed: `ty --version`
- Check output channel for errors
- Verify settings: `re-cue.ty.enabled` = `true`
- Try manual path in `re-cue.ty.path` setting

### No Diagnostics Showing
- Check ty supports LSP: Version must be >= 0.0.1a31 ✅
- Verify file is recognized as Python
- Check output for server errors
- Try restarting server with command

### Performance Issues
- Check CPU usage of ty process
- Large files may take longer to analyze
- Consider disabling for very large projects

## Success Criteria

✅ All 10 tests pass  
✅ No console errors in Developer Tools  
✅ Server stays running during normal usage  
✅ Provides useful type information  
✅ No conflicts with existing extensions  

## Next Steps After Testing

1. Document any bugs found
2. Test with real-world Python projects
3. Gather feedback on type checking usefulness
4. Consider adding more configuration options
5. Prepare for marketplace release

---

**Note**: ty is in alpha (0.0.1-alpha.31), so some features may be unstable. Report issues to https://github.com/astral-sh/ty

# RE-cue Troubleshooting Guide

**Last Updated**: November 9, 2025  
**Version**: 1.0

This guide helps you diagnose and resolve common issues when using RE-cue for reverse engineering Java/Spring Boot projects.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Analysis Errors](#analysis-errors)
3. [Performance Problems](#performance-problems)
4. [Output Quality Issues](#output-quality-issues)
5. [Business Context Problems](#business-context-problems)
6. [Phase Analysis Issues](#phased-analysis-issues)
7. [Common Error Messages](#common-error-messages)

---

## Installation Issues

### Problem: Module not found after installation

**Symptoms:**
```
ModuleNotFoundError: No module named 'reverse_engineer'
```

**Solutions:**
1. Verify installation:
   ```bash
   pip3 list | grep reverse-engineer
   ```

2. Reinstall in editable mode:
   ```bash
   cd reverse-engineer-python
   pip3 install -e .
   ```

3. Check Python path:
   ```bash
   python3 -c "import sys; print(sys.path)"
   ```

### Problem: Permission denied during installation

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**
1. Install for current user only:
   ```bash
   pip3 install --user -e .
   ```

2. Use virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

---

## Analysis Errors

### Problem: No endpoints discovered

**Symptoms:**
```
📍 Stage 1/8: Discovering API endpoints... ✓ Found 0 endpoints
```

**Causes:**
- Project doesn't use Spring annotations
- Files are in unexpected locations
- Test files being analyzed instead of source

**Solutions:**
1. Verify Spring annotations exist:
   ```bash
   grep -r "@RestController\|@Controller\|@GetMapping" /path/to/project/src/main
   ```

2. Check project structure:
   ```
   project/
   └── src/
       └── main/
           └── java/  ← Source code should be here
               └── com/example/...
   ```

3. Ensure you're pointing to project root:
   ```bash
   # Correct
   python3 -m reverse_engineer --use-cases /path/to/project
   
   # Incorrect (pointing to src directory)
   python3 -m reverse_engineer --use-cases /path/to/project/src
   ```

### Problem: Test files being analyzed

**Symptoms:**
- Many false positive endpoints
- Unexpected actors or boundaries
- Test-related classes in output

**Solutions:**
1. Verify test file exclusion is working:
   - Test files in `/src/test/` should be automatically excluded
   - Files with `Test.java`, `.test.`, `.spec.` patterns should be excluded

2. If still seeing test files, report location pattern:
   ```bash
   find /path/to/project -name "*Test*.java" -o -name "*.test.*"
   ```

### Problem: No actors discovered

**Symptoms:**
```
👥 Stage 6/8: Identifying actors... ✓ Found 0 actors
```

**Causes:**
- No Spring Security annotations in project
- No role-based access control
- Annotations in unexpected format

**Solutions:**
1. Check for security annotations:
   ```bash
   grep -r "@PreAuthorize\|@Secured\|@RolesAllowed" /path/to/project/src/main
   ```

2. If no security annotations exist, this is expected
   - RE-cue will still generate use cases
   - Actors will be generic ("User", "System")

3. Manually verify security configuration:
   ```bash
   find /path/to/project -name "*SecurityConfig.java" -o -name "application*.yml"
   ```

### Problem: Analysis crashes with encoding error

**Symptoms:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Solutions:**
1. Check file encodings:
   ```bash
   file /path/to/problematic/file.java
   ```

2. Convert files to UTF-8:
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 file.java > file_utf8.java
   ```

3. Temporarily skip problematic files by moving them out of analysis path

---

## Performance Problems

### Problem: Analysis takes too long

**Symptoms:**
- Analysis runs for > 5 minutes on medium-sized project (< 500 files)
- High CPU usage
- System becomes unresponsive

**Solutions:**
1. Use phased analysis for large projects:
   ```bash
   # Analyze in phases instead of all at once
   python3 -m reverse_engineer --phase 1 /path/to/project
   ```

2. Exclude unnecessary directories:
   ```bash
   # Remove build artifacts first
   rm -rf target/ build/ .gradle/
   ```

3. Monitor progress in verbose mode:
   ```bash
   python3 -m reverse_engineer --use-cases --verbose /path/to/project
   ```

### Problem: Out of memory errors

**Symptoms:**
```
MemoryError
killed
```

**Solutions:**
1. Increase available memory:
   ```bash
   # macOS/Linux
   ulimit -v unlimited
   
   # Or run with limited scope
   python3 -m reverse_engineer --phase 1 /path/to/project
   ```

2. Analyze smaller modules separately if multi-module project

3. Close other applications to free memory

---

## Output Quality Issues

### Problem: Use cases lack detail

**Symptoms:**
- Generic preconditions: "User must have appropriate permissions"
- Generic postconditions: "Operation completes successfully"
- No extension scenarios

**Causes:**
- No validation annotations in DTOs
- No `@Transactional` annotations
- Simple CRUD operations without business logic

**Solutions:**
1. Verify validation annotations exist:
   ```bash
   grep -r "@NotNull\|@Size\|@Email\|@Valid" /path/to/project/src/main
   ```

2. Check for transaction annotations:
   ```bash
   grep -r "@Transactional" /path/to/project/src/main
   ```

3. If annotations don't exist, this is expected behavior
   - RE-cue extracts what's available in the code
   - Consider adding validation annotations for better documentation

### Problem: Business context shows zero metrics

**Symptoms:**
```markdown
## Business Context

**Transaction Boundaries**: 0 identified
**Validation Rules**: 0 constraints
**Business Workflows**: 0 patterns
```

**Causes:**
- No Spring annotations in codebase
- Annotations in non-standard format
- Code uses different framework (not Spring Boot)

**Solutions:**
1. Verify Spring Boot project:
   ```bash
   grep -r "spring-boot" pom.xml build.gradle
   ```

2. Check for alternative frameworks:
   - If using Java EE: Look for `@Stateless`, `@PersistenceContext`
   - If using Quarkus: Look for `@ApplicationScoped`, `@Transactional`

3. RE-cue currently focuses on Spring Boot
   - Support for other frameworks is planned for future releases

### Problem: Actors have incorrect classifications

**Symptoms:**
- Admin role classified as "end_user"
- System service classified as "internal_user"

**Causes:**
- Non-standard role naming
- Custom security implementation

**Solutions:**
1. Check role naming:
   ```bash
   grep -r "ROLE_\|hasRole\|hasAuthority" /path/to/project/src/main
   ```

2. Role names should follow conventions:
   - `ADMIN`, `ADMINISTRATOR`, `ROOT` → internal_user with admin access
   - `USER`, `MEMBER`, `CUSTOMER` → end_user
   - `SYSTEM`, `SERVICE`, `API` → external_system

3. If using custom roles, classification may be generic
   - This is expected and doesn't affect functionality

---

## Business Context Problems

### Problem: Transaction detection misses @Transactional

**Symptoms:**
- Known `@Transactional` methods not counted
- Business context shows fewer transactions than expected

**Causes:**
- Annotation on interface instead of implementation
- Annotation inherited from parent class
- Non-standard annotation format

**Solutions:**
1. Verify annotation location:
   ```bash
   # Should be on method or class in implementation
   grep -B5 "@Transactional" /path/to/service/UserServiceImpl.java
   ```

2. Check annotation format:
   ```java
   // ✓ Supported
   @Transactional
   @Transactional(readOnly = true)
   @Transactional(propagation = Propagation.REQUIRES_NEW)
   
   // ✗ Not yet supported
   @Transactional(value = "txManager", propagation = Propagation.REQUIRED)
   ```

3. RE-cue analyzes implementation files, not interfaces

### Problem: Validation rules not extracted from DTOs

**Symptoms:**
- Known validation annotations not counted
- Use cases lack precondition details

**Causes:**
- Annotations on getters/setters instead of fields
- Custom validation annotations
- Validation groups not recognized

**Solutions:**
1. Verify annotation placement:
   ```java
   // ✓ Supported (field-level)
   @NotNull
   @Size(min = 3, max = 50)
   private String username;
   
   // ✗ Not yet supported (method-level)
   @NotNull
   public String getUsername() { return username; }
   ```

2. Check for standard annotations:
   - Supported: `@NotNull`, `@NotEmpty`, `@NotBlank`, `@Size`, `@Min`, `@Max`, `@Email`, `@Pattern`
   - Custom annotations: Not yet supported

---

## Phased Analysis Issues

### Problem: Cannot resume from Phase 2

**Symptoms:**
```
Error: Cannot find previous phase data
```

**Causes:**
- State file deleted or corrupted
- Different output directory used
- Project moved since last run

**Solutions:**
1. Check for state file:
   ```bash
   ls -la /path/to/output/.analysis_state.json
   ```

2. If missing, restart from Phase 1:
   ```bash
   python3 -m reverse_engineer --phase 1 /path/to/project
   ```

3. Ensure consistent output directory:
   ```bash
   # Use same directory for all phases
   python3 -m reverse_engineer --phase 1 --output ./output /path/to/project
   python3 -m reverse_engineer --phase 2 --output ./output /path/to/project
   ```

### Problem: Phase 4 shows "Prerequisites not loaded"

**Symptoms:**
```
Error: Phase 4 requires Phases 1-3 to be completed first
```

**Solutions:**
1. Phase 4 auto-loads prerequisites - this usually works automatically

2. If error persists, run phases in order:
   ```bash
   python3 -m reverse_engineer --phase 1 /path/to/project
   python3 -m reverse_engineer --phase 2 /path/to/project
   python3 -m reverse_engineer --phase 3 /path/to/project
   python3 -m reverse_engineer --phase 4 /path/to/project
   ```

3. Or run all phases at once:
   ```bash
   python3 -m reverse_engineer --phase all /path/to/project
   ```

---

## Common Error Messages

### "No Java files found in project"

**Problem**: RE-cue cannot find any `.java` files

**Solution**:
```bash
# Verify Java files exist
find /path/to/project -name "*.java" | head -10

# Check you're pointing to correct directory
ls -la /path/to/project/src/main/java
```

### "Failed to parse method signatures"

**Problem**: Java syntax error or unsupported language feature

**Solution**:
- RE-cue uses regex-based parsing, not full AST
- Complex generics or annotations may cause issues
- Analysis will continue, skipping problematic files
- Check verbose output to see which files were skipped

### "Cannot determine project type"

**Problem**: RE-cue cannot identify build system (Maven/Gradle)

**Solution**:
```bash
# Look for build files
ls -la /path/to/project/pom.xml
ls -la /path/to/project/build.gradle
```

RE-cue works without build files but some features require them

### "Insufficient permissions to write output"

**Problem**: Cannot write output files

**Solution**:
```bash
# Check directory permissions
ls -ld /path/to/output

# Create output directory if missing
mkdir -p /path/to/output
chmod 755 /path/to/output

# Or specify different output location
python3 -m reverse_engineer --output ~/Documents/analysis /path/to/project
```

---

## Getting More Help

### Enable Verbose Mode

Get detailed progress information:
```bash
python3 -m reverse_engineer --use-cases --verbose /path/to/project
```

### Check File Patterns

See what files RE-cue is analyzing:
```bash
find /path/to/project -name "*.java" | grep -v "/test/" | wc -l
```

### Review Generated Files

Check intermediate outputs:
```bash
ls -lh use-cases.md
cat use-cases.md | head -100
```

### Report Issues

If problems persist:

1. Gather information:
   ```bash
   python3 --version
   pip3 list | grep reverse
   find /path/to/project -name "*.java" | wc -l
   ```

2. Run with verbose output and save log:
   ```bash
   python3 -m reverse_engineer --use-cases --verbose /path/to/project 2>&1 | tee analysis.log
   ```

3. Create issue with:
   - Error message
   - Python version
   - RE-cue version
   - Project size (number of files)
   - Relevant log output

---

## Best Practices to Avoid Issues

1. **Always use project root directory**:
   ```bash
   # Correct
   python3 -m reverse_engineer /path/to/myproject
   
   # Incorrect
   python3 -m reverse_engineer /path/to/myproject/src/main/java
   ```

2. **Clean build artifacts first**:
   ```bash
   mvn clean
   # or
   ./gradlew clean
   ```

3. **Use phased analysis for large projects** (> 500 files)

4. **Keep output directory consistent** across phases

5. **Check file encodings** if working with legacy codebases

6. **Verify Spring Boot annotations** are in expected format

7. **Run from project root** where pom.xml or build.gradle exists

---

## Version-Specific Notes

### v1.0 (Current)
- Supports Spring Boot 2.x and 3.x
- Java 8, 11, 17, 21
- Maven and Gradle projects
- Focus on Spring annotations

### Upcoming Features
- Support for more frameworks (Quarkus, Micronaut)
- Better multi-module project handling
- Custom annotation support
- Performance improvements for large codebases

---

## Quick Reference

| Symptom | Quick Fix |
|---------|-----------|
| No endpoints found | Check Spring annotations exist |
| No actors found | Normal if no security annotations |
| Analysis too slow | Use phased mode (`--phase 1`) |
| Out of memory | Analyze modules separately |
| Test files analyzed | Move to `/src/test/` directory |
| State file missing | Restart from Phase 1 |
| Permission denied | Use `--output` to specify writable location |
| Encoding errors | Convert files to UTF-8 |
| No business context | Verify Spring Boot project |
| Missing dependencies | Reinstall: `pip3 install -e .` |

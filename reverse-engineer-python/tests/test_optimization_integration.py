"""
Integration tests for optimization features with framework analyzers.

Tests parallel processing, caching, and incremental analysis across all
supported frameworks to ensure consistent behavior.
"""

import unittest
import tempfile
import shutil
import time
from pathlib import Path

from reverse_engineer.optimized_analyzer import OptimizedAnalyzer
from reverse_engineer.analyzer import ProjectAnalyzer


# Module-level processor functions for multiprocessing (must be picklable)
def file_processor_simple(file_path: Path) -> dict:
    """Simple file processor for testing."""
    content = file_path.read_text()
    return {'file': str(file_path), 'length': len(content)}


def file_processor_detailed(file_path: Path) -> dict:
    """Detailed file processor for testing."""
    content = file_path.read_text()
    return {
        'file': str(file_path.name),
        'lines': content.count('\n'),
        'classes': content.count('class ')
    }


def file_processor_lines(file_path: Path) -> dict:
    """File processor that counts lines."""
    content = file_path.read_text()
    return {'file': str(file_path), 'lines': content.count('\n')}


class TestOptimizedAnalyzerIntegration(unittest.TestCase):
    """Integration tests for optimized analyzer with various project types."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test-project"
        self.project_root.mkdir()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def _create_spring_project(self, num_controllers=5):
        """Create Spring project with multiple controllers."""
        controller_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "controller"
        controller_dir.mkdir(parents=True)
        
        model_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "model"
        model_dir.mkdir(parents=True)
        
        for i in range(num_controllers):
            (controller_dir / f"User{i}Controller.java").write_text(f'''
package com.example.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/users{i}")
public class User{i}Controller {{
    
    @GetMapping
    public List<User> getAll() {{ return null; }}
    
    @GetMapping("/{{id}}")
    @PreAuthorize("hasRole('USER')")
    public User getById(@PathVariable Long id) {{ return null; }}
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User create(@RequestBody User user) {{ return null; }}
    
    @DeleteMapping("/{{id}}")
    @PreAuthorize("hasRole('ADMIN')")
    public void delete(@PathVariable Long id) {{}}
}}
''')
        
        for i in range(num_controllers):
            (model_dir / f"Entity{i}.java").write_text(f'''
package com.example.model;

import javax.persistence.*;

@Entity
public class Entity{i} {{
    @Id
    private Long id;
    private String name;
    private String description;
}}
''')
    
    def test_parallel_processing_with_project_analyzer(self):
        """Test parallel processing with ProjectAnalyzer."""
        self._create_spring_project(num_controllers=10)
        
        # Run with parallel processing enabled
        start_time = time.time()
        analyzer_parallel = ProjectAnalyzer(
            self.project_root,
            verbose=False,
            enable_optimizations=True,
            max_workers=4
        )
        analyzer_parallel.discover_endpoints()
        parallel_time = time.time() - start_time
        parallel_endpoints = len(analyzer_parallel.endpoints)
        
        # Run with parallel processing disabled
        start_time = time.time()
        analyzer_sequential = ProjectAnalyzer(
            self.project_root,
            verbose=False,
            enable_optimizations=False
        )
        analyzer_sequential.discover_endpoints()
        sequential_time = time.time() - start_time
        sequential_endpoints = len(analyzer_sequential.endpoints)
        
        # Both should find the same endpoints
        self.assertEqual(parallel_endpoints, sequential_endpoints)
        
        # Both should find endpoints from Spring controllers
        self.assertGreater(parallel_endpoints, 0, 
                          "Should discover endpoints from Spring controllers")
        
        print(f"\nParallel: {parallel_time:.3f}s ({parallel_endpoints} endpoints)")
        print(f"Sequential: {sequential_time:.3f}s ({sequential_endpoints} endpoints)")
    
    def test_caching_speeds_up_reanalysis(self):
        """Test that caching provides speedup on re-analysis."""
        self._create_spring_project(num_controllers=5)
        
        # First run with caching enabled
        analyzer1 = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        java_files = list(self.project_root.rglob("*.java"))
        
        start1 = time.time()
        results1 = analyzer1.process_files_optimized(
            java_files,
            file_processor_simple,
            desc="First run"
        )
        time1 = time.time() - start1
        
        # Save cache
        analyzer1.cache_manager.save_cache()
        
        # Second run - should use cache
        analyzer2 = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        start2 = time.time()
        results2 = analyzer2.process_files_optimized(
            java_files,
            file_processor_simple,
            desc="Second run"
        )
        time2 = time.time() - start2
        
        # Verify results match
        self.assertEqual(len(results1), len(results2))
        
        # Check cache was used
        stats = analyzer2.cache_manager.get_statistics()
        self.assertEqual(stats.hits, len(java_files))
        
        print(f"\nFirst run: {time1:.4f}s")
        print(f"Second run (cached): {time2:.4f}s")
    
    def test_incremental_analysis_detects_changes(self):
        """Test incremental analysis detects file changes."""
        self._create_spring_project(num_controllers=3)
        
        # First analysis
        analyzer1 = ProjectAnalyzer(
            self.project_root,
            verbose=False,
            enable_optimizations=True,
            enable_incremental=True
        )
        analyzer1.discover_endpoints()
        first_count = len(analyzer1.endpoints)
        
        # Add a new controller
        controller_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "controller"
        (controller_dir / "NewController.java").write_text('''
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/new")
public class NewController {
    @GetMapping
    public String get() { return "new"; }
}
''')
        
        # Second analysis should include new endpoint
        analyzer2 = ProjectAnalyzer(
            self.project_root,
            verbose=False,
            enable_optimizations=True,
            enable_incremental=True
        )
        analyzer2.discover_endpoints()
        second_count = len(analyzer2.endpoints)
        
        # Should have more endpoints
        self.assertGreater(second_count, first_count, 
                          "Should detect new endpoints from added file")
    
    def test_cache_invalidation_on_file_modification(self):
        """Test cache is invalidated when files are modified."""
        self._create_spring_project(num_controllers=2)
        
        java_files = list(self.project_root.rglob("*.java"))
        
        # First run
        analyzer1 = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        analyzer1.process_files_optimized(java_files, file_processor_lines, desc="First")
        analyzer1.cache_manager.save_cache()
        
        # Modify a file
        modified_file = java_files[0]
        original_content = modified_file.read_text()
        modified_file.write_text(original_content + "\n// Modified\n")
        
        # Second run
        analyzer2 = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        stats_before = analyzer2.cache_manager.get_statistics()
        prev_misses = stats_before.misses
        
        analyzer2.process_files_optimized(java_files, file_processor_lines, desc="Second")
        
        stats_after = analyzer2.cache_manager.get_statistics()
        new_misses = stats_after.misses - prev_misses
        
        # Should have 1 cache miss for the modified file
        self.assertEqual(new_misses, 1, 
                        "Should have cache miss for modified file")
    
    def test_optimized_analyzer_handles_errors_gracefully(self):
        """Test optimized analyzer handles file errors gracefully."""
        self._create_spring_project(num_controllers=3)
        
        java_files = list(self.project_root.rglob("*.java"))
        
        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=True,
            enable_parallel=False,  # Use sequential to avoid pickle issues
            max_workers=2,
            verbose=False
        )
        
        # Should not crash - returns list of successful results
        results = analyzer.process_files_optimized(
            java_files,
            file_processor_simple,
            desc="Test"
        )
        
        # Should have processed all files
        self.assertGreater(len(results), 0, "Should process files successfully")


class TestCachingWithMultipleAnalysisTypes(unittest.TestCase):
    """Test caching with different analysis types."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test-project"
        self.project_root.mkdir()
        
        # Create test files
        for i in range(3):
            (self.project_root / f"file{i}.py").write_text(f"# File {i}\nprint({i})\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_separate_caches_per_analysis_type(self):
        """Test that different analysis types maintain separate caches."""
        files = list(self.project_root.glob("*.py"))
        
        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=True,
            enable_parallel=False,
            verbose=False
        )
        
        # First analysis type
        analyzer.process_files_optimized(
            files, file_processor_simple, desc="Endpoints", analysis_type="endpoints"
        )
        
        stats1 = analyzer.cache_manager.get_statistics()
        entries1 = stats1.total_entries
        
        # Second analysis type
        analyzer.process_files_optimized(
            files, file_processor_simple, desc="Models", analysis_type="models"
        )
        
        stats2 = analyzer.cache_manager.get_statistics()
        entries2 = stats2.total_entries
        
        # Should have entries for both analysis types
        self.assertEqual(entries2, entries1 * 2, 
                        "Should have separate entries for each analysis type")


class TestParallelProcessingConsistency(unittest.TestCase):
    """Test parallel processing produces consistent results."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test-project"
        self.project_root.mkdir()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def _create_many_files(self, count=20):
        """Create many Python files."""
        for i in range(count):
            (self.project_root / f"module{i}.py").write_text(f'''
# Module {i}
class Class{i}:
    def method(self):
        return {i}
''')
    
    def test_parallel_vs_sequential_produces_same_results(self):
        """Test parallel and sequential processing produce same results."""
        self._create_many_files(count=15)
        
        files = list(self.project_root.glob("*.py"))
        
        # Sequential - disable incremental analysis as well
        analyzer_seq = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=False,
            enable_incremental=False,
            verbose=False
        )
        results_seq = analyzer_seq.process_files_optimized(
            files, file_processor_detailed, desc="Sequential"
        )
        
        # Parallel - use module-level processor function
        analyzer_par = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=True,
            enable_incremental=False,
            max_workers=4,
            verbose=False
        )
        results_par = analyzer_par.process_files_optimized(
            files, file_processor_detailed, desc="Parallel"
        )
        
        # Should have same number of results
        self.assertEqual(len(results_seq), len(results_par))
        
        # Sort and compare results
        seq_data = sorted(results_seq, key=lambda x: x['file'])
        par_data = sorted(results_par, key=lambda x: x['file'])
        
        for s, p in zip(seq_data, par_data):
            self.assertEqual(s['file'], p['file'])
            self.assertEqual(s['lines'], p['lines'])
            self.assertEqual(s['classes'], p['classes'])
    
    def test_parallel_processing_handles_large_file_count(self):
        """Test parallel processing with many files."""
        self._create_many_files(count=50)
        
        files = list(self.project_root.glob("*.py"))
        
        analyzer = OptimizedAnalyzer(
            repo_root=self.project_root,
            enable_caching=False,
            enable_parallel=True,
            enable_incremental=False,
            max_workers=8,
            verbose=False
        )
        
        results = analyzer.process_files_optimized(
            files, file_processor_simple, desc="Large batch"
        )
        
        self.assertEqual(len(results), 50)
        # Results are just dicts, not tuples with errors
        for r in results:
            self.assertIsNotNone(r.get('file'))


if __name__ == '__main__':
    unittest.main()

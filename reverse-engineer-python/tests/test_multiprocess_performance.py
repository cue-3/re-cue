"""
Performance benchmarks for multi-process analysis (ENH-PERF-004).

This module compares performance of parallel vs sequential processing.
"""

import tempfile
import time
import unittest
from pathlib import Path

from reverse_engineer.frameworks.java_spring.analyzer import JavaSpringAnalyzer


class TestMultiProcessPerformance(unittest.TestCase):
    """Performance benchmarks for multi-process analysis."""

    def setUp(self):
        """Set up test fixtures with a larger project."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a larger mock Spring Boot project
        self._create_large_mock_project()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_large_mock_project(self):
        """Create a mock Spring Boot project with many files."""
        # Create directory structure
        src_main_java = self.temp_path / "src" / "main" / "java" / "com" / "example"
        src_main_java.mkdir(parents=True, exist_ok=True)

        # Create controller directory
        controller_dir = src_main_java / "controller"
        controller_dir.mkdir(exist_ok=True)

        # Create model directory
        model_dir = src_main_java / "model"
        model_dir.mkdir(exist_ok=True)

        # Create service directory
        service_dir = src_main_java / "service"
        service_dir.mkdir(exist_ok=True)

        # Generate multiple controller files
        for i in range(20):
            controller_content = f"""
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/resource{i}")
public class Resource{i}Controller {{
    
    @GetMapping
    public List<Resource{i}> getAll() {{
        return service.getAll();
    }}
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public Resource{i} create(@RequestBody Resource{i} resource) {{
        return service.create(resource);
    }}
    
    @GetMapping("/{{id}}")
    public Resource{i} getById(@PathVariable Long id) {{
        return service.getById(id);
    }}
    
    @PutMapping("/{{id}}")
    @PreAuthorize("hasRole('MANAGER')")
    public Resource{i} update(@PathVariable Long id, @RequestBody Resource{i} resource) {{
        return service.update(id, resource);
    }}
    
    @DeleteMapping("/{{id}}")
    @Secured("ROLE_ADMIN")
    public void delete(@PathVariable Long id) {{
        service.delete(id);
    }}
}}
"""
            (controller_dir / f"Resource{i}Controller.java").write_text(controller_content)

        # Generate multiple model files
        for i in range(20):
            model_content = f"""
package com.example.model;

import javax.persistence.*;

@Entity
@Table(name = "resource{i}")
public class Resource{i} {{
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String description;
    private String field1;
    private String field2;
    private String field3;
    private Integer count;
    private Double value;
}}
"""
            (model_dir / f"Resource{i}.java").write_text(model_content)

        # Generate multiple service files
        for i in range(20):
            service_content = f"""
package com.example.service;

import org.springframework.stereotype.Service;

@Service
public class Resource{i}Service {{
    private Resource{i}Repository repository;
    
    public List<Resource{i}> getAll() {{
        return repository.findAll();
    }}
    
    public Resource{i} create(Resource{i} resource) {{
        return repository.save(resource);
    }}
    
    public Resource{i} getById(Long id) {{
        return repository.findById(id).orElseThrow();
    }}
    
    public Resource{i} update(Long id, Resource{i} resource) {{
        resource.setId(id);
        return repository.save(resource);
    }}
    
    public void delete(Long id) {{
        repository.deleteById(id);
    }}
}}
"""
            (service_dir / f"Resource{i}Service.java").write_text(service_content)

    def test_sequential_performance(self):
        """Benchmark sequential processing performance."""
        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=False,
        )

        start_time = time.time()
        endpoints = analyzer.discover_endpoints()
        models = analyzer.discover_models()
        services = analyzer.discover_services()
        sequential_time = time.time() - start_time

        print(f"\n  Sequential processing time: {sequential_time:.3f}s")
        print(f"  Discovered {len(endpoints)} endpoints, {len(models)} models, {len(services)} services")

        # Store for comparison
        self.sequential_time = sequential_time
        self.sequential_endpoints = len(endpoints)
        self.sequential_models = len(models)
        self.sequential_services = len(services)

    def test_parallel_performance(self):
        """Benchmark parallel processing performance."""
        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=True,
        )

        start_time = time.time()
        endpoints = analyzer.discover_endpoints()
        models = analyzer.discover_models()
        services = analyzer.discover_services()
        parallel_time = time.time() - start_time

        print(f"\n  Parallel processing time: {parallel_time:.3f}s")
        print(f"  Discovered {len(endpoints)} endpoints, {len(models)} models, {len(services)} services")

        # Store for comparison
        self.parallel_time = parallel_time
        self.parallel_endpoints = len(endpoints)
        self.parallel_models = len(models)
        self.parallel_services = len(services)

    def test_compare_performance(self):
        """Compare sequential vs parallel performance."""
        # Run sequential
        analyzer_seq = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=False,
        )
        start_seq = time.time()
        endpoints_seq = analyzer_seq.discover_endpoints()
        models_seq = analyzer_seq.discover_models()
        services_seq = analyzer_seq.discover_services()
        seq_time = time.time() - start_seq

        # Run parallel
        analyzer_par = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=True,
        )
        start_par = time.time()
        endpoints_par = analyzer_par.discover_endpoints()
        models_par = analyzer_par.discover_models()
        services_par = analyzer_par.discover_services()
        par_time = time.time() - start_par

        # Compare results
        self.assertEqual(len(endpoints_seq), len(endpoints_par))
        self.assertEqual(len(models_seq), len(models_par))
        self.assertEqual(len(services_seq), len(services_par))

        # Calculate speedup
        speedup = seq_time / par_time if par_time > 0 else 1.0

        print(f"\n  ======================================")
        print(f"  Performance Comparison")
        print(f"  ======================================")
        print(f"  Sequential time: {seq_time:.3f}s")
        print(f"  Parallel time:   {par_time:.3f}s")
        print(f"  Speedup:         {speedup:.2f}x")
        print(f"  ======================================")
        print(f"  Files processed: {len(endpoints_seq)} controllers, {len(models_seq)} models, {len(services_seq)} services")
        print(f"  ======================================")

        # Note: Parallel processing should be at least as fast (accounting for overhead on small datasets)
        # On larger datasets, we expect significant speedup
        # For this small test, we just verify it doesn't crash and produces same results

    def test_parallel_scaling_with_workers(self):
        """Test how performance scales with different worker counts."""
        worker_counts = [1, 2, 4]
        times = []

        for workers in worker_counts:
            analyzer = JavaSpringAnalyzer(
                self.temp_path,
                verbose=False,
                enable_parallel=True,
                max_workers=workers,
            )

            start_time = time.time()
            analyzer.discover_endpoints()
            analyzer.discover_models()
            analyzer.discover_services()
            elapsed = time.time() - start_time

            times.append(elapsed)
            print(f"\n  {workers} worker(s): {elapsed:.3f}s")

        print(f"\n  Scaling efficiency:")
        for i, workers in enumerate(worker_counts):
            if i > 0:
                baseline_ratio = worker_counts[i] / worker_counts[0]
                time_ratio = times[0] / times[i]
                efficiency = (time_ratio / baseline_ratio) * 100
                print(f"    {workers} workers: {efficiency:.1f}% efficient")


if __name__ == "__main__":
    # Run with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMultiProcessPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

"""
Unit tests for traceability domain models.
"""

import unittest
from reverse_engineer.domain import (
    CodeLink,
    TestLink,
    TraceabilityEntry,
    ImpactedItem,
    ImpactAnalysis,
    TraceabilityMatrix,
)


class TestCodeLink(unittest.TestCase):
    """Test CodeLink dataclass."""
    
    def test_code_link_creation(self):
        """Test creating a CodeLink."""
        link = CodeLink(
            file_path="src/controllers/UserController.java",
            component_name="UserController",
            component_type="controller",
            line_number=10,
            confidence=0.8,
            link_type="implements",
            evidence=["Keyword match: user"]
        )
        self.assertEqual(link.file_path, "src/controllers/UserController.java")
        self.assertEqual(link.component_name, "UserController")
        self.assertEqual(link.component_type, "controller")
        self.assertEqual(link.line_number, 10)
        self.assertEqual(link.confidence, 0.8)
        self.assertEqual(link.link_type, "implements")
        self.assertEqual(len(link.evidence), 1)
    
    def test_code_link_defaults(self):
        """Test CodeLink default values."""
        link = CodeLink(
            file_path="src/UserService.java",
            component_name="UserService",
            component_type="service"
        )
        self.assertIsNone(link.line_number)
        self.assertEqual(link.confidence, 1.0)
        self.assertEqual(link.link_type, "implements")
        self.assertEqual(link.evidence, [])


class TestTestLink(unittest.TestCase):
    """Test TestLink dataclass."""
    
    def test_test_link_creation(self):
        """Test creating a TestLink."""
        link = TestLink(
            file_path="tests/UserControllerTest.java",
            test_name="UserControllerTest",
            test_type="integration",
            line_number=25,
            covers_scenario="main",
            status="passing"
        )
        self.assertEqual(link.file_path, "tests/UserControllerTest.java")
        self.assertEqual(link.test_name, "UserControllerTest")
        self.assertEqual(link.test_type, "integration")
        self.assertEqual(link.line_number, 25)
        self.assertEqual(link.covers_scenario, "main")
        self.assertEqual(link.status, "passing")
    
    def test_test_link_defaults(self):
        """Test TestLink default values."""
        link = TestLink(
            file_path="tests/UserTest.java",
            test_name="UserTest",
            test_type="unit"
        )
        self.assertIsNone(link.line_number)
        self.assertEqual(link.covers_scenario, "main")
        self.assertEqual(link.status, "unknown")


class TestTraceabilityEntry(unittest.TestCase):
    """Test TraceabilityEntry dataclass."""
    
    def test_entry_creation(self):
        """Test creating a TraceabilityEntry."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin"
        )
        self.assertEqual(entry.use_case_id, "UC001")
        self.assertEqual(entry.use_case_name, "Create User")
        self.assertEqual(entry.primary_actor, "Admin")
        self.assertEqual(entry.code_links, [])
        self.assertEqual(entry.test_links, [])
    
    def test_entry_total_links(self):
        """Test total_links property."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            code_links=[
                CodeLink("f1", "c1", "controller"),
                CodeLink("f2", "c2", "service")
            ],
            test_links=[
                TestLink("t1", "test1", "unit")
            ]
        )
        self.assertEqual(entry.total_links, 3)
    
    def test_implementation_status_not_implemented(self):
        """Test implementation_status for no code links."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin"
        )
        self.assertEqual(entry.implementation_status, "not_implemented")
    
    def test_implementation_status_fully_implemented(self):
        """Test implementation_status for high coverage."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            code_links=[CodeLink("f1", "c1", "controller")],
            implementation_coverage=85.0
        )
        self.assertEqual(entry.implementation_status, "fully_implemented")
    
    def test_implementation_status_partially_implemented(self):
        """Test implementation_status for medium coverage."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            code_links=[CodeLink("f1", "c1", "controller")],
            implementation_coverage=50.0
        )
        self.assertEqual(entry.implementation_status, "partially_implemented")
    
    def test_test_status_untested(self):
        """Test test_status for no test links."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin"
        )
        self.assertEqual(entry.test_status, "untested")
    
    def test_test_status_well_tested(self):
        """Test test_status for high coverage."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            test_links=[TestLink("t1", "test1", "integration")],
            test_coverage=85.0
        )
        self.assertEqual(entry.test_status, "well_tested")


class TestImpactAnalysis(unittest.TestCase):
    """Test ImpactAnalysis dataclass."""
    
    def test_impact_analysis_creation(self):
        """Test creating an ImpactAnalysis."""
        analysis = ImpactAnalysis(
            changed_file="src/UserController.java",
            changed_component="UserController",
            component_type="controller"
        )
        self.assertEqual(analysis.changed_file, "src/UserController.java")
        self.assertEqual(analysis.changed_component, "UserController")
        self.assertEqual(analysis.component_type, "controller")
        self.assertEqual(analysis.impacted_use_cases, [])
        self.assertEqual(analysis.risk_level, "low")
    
    def test_total_impacts(self):
        """Test total_impacts property."""
        analysis = ImpactAnalysis(
            changed_file="src/UserController.java",
            changed_component="UserController",
            component_type="controller",
            impacted_use_cases=[
                ImpactedItem("use_case", "UC001", "Create User", "direct", "keyword")
            ],
            impacted_tests=[
                ImpactedItem("test", "t1", "UserTest", "direct", "name match")
            ]
        )
        self.assertEqual(analysis.total_impacts, 2)
    
    def test_assess_risk_low(self):
        """Test risk assessment - low."""
        analysis = ImpactAnalysis(
            changed_file="src/Helper.java",
            changed_component="Helper",
            component_type="utility"
        )
        self.assertEqual(analysis.assess_risk(), "low")
    
    def test_assess_risk_critical(self):
        """Test risk assessment - critical."""
        analysis = ImpactAnalysis(
            changed_file="src/UserController.java",
            changed_component="UserController",
            component_type="controller",
            impacted_use_cases=[
                ImpactedItem("use_case", "UC001", "Create User", "direct", "r1"),
                ImpactedItem("use_case", "UC002", "Update User", "direct", "r2"),
                ImpactedItem("use_case", "UC003", "Delete User", "direct", "r3"),
            ]
        )
        self.assertEqual(analysis.assess_risk(), "critical")


class TestTraceabilityMatrix(unittest.TestCase):
    """Test TraceabilityMatrix dataclass."""
    
    def test_matrix_creation(self):
        """Test creating a TraceabilityMatrix."""
        matrix = TraceabilityMatrix(project_name="TestProject")
        self.assertEqual(matrix.project_name, "TestProject")
        self.assertEqual(matrix.entries, [])
        self.assertEqual(matrix.total_use_cases, 0)
    
    def test_compute_metrics(self):
        """Test compute_metrics method."""
        entry1 = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            code_links=[CodeLink("f1", "c1", "controller")],
            test_links=[TestLink("t1", "test1", "unit")],
            implementation_coverage=80.0,
            test_coverage=60.0
        )
        entry2 = TraceabilityEntry(
            use_case_id="UC002",
            use_case_name="Delete User",
            primary_actor="Admin",
            implementation_coverage=40.0,
            test_coverage=20.0
        )
        
        matrix = TraceabilityMatrix(
            project_name="TestProject",
            entries=[entry1, entry2]
        )
        matrix.compute_metrics()
        
        self.assertEqual(matrix.total_use_cases, 2)
        self.assertEqual(matrix.implemented_use_cases, 1)
        self.assertEqual(matrix.tested_use_cases, 1)
        self.assertEqual(matrix.total_code_links, 1)
        self.assertEqual(matrix.total_test_links, 1)
        self.assertEqual(matrix.average_implementation_coverage, 60.0)
        self.assertEqual(matrix.average_test_coverage, 40.0)
    
    def test_get_entry(self):
        """Test get_entry method."""
        entry = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin"
        )
        matrix = TraceabilityMatrix(
            project_name="TestProject",
            entries=[entry]
        )
        
        found = matrix.get_entry("UC001")
        self.assertIsNotNone(found)
        self.assertEqual(found.use_case_id, "UC001")
        
        not_found = matrix.get_entry("UC999")
        self.assertIsNone(not_found)
    
    def test_get_unimplemented_use_cases(self):
        """Test get_unimplemented_use_cases method."""
        entry1 = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            code_links=[CodeLink("f1", "c1", "controller")]
        )
        entry2 = TraceabilityEntry(
            use_case_id="UC002",
            use_case_name="Delete User",
            primary_actor="Admin"
        )
        
        matrix = TraceabilityMatrix(
            project_name="TestProject",
            entries=[entry1, entry2]
        )
        
        unimplemented = matrix.get_unimplemented_use_cases()
        self.assertEqual(len(unimplemented), 1)
        self.assertEqual(unimplemented[0].use_case_id, "UC002")
    
    def test_get_untested_use_cases(self):
        """Test get_untested_use_cases method."""
        entry1 = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            test_links=[TestLink("t1", "test1", "unit")]
        )
        entry2 = TraceabilityEntry(
            use_case_id="UC002",
            use_case_name="Delete User",
            primary_actor="Admin"
        )
        
        matrix = TraceabilityMatrix(
            project_name="TestProject",
            entries=[entry1, entry2]
        )
        
        untested = matrix.get_untested_use_cases()
        self.assertEqual(len(untested), 1)
        self.assertEqual(untested[0].use_case_id, "UC002")
    
    def test_get_low_coverage_use_cases(self):
        """Test get_low_coverage_use_cases method."""
        entry1 = TraceabilityEntry(
            use_case_id="UC001",
            use_case_name="Create User",
            primary_actor="Admin",
            implementation_coverage=80.0,
            test_coverage=70.0
        )
        entry2 = TraceabilityEntry(
            use_case_id="UC002",
            use_case_name="Delete User",
            primary_actor="Admin",
            implementation_coverage=30.0,
            test_coverage=20.0
        )
        
        matrix = TraceabilityMatrix(
            project_name="TestProject",
            entries=[entry1, entry2]
        )
        
        low_coverage = matrix.get_low_coverage_use_cases(threshold=50.0)
        self.assertEqual(len(low_coverage), 1)
        self.assertEqual(low_coverage[0].use_case_id, "UC002")


if __name__ == "__main__":
    unittest.main()

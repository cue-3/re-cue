"""
Tests for JiraExporter - Export use cases to Jira issues.

Tests cover:
- Configuration validation
- Use case to Jira issue conversion
- Issue creation (mocked)
- Multiple use case export
- Error handling
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from reverse_engineer.domain import UseCase
from reverse_engineer.exporters.jira import JiraConfig, JiraIssueResult


class TestJiraConfig(unittest.TestCase):
    """Test JiraConfig dataclass."""

    def test_basic_config(self):
        """Test basic configuration creation."""
        config = JiraConfig(
            server="https://example.atlassian.net",
            username="user@example.com",
            api_token="token123",
            project_key="PROJ",
        )

        self.assertEqual(config.server, "https://example.atlassian.net")
        self.assertEqual(config.username, "user@example.com")
        self.assertEqual(config.api_token, "token123")
        self.assertEqual(config.project_key, "PROJ")
        self.assertEqual(config.issue_type, "Story")

    def test_config_with_custom_issue_type(self):
        """Test configuration with custom issue type."""
        config = JiraConfig(
            server="https://example.atlassian.net",
            username="user@example.com",
            api_token="token123",
            project_key="PROJ",
            issue_type="Task",
        )

        self.assertEqual(config.issue_type, "Task")

    def test_default_labels(self):
        """Test that default labels are set."""
        config = JiraConfig(
            server="https://example.atlassian.net",
            username="user@example.com",
            api_token="token123",
            project_key="PROJ",
        )

        self.assertEqual(config.labels, ["re-cue", "use-case"])

    def test_custom_labels(self):
        """Test configuration with custom labels."""
        config = JiraConfig(
            server="https://example.atlassian.net",
            username="user@example.com",
            api_token="token123",
            project_key="PROJ",
            labels=["custom", "labels"],
        )

        self.assertEqual(config.labels, ["custom", "labels"])


class TestJiraIssueResult(unittest.TestCase):
    """Test JiraIssueResult dataclass."""

    def test_success_result(self):
        """Test successful issue result."""
        result = JiraIssueResult(
            success=True,
            issue_key="PROJ-123",
            issue_url="https://example.atlassian.net/browse/PROJ-123",
            use_case_id="UC01",
            use_case_name="Create User Account",
        )

        self.assertTrue(result.success)
        self.assertEqual(result.issue_key, "PROJ-123")
        self.assertEqual(result.use_case_id, "UC01")

    def test_failure_result(self):
        """Test failed issue result."""
        result = JiraIssueResult(
            success=False,
            use_case_id="UC01",
            use_case_name="Create User Account",
            error_message="Connection failed",
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.issue_key)
        self.assertEqual(result.error_message, "Connection failed")


class TestJiraExporter(unittest.TestCase):
    """Test JiraExporter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = JiraConfig(
            server="https://example.atlassian.net",
            username="user@example.com",
            api_token="token123",
            project_key="PROJ",
        )

        # Mock the jira module before importing JiraExporter
        self.mock_jira_module = MagicMock()
        self.mock_JIRA = MagicMock()
        self.mock_JIRAError = type("JIRAError", (Exception,), {})
        self.mock_jira_module.JIRA = self.mock_JIRA
        self.mock_jira_module.exceptions.JIRAError = self.mock_JIRAError

        # Patch sys.modules to inject our mock
        self.jira_patcher = patch.dict("sys.modules", {"jira": self.mock_jira_module, "jira.exceptions": self.mock_jira_module.exceptions})
        self.jira_patcher.start()

        # Import JiraExporter after mocking
        from reverse_engineer.exporters.jira import JiraExporter

        self.JiraExporter = JiraExporter

    def tearDown(self):
        """Clean up patches."""
        self.jira_patcher.stop()

    def test_initialization(self):
        """Test exporter initialization."""
        exporter = self.JiraExporter(self.config)

        self.assertEqual(exporter.config, self.config)
        self.assertIsNone(exporter._client)

    def test_get_client_creates_connection(self):
        """Test that _get_client creates a JIRA connection."""
        mock_client = MagicMock()
        self.mock_JIRA.return_value = mock_client

        exporter = self.JiraExporter(self.config)
        client = exporter._get_client()

        self.assertEqual(client, mock_client)
        self.mock_JIRA.assert_called_once()

    def test_test_connection_success(self):
        """Test successful connection test."""
        mock_client = MagicMock()
        mock_client.server_info.return_value = {"version": "8.0.0"}
        self.mock_JIRA.return_value = mock_client

        exporter = self.JiraExporter(self.config)
        result = exporter.test_connection()

        self.assertTrue(result)
        mock_client.server_info.assert_called_once()

    def test_test_connection_failure(self):
        """Test failed connection test."""
        mock_client = MagicMock()
        mock_client.server_info.side_effect = Exception("Connection failed")
        self.mock_JIRA.return_value = mock_client

        exporter = self.JiraExporter(self.config)
        result = exporter.test_connection()

        self.assertFalse(result)

    def test_use_case_to_description(self):
        """Test conversion of use case to Jira description format."""
        use_case = UseCase(
            id="UC01",
            name="Create User Account",
            primary_actor="User",
            secondary_actors=["Email Service"],
            preconditions=["User is not logged in", "Registration is enabled"],
            postconditions=["User account is created", "Welcome email is sent"],
            main_scenario=[
                "User navigates to registration page",
                "User enters email and password",
                "System validates input",
                "System creates account",
                "System sends welcome email",
            ],
            extensions=["3a. Invalid email format - show error", "4a. Email already exists - show error"],
            identified_from=["UserController.register()", "RegistrationService.createAccount()"],
        )

        exporter = self.JiraExporter(self.config)
        description = exporter._use_case_to_description(use_case)

        # Check that key sections are present
        self.assertIn("*Primary Actor:* User", description)
        self.assertIn("*Secondary Actors:* Email Service", description)
        self.assertIn("h3. Preconditions", description)
        self.assertIn("User is not logged in", description)
        self.assertIn("h3. Postconditions", description)
        self.assertIn("User account is created", description)
        self.assertIn("h3. Main Scenario", description)
        self.assertIn("# User navigates to registration page", description)
        self.assertIn("h3. Extensions", description)
        self.assertIn("Invalid email format", description)
        self.assertIn("h3. Technical Context", description)
        self.assertIn("UserController.register()", description)

    def test_create_issue_from_use_case_success(self):
        """Test successful issue creation from use case."""
        mock_client = MagicMock()
        mock_issue = MagicMock()
        mock_issue.key = "PROJ-123"
        mock_client.create_issue.return_value = mock_issue
        self.mock_JIRA.return_value = mock_client

        use_case = UseCase(
            id="UC01",
            name="Create User Account",
            primary_actor="User",
            main_scenario=["User enters details", "System creates account"],
        )

        exporter = self.JiraExporter(self.config)
        result = exporter.create_issue_from_use_case(use_case)

        self.assertTrue(result.success)
        self.assertEqual(result.issue_key, "PROJ-123")
        self.assertEqual(result.use_case_id, "UC01")
        self.assertEqual(result.use_case_name, "Create User Account")
        self.assertIn("/browse/PROJ-123", result.issue_url)

        # Verify create_issue was called with correct parameters
        mock_client.create_issue.assert_called_once()
        call_args = mock_client.create_issue.call_args
        fields = call_args[1]["fields"]
        self.assertEqual(fields["project"]["key"], "PROJ")
        self.assertEqual(fields["summary"], "Create User Account")
        self.assertEqual(fields["issuetype"]["name"], "Story")
        self.assertIn("re-cue", fields["labels"])
        self.assertIn("uc-uc01", fields["labels"])

    def test_create_issue_from_use_case_failure(self):
        """Test failed issue creation from use case."""
        mock_client = MagicMock()
        mock_client.create_issue.side_effect = Exception("Permission denied")
        self.mock_JIRA.return_value = mock_client

        use_case = UseCase(
            id="UC01",
            name="Create User Account",
            primary_actor="User",
        )

        exporter = self.JiraExporter(self.config)
        result = exporter.create_issue_from_use_case(use_case)

        self.assertFalse(result.success)
        self.assertIsNone(result.issue_key)
        self.assertIn("Permission denied", result.error_message)

    def test_export_multiple_use_cases(self):
        """Test exporting multiple use cases."""
        mock_client = MagicMock()
        mock_issue1 = MagicMock()
        mock_issue1.key = "PROJ-123"
        mock_issue2 = MagicMock()
        mock_issue2.key = "PROJ-124"
        mock_client.create_issue.side_effect = [mock_issue1, mock_issue2]
        self.mock_JIRA.return_value = mock_client

        use_cases = [
            UseCase(id="UC01", name="Create User", primary_actor="User"),
            UseCase(id="UC02", name="Delete User", primary_actor="Admin"),
        ]

        exporter = self.JiraExporter(self.config)
        results = exporter.export_use_cases(use_cases)

        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.success for r in results))
        self.assertEqual(results[0].issue_key, "PROJ-123")
        self.assertEqual(results[1].issue_key, "PROJ-124")


if __name__ == "__main__":
    unittest.main()

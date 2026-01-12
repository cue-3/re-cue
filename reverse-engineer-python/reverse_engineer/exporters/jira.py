"""
JiraExporter - Export use cases to Jira issues.

This module provides functionality to:
- Convert use cases to Jira issues
- Create issues via Jira REST API using jira-python library
- Handle authentication (API Token)
- Map use case components to Jira issue fields
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from ..domain import UseCase

logger = logging.getLogger(__name__)


@dataclass
class JiraConfig:
    """Configuration for Jira connection and issue settings."""

    server: str
    """Jira server URL (e.g., https://your-domain.atlassian.net)"""

    username: str
    """Username or email for authentication"""

    api_token: str
    """API token for authentication"""

    project_key: str
    """Jira project key where issues will be created"""

    issue_type: str = "Story"
    """Issue type for created issues (Story, Task, Epic, etc.)"""

    epic_link_field: Optional[str] = None
    """Custom field ID for Epic Link (e.g., 'customfield_10014')"""

    labels: list[str] = field(default_factory=lambda: ["re-cue", "use-case"])
    """Labels to add to created issues"""

    verify_ssl: bool = True
    """Whether to verify SSL certificates"""


@dataclass
class JiraIssueResult:
    """Result of a Jira issue creation operation."""

    success: bool
    issue_key: Optional[str] = None
    issue_url: Optional[str] = None
    use_case_id: str = ""
    use_case_name: str = ""
    error_message: Optional[str] = None


class JiraExporter:
    """Export use cases to Jira as issues."""

    def __init__(self, config: JiraConfig):
        """
        Initialize Jira exporter with configuration.

        Args:
            config: JiraConfig with connection details

        Raises:
            ImportError: If jira library is not installed
        """
        try:
            from jira import JIRA
            from jira.exceptions import JIRAError

            self.JIRA = JIRA
            self.JIRAError = JIRAError
        except ImportError as e:
            raise ImportError(
                "The 'jira' library is required for Jira integration. "
                "Install it with: pip install jira>=3.0.0"
            ) from e

        self.config = config
        self._client: Optional[Any] = None
        logger.info("JiraExporter initialized for server: %s", config.server)

    def _get_client(self) -> Any:
        """
        Get or create Jira client connection.

        Returns:
            JIRA client instance

        Raises:
            JIRAError: If connection fails
        """
        if self._client is None:
            logger.info("Connecting to Jira server: %s", self.config.server)
            options = {"server": self.config.server, "verify": self.config.verify_ssl}

            self._client = self.JIRA(
                options=options,
                basic_auth=(self.config.username, self.config.api_token),
            )
            logger.info("Successfully connected to Jira")

        return self._client

    def test_connection(self) -> bool:
        """
        Test connection to Jira server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            client = self._get_client()
            # Try to get server info to verify connection
            _ = client.server_info()
            logger.info("Jira connection test successful")
            return True
        except self.JIRAError as e:
            logger.error("Jira connection test failed: %s", e)
            return False
        except Exception as e:
            logger.error("Unexpected error testing Jira connection: %s", e)
            return False

    def _use_case_to_description(self, use_case: UseCase) -> str:
        """
        Convert use case to Jira description format.

        Args:
            use_case: UseCase to convert

        Returns:
            Formatted description string
        """
        lines = []

        # Primary Actor
        lines.append(f"*Primary Actor:* {use_case.primary_actor}")

        # Secondary Actors
        if use_case.secondary_actors:
            lines.append(f"*Secondary Actors:* {', '.join(use_case.secondary_actors)}")

        # Preconditions
        if use_case.preconditions:
            lines.append("")
            lines.append("h3. Preconditions")
            for precondition in use_case.preconditions:
                lines.append(f"* {precondition}")

        # Postconditions
        if use_case.postconditions:
            lines.append("")
            lines.append("h3. Postconditions")
            for postcondition in use_case.postconditions:
                lines.append(f"* {postcondition}")

        # Main Scenario
        if use_case.main_scenario:
            lines.append("")
            lines.append("h3. Main Scenario")
            for _i, step in enumerate(use_case.main_scenario, 1):
                lines.append(f"# {step}")

        # Extensions
        if use_case.extensions:
            lines.append("")
            lines.append("h3. Extensions")
            for extension in use_case.extensions:
                lines.append(f"* {extension}")

        # Identified From (as additional context)
        if use_case.identified_from:
            lines.append("")
            lines.append("h3. Technical Context")
            lines.append("Identified from:")
            for source in use_case.identified_from[:5]:  # Limit to first 5
                lines.append(f"* {{code}}{source}{{code}}")

        return "\n".join(lines)

    def create_issue_from_use_case(self, use_case: UseCase) -> JiraIssueResult:
        """
        Create a Jira issue from a use case.

        Args:
            use_case: UseCase to convert to issue

        Returns:
            JiraIssueResult with creation status
        """
        try:
            client = self._get_client()

            # Build issue fields
            issue_dict = {
                "project": {"key": self.config.project_key},
                "summary": use_case.name,
                "description": self._use_case_to_description(use_case),
                "issuetype": {"name": self.config.issue_type},
            }

            # Add labels
            if self.config.labels:
                issue_dict["labels"] = self.config.labels.copy()
                # Add use case ID as a label (sanitized)
                sanitized_id = use_case.id.replace(" ", "-").lower()
                issue_dict["labels"].append(f"uc-{sanitized_id}")

            logger.info("Creating Jira issue for use case: %s", use_case.name)
            issue = client.create_issue(fields=issue_dict)

            issue_url = f"{self.config.server}/browse/{issue.key}"
            logger.info("Successfully created issue: %s", issue.key)

            return JiraIssueResult(
                success=True,
                issue_key=issue.key,
                issue_url=issue_url,
                use_case_id=use_case.id,
                use_case_name=use_case.name,
            )

        except self.JIRAError as e:
            error_msg = f"Jira API error: {e}"
            logger.error("Failed to create issue for %s: %s", use_case.name, error_msg)
            return JiraIssueResult(
                success=False,
                use_case_id=use_case.id,
                use_case_name=use_case.name,
                error_message=error_msg,
            )
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error("Failed to create issue for %s: %s", use_case.name, error_msg)
            return JiraIssueResult(
                success=False,
                use_case_id=use_case.id,
                use_case_name=use_case.name,
                error_message=error_msg,
            )

    def export_use_cases(self, use_cases: list[UseCase]) -> list[JiraIssueResult]:
        """
        Export multiple use cases as Jira issues.

        Args:
            use_cases: List of UseCases to export

        Returns:
            List of JiraIssueResult objects
        """
        results = []

        for use_case in use_cases:
            result = self.create_issue_from_use_case(use_case)
            results.append(result)

        return results

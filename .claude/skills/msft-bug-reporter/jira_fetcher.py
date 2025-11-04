"""
JIRA Fetcher Module

Fetches JIRA issue data via Atlassian MCP integration and extracts
relevant fields for Microsoft bug report generation.

This module handles:
- JIRA ticket key extraction from various formats
- MCP integration for data retrieval
- Field extraction and normalization
- Missing/null field handling
"""

from typing import Dict, Any, Optional, Tuple
import re
from datetime import datetime


class JiraFetcher:
    """
    Handles fetching and parsing JIRA issue data for Microsoft bug reports.

    This class provides methods to:
    1. Extract JIRA keys from various input formats
    2. Fetch issue data via Atlassian MCP
    3. Extract and normalize relevant fields
    4. Handle missing or incomplete data gracefully
    """

    # Regex patterns for JIRA key extraction
    JIRA_KEY_PATTERN = re.compile(r'([A-Z]{2,10}-\d+)', re.IGNORECASE)
    JIRA_URL_PATTERN = re.compile(
        r'https?://[^/]+/browse/([A-Z]{2,10}-\d+)',
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize the JIRA fetcher with compiled regex patterns."""
        self.last_fetch_timestamp: Optional[str] = None
        self.last_jira_key: Optional[str] = None

    def extract_jira_key(self, user_input: str) -> Optional[str]:
        """
        Extract JIRA issue key from various input formats.

        Supported formats:
        - JIRA-1234
        - https://company.atlassian.net/browse/JIRA-1234
        - "Create bug report from JIRA-1234"

        Args:
            user_input: Raw user input containing JIRA reference

        Returns:
            Extracted JIRA key (e.g., "JIRA-1234") or None if not found

        Examples:
            >>> fetcher = JiraFetcher()
            >>> fetcher.extract_jira_key("JIRA-1234")
            'JIRA-1234'
            >>> fetcher.extract_jira_key("https://company.atlassian.net/browse/PROJ-567")
            'PROJ-567'
        """
        # Try URL pattern first (more specific)
        url_match = self.JIRA_URL_PATTERN.search(user_input)
        if url_match:
            return url_match.group(1).upper()

        # Fall back to key pattern
        key_match = self.JIRA_KEY_PATTERN.search(user_input)
        if key_match:
            return key_match.group(1).upper()

        return None

    def fetch_jira_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Fetch JIRA issue data via Atlassian MCP integration.

        This method calls the MCP tool to retrieve issue data and
        normalizes it into a standard structure for processing.

        Args:
            issue_key: JIRA issue key (e.g., "JIRA-1234")

        Returns:
            Dictionary containing normalized JIRA issue data with keys:
            - jira_key: str
            - title: str
            - description: str
            - steps_to_reproduce: str
            - expected_behavior: str
            - actual_behavior: str
            - environment: Dict[str, str]
            - priority: str
            - severity: str
            - attachments: List[Dict]
            - custom_fields: Dict[str, Any]
            - fetch_timestamp: str

        Raises:
            ValueError: If issue_key is invalid or issue not found
            RuntimeError: If MCP integration fails
        """
        if not issue_key or not self.JIRA_KEY_PATTERN.match(issue_key):
            raise ValueError(f"Invalid JIRA key format: {issue_key}")

        self.last_jira_key = issue_key
        self.last_fetch_timestamp = datetime.now().isoformat()

        # NOTE: In actual Claude Code execution, this would call:
        # mcp__atlassian__jira_get_issue(issue_key=issue_key)
        # For now, we'll document the expected structure

        # The MCP tool returns issue data that needs to be normalized
        # This is a placeholder showing the expected flow

        try:
            # Placeholder for MCP call - Claude Code will execute this
            # raw_issue = mcp__atlassian__jira_get_issue(issue_key=issue_key)

            # For development/testing, return a structure that shows
            # what the normalization would produce
            normalized_data = self._normalize_jira_data({
                'key': issue_key,
                'fields': {
                    'summary': '',
                    'description': '',
                    'priority': {'name': 'Medium'},
                    'customfields': {}
                }
            })

            return normalized_data

        except Exception as e:
            raise RuntimeError(f"Failed to fetch JIRA issue {issue_key}: {str(e)}")

    def _normalize_jira_data(self, raw_issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw JIRA API response into standard structure.

        Args:
            raw_issue: Raw JIRA issue data from MCP

        Returns:
            Normalized data dictionary
        """
        fields = raw_issue.get('fields', {})

        # Extract basic fields with safe defaults
        normalized = {
            'jira_key': raw_issue.get('key', self.last_jira_key),
            'title': fields.get('summary', ''),
            'description': fields.get('description', ''),
            'fetch_timestamp': self.last_fetch_timestamp,
        }

        # Extract priority and severity
        priority_obj = fields.get('priority', {})
        normalized['priority'] = priority_obj.get('name', 'Medium') if priority_obj else 'Medium'

        # Extract environment information
        normalized['environment'] = self._extract_environment(fields)

        # Try to extract structured fields (may be in custom fields)
        normalized.update(self._extract_structured_fields(fields))

        # Extract attachments
        normalized['attachments'] = self._extract_attachments(fields)

        # Store custom fields for potential later use
        normalized['custom_fields'] = self._extract_custom_fields(fields)

        return normalized

    def _extract_environment(self, fields: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract environment information from JIRA fields.

        Args:
            fields: JIRA fields dictionary

        Returns:
            Dictionary with environment details (os, dotnet_version, azure_service, etc.)
        """
        env_text = fields.get('environment', '')

        # Parse environment text for common patterns
        environment = {
            'os': self._extract_pattern(env_text, r'OS:\s*([^\n]+)'),
            'dotnet_version': self._extract_pattern(env_text, r'\.NET\s+(?:Version|Framework)?:?\s*([^\n]+)'),
            'azure_service': self._extract_pattern(env_text, r'Azure\s+Service:?\s*([^\n]+)'),
            'raw_environment': env_text
        }

        return {k: v for k, v in environment.items() if v}

    def _extract_structured_fields(self, fields: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract structured fields like steps to reproduce, expected/actual behavior.

        These might be in custom fields or embedded in description.

        Args:
            fields: JIRA fields dictionary

        Returns:
            Dictionary with steps_to_reproduce, expected_behavior, actual_behavior
        """
        description = fields.get('description', '')

        return {
            'steps_to_reproduce': self._extract_section(description, 'Steps to Reproduce'),
            'expected_behavior': self._extract_section(description, 'Expected Behavior'),
            'actual_behavior': self._extract_section(description, 'Actual Behavior'),
        }

    def _extract_section(self, text: str, section_name: str) -> str:
        """
        Extract a specific section from formatted text.

        Args:
            text: Source text (e.g., JIRA description)
            section_name: Section header to find

        Returns:
            Extracted section content or empty string
        """
        if not text:
            return ''

        # Try various header formats
        patterns = [
            rf'##\s*{re.escape(section_name)}[:\s]*\n(.*?)(?=\n##|\Z)',  # Markdown
            rf'{re.escape(section_name)}[:\s]*\n(.*?)(?=\n[A-Z][a-z]+:|\Z)',  # Plain text
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()

        return ''

    def _extract_pattern(self, text: str, pattern: str) -> str:
        """
        Extract text matching a regex pattern.

        Args:
            text: Source text
            pattern: Regex pattern with one capture group

        Returns:
            Matched text or empty string
        """
        if not text:
            return ''

        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ''

    def _extract_attachments(self, fields: Dict[str, Any]) -> list:
        """
        Extract attachment metadata from JIRA fields.

        Args:
            fields: JIRA fields dictionary

        Returns:
            List of attachment dictionaries with filename, size, type
        """
        attachments = fields.get('attachment', [])

        if not isinstance(attachments, list):
            return []

        return [
            {
                'filename': att.get('filename', 'unknown'),
                'size': att.get('size', 0),
                'mime_type': att.get('mimeType', 'unknown'),
                'url': att.get('content', '')
            }
            for att in attachments
        ]

    def _extract_custom_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract custom fields from JIRA issue.

        Args:
            fields: JIRA fields dictionary

        Returns:
            Dictionary of custom field values
        """
        custom_fields = {}

        for key, value in fields.items():
            if key.startswith('customfield_'):
                custom_fields[key] = value

        return custom_fields

    def validate_jira_data(self, jira_data: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate that fetched JIRA data has minimum required fields.

        Args:
            jira_data: Normalized JIRA data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        if not jira_data.get('jira_key'):
            errors.append("Missing JIRA key")

        if not jira_data.get('title'):
            errors.append("Missing title/summary")

        if not jira_data.get('description'):
            errors.append("Missing description")

        # Warn about recommended fields
        if not jira_data.get('steps_to_reproduce'):
            errors.append("Warning: Missing steps to reproduce (recommended)")

        if not jira_data.get('expected_behavior'):
            errors.append("Warning: Missing expected behavior (recommended)")

        return len([e for e in errors if not e.startswith('Warning')]) == 0, errors


# Helper function for easy import
def fetch_jira_issue(issue_key: str) -> Dict[str, Any]:
    """
    Convenience function to fetch JIRA issue data.

    Args:
        issue_key: JIRA issue key (e.g., "JIRA-1234")

    Returns:
        Normalized JIRA issue data dictionary
    """
    fetcher = JiraFetcher()
    return fetcher.fetch_jira_issue(issue_key)

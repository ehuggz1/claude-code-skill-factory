"""
Microsoft Template Module

Formats sanitized bug data into Microsoft GitHub bug report markdown template.

This module handles:
- Microsoft-standard bug report structure
- Proper markdown formatting
- Missing field handling
- Metadata inclusion
- Code block and list formatting
"""

from typing import Dict, Any, List
from datetime import datetime


class MicrosoftTemplate:
    """
    Generates Microsoft GitHub-compliant bug report markdown.

    Formats bug data according to Microsoft's standard bug report structure
    with proper markdown syntax and complete metadata.
    """

    def __init__(self):
        """Initialize the template generator."""
        self.template_version = "1.0"

    def generate_public_report(
        self,
        jira_data: Dict[str, Any],
        sanitization_summary: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate public Microsoft GitHub bug report.

        Args:
            jira_data: Sanitized JIRA issue data
            sanitization_summary: Summary of sanitization actions
            metadata: Additional metadata (timestamp, completeness, etc.)

        Returns:
            Formatted markdown string for public GitHub issue
        """
        sections = []

        # Header with metadata
        sections.append(self._generate_header(jira_data, metadata, sanitization_summary))

        # Title
        title = jira_data.get('title', 'Untitled Bug Report')
        sections.append(f"# {title}\n")

        # Description
        sections.append(self._generate_description(jira_data))

        # Steps to Reproduce
        sections.append(self._generate_steps(jira_data))

        # Expected Behavior
        sections.append(self._generate_expected_behavior(jira_data))

        # Actual Behavior
        sections.append(self._generate_actual_behavior(jira_data))

        # Environment
        sections.append(self._generate_environment(jira_data))

        # Additional Context
        sections.append(self._generate_additional_context(jira_data))

        # Footer
        sections.append(self._generate_footer(jira_data))

        return "\n".join(sections)

    def generate_private_report(
        self,
        jira_data: Dict[str, Any],
        private_data: Dict[str, List[str]],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate private Azure-specific information report.

        Args:
            jira_data: Original (unsanitized) JIRA issue data
            private_data: Dictionary of removed private information
            metadata: Additional metadata

        Returns:
            Formatted markdown string for private report
        """
        sections = []

        # Warning header
        sections.append("# ⚠️ PRIVATE - Azure Specific Information")
        sections.append("# " + "="*60)
        sections.append("# CONFIDENTIAL - DO NOT UPLOAD TO PUBLIC REPOSITORIES")
        sections.append("# " + "="*60 + "\n")

        # Metadata
        jira_key = jira_data.get('jira_key', 'UNKNOWN')
        title = jira_data.get('title', 'Untitled')
        sections.append(f"**Bug Title**: {title}")
        sections.append(f"**JIRA Reference**: {jira_key}")
        sections.append(f"**Date Created**: {metadata.get('timestamp', datetime.now().isoformat())}")
        sections.append(f"**Public Report**: msft-bug-{jira_key.lower()}.md\n")

        # Azure Resource Information
        if private_data.get('azure_subscriptions') or private_data.get('azure_resources'):
            sections.append("## Azure Resource Information\n")

            if private_data.get('azure_subscriptions'):
                sections.append("### Subscription IDs")
                for sub_id in private_data['azure_subscriptions']:
                    sections.append(f"- `{sub_id}`")
                sections.append("")

            if private_data.get('azure_resources'):
                sections.append("### Resource Names")
                for resource in private_data['azure_resources']:
                    sections.append(f"- `{resource}`")
                sections.append("")

        # Internal URLs/Paths
        if private_data.get('internal_urls') or private_data.get('file_paths'):
            sections.append("## Internal URLs and Paths\n")

            if private_data.get('internal_urls'):
                sections.append("### Internal URLs")
                for url in private_data['internal_urls']:
                    sections.append(f"- `{url}`")
                sections.append("")

            if private_data.get('file_paths'):
                sections.append("### File Paths")
                for path in private_data['file_paths']:
                    sections.append(f"- `{path}`")
                sections.append("")

        # Contact Information
        if private_data.get('emails') or private_data.get('ip_addresses'):
            sections.append("## Contact and Network Information\n")

            if private_data.get('emails'):
                sections.append("### Email Addresses")
                for email in private_data['emails']:
                    sections.append(f"- `{email}`")
                sections.append("")

            if private_data.get('ip_addresses'):
                sections.append("### IP Addresses")
                for ip in private_data['ip_addresses']:
                    sections.append(f"- `{ip}`")
                sections.append("")

        # Credentials (note: these should be masked even in private report)
        if private_data.get('credentials'):
            sections.append("## Credentials Detected\n")
            sections.append("**Note**: Actual credential values are not stored for security.")
            sections.append(f"- {len(private_data['credentials'])} credential(s) were detected and removed\n")

        # Environment details
        environment = jira_data.get('environment', {})
        if environment:
            sections.append("## Full Environment Details\n")
            raw_env = environment.get('raw_environment', '')
            if raw_env:
                sections.append("```")
                sections.append(raw_env)
                sections.append("```\n")

        # Instructions for use
        sections.append("## How to Use This Information\n")
        sections.append("This private report contains sensitive information that should be shared only through:")
        sections.append("1. Microsoft Support case submission (secure channels)")
        sections.append("2. Direct communication with Microsoft engineers under NDA")
        sections.append("3. Internal tracking systems (never commit to public repositories)\n")

        sections.append("**DO NOT**:")
        sections.append("- Upload this file to public GitHub repositories")
        sections.append("- Share in public forums or chat channels")
        sections.append("- Include in screenshots or screen recordings\n")

        # Footer
        sections.append("---")
        sections.append(f"*Generated: {datetime.now().isoformat()}*")
        sections.append(f"*From JIRA: {jira_key}*")
        sections.append("*This file contains sensitive information. Handle with care.*")

        return "\n".join(sections)

    def _generate_header(
        self,
        jira_data: Dict[str, Any],
        metadata: Dict[str, Any],
        sanitization_summary: str
    ) -> str:
        """Generate metadata header."""
        jira_key = jira_data.get('jira_key', 'UNKNOWN')
        timestamp = metadata.get('timestamp', datetime.now().isoformat())
        completeness = metadata.get('completeness_score', 'N/A')

        header = [
            "<!--",
            "Microsoft Bug Report",
            f"JIRA Reference: {jira_key}",
            f"Generated: {timestamp}",
            f"Field Completeness: {completeness}",
            "",
            "Sanitization Applied:",
            sanitization_summary,
            "-->\n"
        ]

        return "\n".join(header)

    def _generate_description(self, jira_data: Dict[str, Any]) -> str:
        """Generate description section."""
        description = jira_data.get('description', '')

        if not description:
            return "## Description\n\n*No description provided*\n"

        return f"## Description\n\n{description}\n"

    def _generate_steps(self, jira_data: Dict[str, Any]) -> str:
        """Generate steps to reproduce section."""
        steps = jira_data.get('steps_to_reproduce', '')

        section = ["## Steps to Reproduce\n"]

        if not steps:
            section.append("1. *Steps not provided*")
        else:
            # Check if steps are already formatted as a list
            if self._is_formatted_list(steps):
                section.append(steps)
            else:
                # Convert to numbered list if plain text
                section.append(self._format_as_numbered_list(steps))

        section.append("")
        return "\n".join(section)

    def _generate_expected_behavior(self, jira_data: Dict[str, Any]) -> str:
        """Generate expected behavior section."""
        expected = jira_data.get('expected_behavior', '')

        if not expected:
            return "## Expected Behavior\n\n*Expected behavior not specified*\n"

        return f"## Expected Behavior\n\n{expected}\n"

    def _generate_actual_behavior(self, jira_data: Dict[str, Any]) -> str:
        """Generate actual behavior section."""
        actual = jira_data.get('actual_behavior', '')

        if not actual:
            return "## Actual Behavior\n\n*Actual behavior not specified*\n"

        return f"## Actual Behavior\n\n{actual}\n"

    def _generate_environment(self, jira_data: Dict[str, Any]) -> str:
        """Generate environment section."""
        environment = jira_data.get('environment', {})

        section = ["## Environment\n"]

        if not environment or not isinstance(environment, dict):
            section.append("*Environment information not provided*\n")
            return "\n".join(section)

        # Format environment as bullet list
        if environment.get('os'):
            section.append(f"- **Operating System**: {environment['os']}")

        if environment.get('dotnet_version'):
            section.append(f"- **.NET Version**: {environment['dotnet_version']}")

        if environment.get('azure_service'):
            section.append(f"- **Azure Service**: {environment['azure_service']}")

        # Add any other environment fields
        for key, value in environment.items():
            if key not in ['os', 'dotnet_version', 'azure_service', 'raw_environment'] and value:
                formatted_key = key.replace('_', ' ').title()
                section.append(f"- **{formatted_key}**: {value}")

        section.append("")
        return "\n".join(section)

    def _generate_additional_context(self, jira_data: Dict[str, Any]) -> str:
        """Generate additional context section."""
        section = ["## Additional Context\n"]

        # Priority/Severity
        priority = jira_data.get('priority', 'Medium')
        section.append(f"**Priority**: {priority}\n")

        # Attachments
        attachments = jira_data.get('attachments', [])
        if attachments:
            section.append("### Attachments\n")
            for att in attachments:
                filename = att.get('filename', 'unknown')
                mime_type = att.get('mime_type', 'unknown')
                section.append(f"- {filename} ({mime_type})")
            section.append("")

        # Custom fields (if any relevant ones exist)
        custom_fields = jira_data.get('custom_fields', {})
        if custom_fields:
            section.append("### Additional Information\n")
            for key, value in custom_fields.items():
                if value and not key.startswith('customfield_'):
                    section.append(f"- **{key}**: {value}")
            section.append("")

        return "\n".join(section)

    def _generate_footer(self, jira_data: Dict[str, Any]) -> str:
        """Generate report footer."""
        jira_key = jira_data.get('jira_key', 'UNKNOWN')
        timestamp = datetime.now().isoformat()

        footer = [
            "---",
            "",
            f"*This report was auto-generated from JIRA {jira_key} and sanitized for public disclosure*",
            f"*Generated: {timestamp}*",
            "*Please review for any remaining sensitive information before uploading*"
        ]

        return "\n".join(footer)

    def _is_formatted_list(self, text: str) -> bool:
        """Check if text is already formatted as a numbered or bullet list."""
        lines = text.strip().split('\n')
        if not lines:
            return False

        # Check first few lines for list formatting
        list_pattern = re.compile(r'^\s*(?:\d+\.|[-*+])\s+')
        import re

        formatted_lines = sum(1 for line in lines[:5] if list_pattern.match(line))
        return formatted_lines >= min(2, len(lines))

    def _format_as_numbered_list(self, text: str) -> str:
        """Convert plain text to numbered list."""
        # Split on common separators
        steps = []

        # Try splitting on newlines first
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if len(lines) > 1:
            steps = lines
        else:
            # Try splitting on sentence boundaries
            import re
            sentences = re.split(r'[.!?]\s+', text)
            steps = [s.strip() for s in sentences if s.strip()]

        # Format as numbered list
        if not steps:
            return text

        formatted = []
        for i, step in enumerate(steps, 1):
            # Ensure step ends with period if it doesn't have punctuation
            if step and not step[-1] in '.!?':
                step += '.'
            formatted.append(f"{i}. {step}")

        return "\n".join(formatted)


# Convenience functions
def generate_public_bug_report(
    jira_data: Dict[str, Any],
    sanitization_summary: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Convenience function to generate public bug report.

    Args:
        jira_data: Sanitized JIRA data
        sanitization_summary: Sanitization summary text
        metadata: Metadata dictionary

    Returns:
        Formatted public bug report markdown
    """
    template = MicrosoftTemplate()
    return template.generate_public_report(jira_data, sanitization_summary, metadata)


def generate_private_bug_report(
    jira_data: Dict[str, Any],
    private_data: Dict[str, List[str]],
    metadata: Dict[str, Any]
) -> str:
    """
    Convenience function to generate private bug report.

    Args:
        jira_data: Original JIRA data
        private_data: Removed private information
        metadata: Metadata dictionary

    Returns:
        Formatted private bug report markdown
    """
    template = MicrosoftTemplate()
    return template.generate_private_report(jira_data, private_data, metadata)

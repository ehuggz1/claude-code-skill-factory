"""
Report Generator Module

Generates and saves GitHub bug report markdown files to user-specified directories.
"""

import os
import re
from typing import Dict, Any
from datetime import datetime


class BugReportGenerator:
    """Generate and save GitHub bug report markdown files"""

    def __init__(self, output_dir: str = "migrated-bugs"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports (user-specified or default)
        """
        self.output_dir = output_dir

    def save_report(
        self,
        markdown_content: str,
        jira_issue_key: str,
        issue_summary: str
    ) -> str:
        """
        Save bug report markdown to file.

        Args:
            markdown_content: Complete GitHub bug report markdown
            jira_issue_key: JIRA issue key (e.g., "PROJ-123")
            issue_summary: Issue summary/title

        Returns:
            Path to saved file
        """
        # Create output directory if it doesn't exist
        self._ensure_output_dir()

        # Generate filename
        filename = self._generate_filename(jira_issue_key, issue_summary)

        # Full file path
        filepath = os.path.join(self.output_dir, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return filepath

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _generate_filename(self, issue_key: str, summary: str) -> str:
        """
        Generate filename for the bug report.

        Format: {JIRA-KEY}-{timestamp}-{sanitized-summary}.md
        Example: PROJ-123-20251104-153045-nullreferenceexception-orderprocessor.md

        Args:
            issue_key: JIRA issue key
            summary: Issue summary

        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        # Sanitize summary for filename
        safe_summary = self._sanitize_for_filename(summary)

        # Limit summary length to avoid excessively long filenames
        max_summary_length = 60
        if len(safe_summary) > max_summary_length:
            safe_summary = safe_summary[:max_summary_length]

        filename = f"{issue_key}-{timestamp}-{safe_summary}.md"

        return filename

    def _sanitize_for_filename(self, text: str) -> str:
        """
        Sanitize text for use in filename.

        Args:
            text: Original text

        Returns:
            Safe filename component (lowercase, alphanumeric and hyphens)
        """
        # Convert to lowercase
        text = text.lower()

        # Remove common prefixes
        text = re.sub(r'^\[bug\]\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^bug:\s*', '', text, flags=re.IGNORECASE)

        # Replace non-alphanumeric characters with hyphens
        text = re.sub(r'[^a-z0-9]+', '-', text)

        # Remove leading/trailing hyphens
        text = text.strip('-')

        # Collapse multiple hyphens into one
        text = re.sub(r'-+', '-', text)

        return text


def save_github_bug_report(
    markdown_content: str,
    jira_issue_key: str,
    issue_summary: str,
    output_dir: str = "migrated-bugs"
) -> str:
    """
    Convenience function to save GitHub bug report.

    Usage:
        from jira_reader import retrieve_jira_issue
        from field_validator import validate_fields
        from microsoft_template import generate_github_bug_report
        from report_generator import save_github_bug_report

        # Get JIRA data
        jira_data = retrieve_jira_issue("PROJ-123", jira_response)

        # Validate
        validation = validate_fields(jira_data)

        # Generate markdown
        markdown = generate_github_bug_report(jira_data, validation)

        # Save to file
        filepath = save_github_bug_report(
            markdown,
            jira_data['issue_key'],
            jira_data['summary'],
            output_dir="migrated-bugs"
        )

        print(f"Saved to: {filepath}")

    Args:
        markdown_content: Complete bug report markdown
        jira_issue_key: JIRA issue key
        issue_summary: Issue summary/title
        output_dir: Output directory (defaults to "migrated-bugs")

    Returns:
        Path to saved file
    """
    generator = BugReportGenerator(output_dir=output_dir)
    return generator.save_report(markdown_content, jira_issue_key, issue_summary)


def generate_and_save_report(
    jira_data: Dict[str, Any],
    validation_result: Dict[str, Any],
    output_dir: str = "migrated-bugs"
) -> Dict[str, Any]:
    """
    Complete workflow: generate and save bug report.

    This is the main entry point that combines all modules.

    Args:
        jira_data: Parsed JIRA issue data
        validation_result: Field validation results
        output_dir: Output directory

    Returns:
        Dictionary with:
        - filepath: Path to saved file
        - issue_key: JIRA issue key
        - summary: Issue summary
        - validation: Validation results
    """
    from microsoft_template import generate_github_bug_report

    # Generate markdown
    markdown = generate_github_bug_report(jira_data, validation_result)

    # Save to file
    filepath = save_github_bug_report(
        markdown,
        jira_data['issue_key'],
        jira_data['summary'],
        output_dir
    )

    return {
        'filepath': filepath,
        'issue_key': jira_data['issue_key'],
        'summary': jira_data['summary'],
        'validation': validation_result,
        'jira_url': jira_data.get('self_url', ''),
    }


if __name__ == '__main__':
    # Example usage
    sample_markdown = """# [BUG] NullReferenceException in OrderProcessor

**Source**: Migrated from JIRA [PROJ-123](https://company.atlassian.net/browse/PROJ-123)

## Description
Sample bug description

## Steps to Reproduce
1. Create Order
2. Call ProcessOrder
3. Observe error

## Expected Behavior
Method should handle null gracefully

## Actual Behavior
Throws NullReferenceException

---

**Migration Metadata**
- Migrated from: JIRA PROJ-123
- Migration Date: 2025-11-04
"""

    filepath = save_github_bug_report(
        markdown_content=sample_markdown,
        jira_issue_key="PROJ-123",
        issue_summary="NullReferenceException in OrderProcessor.ProcessOrder",
        output_dir="test-output"
    )

    print(f"Saved to: {filepath}")

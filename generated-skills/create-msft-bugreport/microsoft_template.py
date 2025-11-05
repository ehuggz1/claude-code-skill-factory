"""
Microsoft GitHub Bug Report Template

Formats JIRA issue data into GitHub-compliant bug report markdown.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os


class GitHubBugTemplate:
    """Format bug reports for Microsoft GitHub Issues"""

    def __init__(self, jira_data: Dict[str, Any], validation_result: Dict[str, Any]):
        """
        Initialize with JIRA data and validation results.

        Args:
            jira_data: Parsed JIRA issue data from jira_reader
            validation_result: Field validation results from field_validator
        """
        self.jira = jira_data
        self.validation = validation_result
        self.jira_url = self._build_jira_url()

    def _build_jira_url(self) -> str:
        """Build JIRA issue URL from self_url or construct it"""
        if self.jira.get('self_url'):
            # Extract base URL and construct browse URL
            self_url = self.jira['self_url']
            # Format: https://company.atlassian.net/rest/api/2/issue/10001
            # Want: https://company.atlassian.net/browse/PROJ-123
            base_url = self_url.split('/rest/api')[0]
            return f"{base_url}/browse/{self.jira['issue_key']}"
        return f"[JIRA URL not available]"

    def generate_markdown(self) -> str:
        """Generate complete GitHub bug report markdown"""
        sections = []

        # Title
        sections.append(self._format_title())

        # Source link
        sections.append(self._format_source())

        # Description
        sections.append(self._format_description())

        # Steps to Reproduce
        sections.append(self._format_steps())

        # Expected Behavior
        sections.append(self._format_expected_behavior())

        # Actual Behavior
        sections.append(self._format_actual_behavior())

        # Environment
        sections.append(self._format_environment())

        # Stack Trace / Error Output
        if self._has_code_block():
            sections.append(self._format_stack_trace())

        # Severity
        sections.append(self._format_severity())

        # Workaround
        if self.jira.get('root_cause') or self._find_workaround_in_comments():
            sections.append(self._format_workaround())

        # Related Issues
        if self.jira.get('links'):
            sections.append(self._format_related_issues())

        # Screenshots
        if self.jira.get('attachments'):
            sections.append(self._format_screenshots())

        # Root Cause Analysis
        if self.jira.get('root_cause'):
            sections.append(self._format_root_cause())

        # Separator
        sections.append("\n---\n")

        # Missing Information Section
        if self.validation['missing_required'] or self.validation['missing_recommended']:
            sections.append(self._format_missing_fields())

        # Separator
        sections.append("\n---\n")

        # Migration Metadata
        sections.append(self._format_metadata())

        return '\n'.join(sections)

    def _format_title(self) -> str:
        """Format title section"""
        return f"# [BUG] {self.jira['summary']}\n"

    def _format_source(self) -> str:
        """Format JIRA source link"""
        return f"**Source**: Migrated from JIRA [{self.jira['issue_key']}]({self.jira_url})\n"

    def _format_description(self) -> str:
        """Format description section"""
        description = self.jira.get('description_parsed') or self.jira.get('description', '')

        # Remove sections that we'll format separately
        for section in ['steps_to_reproduce', 'expected_behavior', 'actual_behavior', 'root_cause']:
            section_content = self.jira.get(section, '')
            if section_content and section_content in description:
                description = description.replace(section_content, '')

        # Clean up extra whitespace
        description = description.strip()

        return f"## Description\n\n{description}\n"

    def _format_steps(self) -> str:
        """Format steps to reproduce"""
        steps = self.jira.get('steps_to_reproduce', '').strip()

        if not steps:
            return "## Steps to Reproduce\n\n⚠️ **UPDATE REQUIRED** - Steps not provided in JIRA\n\n[TODO: Add steps to reproduce]\n"

        # If already formatted as a list, use it
        if steps.startswith('1.') or steps.startswith('-') or steps.startswith('*'):
            return f"## Steps to Reproduce\n\n{steps}\n"

        # Otherwise, present as single block
        return f"## Steps to Reproduce\n\n{steps}\n"

    def _format_expected_behavior(self) -> str:
        """Format expected behavior"""
        expected = self.jira.get('expected_behavior', '').strip()

        if not expected:
            return "## Expected Behavior\n\n⚠️ **UPDATE REQUIRED** - Expected behavior not specified in JIRA\n\n[TODO: Describe expected behavior]\n"

        return f"## Expected Behavior\n\n{expected}\n"

    def _format_actual_behavior(self) -> str:
        """Format actual behavior"""
        actual = self.jira.get('actual_behavior', '').strip()

        if not actual:
            return "## Actual Behavior\n\n⚠️ **UPDATE REQUIRED** - Actual behavior not specified in JIRA\n\n[TODO: Describe actual behavior]\n"

        return f"## Actual Behavior\n\n{actual}\n"

    def _format_environment(self) -> str:
        """Format environment section"""
        sections = []
        sections.append("## Environment\n")

        env_text = self.jira.get('environment', '').strip()

        # Try to extract OS and .NET version
        os_info = self._extract_from_text(env_text, r'(?:OS|Operating System)[:\s]*([^\n]+)')
        dotnet_version = self._extract_from_text(env_text, r'(?:\.NET|Framework|Runtime)[:\s]*([^\n]+)')

        # Format environment details
        if os_info:
            sections.append(f"- **OS**: {os_info}")
        else:
            sections.append("- **OS**: ⚠️ Not specified in JIRA - UPDATE REQUIRED")

        if dotnet_version:
            sections.append(f"- **.NET Version**: {dotnet_version}")
        else:
            sections.append("- **.NET Version**: ⚠️ Not specified in JIRA - UPDATE REQUIRED")

        # Add component
        components = self.jira.get('components', [])
        if components:
            sections.append(f"- **Component**: {', '.join(components)}")

        # Add affected version
        versions = self.jira.get('affected_versions', []) or self.jira.get('fix_versions', [])
        if versions:
            sections.append(f"- **Affected Version**: {versions[0]}")

        # Add any other environment details
        if env_text and not os_info and not dotnet_version:
            sections.append(f"\n{env_text}")

        sections.append("")
        return '\n'.join(sections)

    def _format_stack_trace(self) -> str:
        """Format stack trace / error output"""
        description = self.jira.get('description', '')

        # Extract code blocks
        import re
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', description, re.DOTALL)

        if not code_blocks:
            return ""

        sections = []
        sections.append("## Stack Trace / Error Output\n")

        for lang, code in code_blocks:
            lang = lang or 'csharp'
            sections.append(f"```{lang}")
            sections.append(code.strip())
            sections.append("```\n")

        return '\n'.join(sections)

    def _format_severity(self) -> str:
        """Format severity section"""
        priority = self.jira.get('priority', 'Medium')

        severity_desc = {
            'Highest': 'Critical - System crash or complete service disruption',
            'Critical': 'Critical - System crash or complete service disruption',
            'High': 'High - Feature unavailable or severely degraded',
            'Medium': 'Medium - Reduced functionality, workaround available',
            'Low': 'Low - Minor inconvenience or cosmetic issue',
        }

        description = severity_desc.get(priority, 'Medium - Impact unknown')

        return f"## Severity\n\n**{priority}** - {description}\n"

    def _format_workaround(self) -> str:
        """Format workaround section"""
        workaround = self._find_workaround_in_comments()

        if workaround:
            return f"## Workaround\n\n{workaround}\n"

        return "## Workaround\n\n[TODO: Document workaround if available]\n"

    def _format_related_issues(self) -> str:
        """Format related issues"""
        links = self.jira.get('links', [])

        if not links:
            return ""

        sections = []
        sections.append("## Related Issues\n")

        for link in links:
            issue_key = link.get('issue_key', '')
            summary = link.get('summary', '')
            link_type = link.get('type', 'Related')

            sections.append(f"- **{link_type}**: {issue_key} - {summary}")

        sections.append("")
        return '\n'.join(sections)

    def _format_screenshots(self) -> str:
        """Format screenshots section with local file references"""
        attachments = self.jira.get('attachments', [])

        if not attachments:
            return ""

        sections = []
        sections.append("## Screenshots / Attachments\n")

        downloaded = []
        pending = []

        for att in attachments:
            filename = att.get('filename', '')
            local_path = att.get('local_path', '')
            url = att.get('url', '')
            size = att.get('size', 0)

            # Categorize as downloaded or pending
            if local_path and os.path.exists(local_path):
                downloaded.append(att)
                sections.append(f"- ✓ **{filename}** (included in this directory, {size:,} bytes)")
            else:
                pending.append(att)
                sections.append(f"- ⚠️ **{filename}** (needs manual download, {size:,} bytes)")

        sections.append("")

        if pending:
            sections.append("### ⚠️ Manual Download Required\n")
            sections.append(f"**{len(pending)} attachment(s) need to be downloaded from JIRA:**\n")

            jira_url = self.jira_url
            if jira_url and jira_url != "[JIRA URL not available]":
                sections.append(f"**Download from**: {jira_url}\n")

            for att in pending:
                filename = att.get('filename', '')
                size = att.get('size', 0)
                sections.append(f"{len(downloaded) + pending.index(att) + 1}. `{filename}` ({size:,} bytes)")

            sections.append("\n**Instructions**:")
            sections.append("1. Open the JIRA issue in your browser")
            sections.append("2. Scroll to the Attachments section")
            sections.append("3. Download each file listed above")
            sections.append(f"4. Save to the same directory as this markdown file (issue folder: `{self.jira.get('issue_key', 'ISSUE-KEY')}/`)")
            sections.append("5. Upload to GitHub when creating the issue")
            sections.append("")

        if downloaded:
            sections.append(f"**Note**: {len(downloaded)} attachment(s) already downloaded and ready to upload to GitHub.")
            sections.append("")

        return '\n'.join(sections)

    def _format_root_cause(self) -> str:
        """Format root cause analysis"""
        root_cause = self.jira.get('root_cause', '').strip()

        if not root_cause:
            return ""

        return f"## Root Cause Analysis\n\n{root_cause}\n"

    def _format_missing_fields(self) -> str:
        """Format missing fields section"""
        sections = []
        sections.append("## ⚠️ Missing Information\n")

        # Required fields
        if self.validation['missing_required']:
            sections.append("### Required Fields (Update Before Creating GitHub Issue)")
            for field in self.validation['missing_required']:
                reason = self._get_missing_field_reason(field)
                sections.append(f"- [ ] ⚠️ **{field}**: {reason}")
            sections.append("")

        # Recommended fields
        if self.validation['missing_recommended']:
            sections.append("### Recommended Fields (Should Complete)")
            for field in self.validation['missing_recommended']:
                reason = self._get_missing_field_reason(field)
                sections.append(f"- [ ] **{field}**: {reason}")
            sections.append("")

        return '\n'.join(sections)

    def _format_metadata(self) -> str:
        """Format migration metadata"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sections = []
        sections.append("**Migration Metadata**")
        sections.append(f"- **Migrated from**: JIRA {self.jira['issue_key']}")
        sections.append(f"- **Original URL**: {self.jira_url}")
        sections.append(f"- **Original Reporter**: {self.jira.get('reporter', {}).get('display_name', 'Unknown')}")
        sections.append(f"- **Original Created**: {self.jira.get('created', 'Unknown')}")
        sections.append(f"- **Migration Date**: {timestamp}")
        sections.append("- **Migrated by**: Claude (JIRA to Microsoft Bug Migrator Skill)")

        return '\n'.join(sections)

    def _has_code_block(self) -> bool:
        """Check if description contains code blocks"""
        description = self.jira.get('description', '')
        return '```' in description

    def _find_workaround_in_comments(self) -> Optional[str]:
        """Search comments for workaround"""
        comments = self.jira.get('comments', [])

        for comment in comments:
            body = comment.get('body', '').lower()
            if 'workaround' in body:
                return comment.get('body', '')

        return None

    def _extract_from_text(self, text: str, pattern: str) -> Optional[str]:
        """Extract information using regex pattern"""
        import re
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _get_missing_field_reason(self, field: str) -> str:
        """Get reason why field is missing"""
        reasons = {
            'OS': 'Not specified in JIRA Environment field',
            '.NET Version': 'Not specified in JIRA Environment field',
            'Steps to Reproduce': 'Not documented in JIRA description',
            'Expected Behavior': 'Not documented in JIRA description',
            'Actual Behavior': 'Not documented in JIRA description',
            'Workaround': 'No workaround documented in JIRA',
            'Related Issues': 'No issue links found in JIRA',
            'Screenshots': 'No attachments found in JIRA',
            'Root Cause': 'Root cause analysis not documented',
        }
        return reasons.get(field, 'Not available in JIRA')


def generate_github_bug_report(
    jira_data: Dict[str, Any],
    validation_result: Dict[str, Any]
) -> str:
    """
    Convenience function to generate GitHub bug report markdown.

    Usage:
        from jira_reader import retrieve_jira_issue
        from field_validator import validate_fields
        from microsoft_template import generate_github_bug_report

        # Get and parse JIRA data
        jira_data = retrieve_jira_issue("PROJ-123", jira_response)

        # Validate fields
        validation = validate_fields(jira_data)

        # Generate GitHub markdown
        markdown = generate_github_bug_report(jira_data, validation)

    Args:
        jira_data: Parsed JIRA issue data
        validation_result: Field validation results

    Returns:
        Complete GitHub-compliant bug report markdown
    """
    template = GitHubBugTemplate(jira_data, validation_result)
    return template.generate_markdown()


if __name__ == '__main__':
    # Example usage
    sample_jira_data = {
        'issue_key': 'PROJ-123',
        'summary': 'NullReferenceException in OrderProcessor.ProcessOrder',
        'description': 'Sample description',
        'steps_to_reproduce': '1. Create Order\n2. Call ProcessOrder\n3. Observe error',
        'expected_behavior': 'Method handles null gracefully',
        'actual_behavior': 'Throws NullReferenceException',
        'environment': '',
        'priority': 'High',
        'components': ['OrderProcessing'],
        'reporter': {'display_name': 'John Doe'},
        'created': '2025-11-01'
    }

    sample_validation = {
        'missing_required': ['.NET Version', 'OS'],
        'missing_recommended': ['Workaround', 'Screenshots']
    }

    markdown = generate_github_bug_report(sample_jira_data, sample_validation)
    print(markdown[:500] + "...")

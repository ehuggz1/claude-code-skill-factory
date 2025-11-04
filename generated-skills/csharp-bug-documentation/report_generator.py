"""
Markdown Report Generator

Generates Microsoft-style bug reports in Markdown format.
"""

import os
import re
from typing import Dict, List, Optional
from datetime import datetime


class MarkdownReportGenerator:
    """Generates Markdown bug reports"""

    def __init__(self, output_dir: str = "bugs"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports (default: "bugs")
        """
        self.output_dir = output_dir
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_report(
        self,
        bug_data: Dict,
        reproduction_steps: List[str],
        suggested_fix: Optional[str] = None,
        impact: Optional[List[str]] = None,
        jira_issue_key: Optional[str] = None,
        jira_url: Optional[str] = None
    ) -> str:
        """
        Generate Markdown bug report.

        Args:
            bug_data: Bug analysis data from bug_analyzer.py
            reproduction_steps: List of reproduction steps
            suggested_fix: Code suggestion to fix the bug
            impact: List of impact points
            jira_issue_key: JIRA issue key (e.g., "ECOM-1234")
            jira_url: Full JIRA issue URL

        Returns:
            Path to generated Markdown file
        """
        content = self._create_markdown_content(
            bug_data,
            reproduction_steps,
            suggested_fix,
            impact,
            jira_issue_key,
            jira_url
        )

        filename = self._generate_filename(bug_data, jira_issue_key)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def _create_markdown_content(
        self,
        bug_data: Dict,
        reproduction_steps: List[str],
        suggested_fix: Optional[str],
        impact: Optional[List[str]],
        jira_issue_key: Optional[str],
        jira_url: Optional[str]
    ) -> str:
        """Create Markdown content for the bug report"""
        sections = []

        # Title
        title = self._create_title(bug_data)
        sections.append(f"# Bug Report: {title}\n")

        # JIRA link (if available)
        if jira_issue_key and jira_url:
            sections.append(f"**JIRA Issue**: [{jira_issue_key}]({jira_url})\n")
        elif jira_issue_key:
            sections.append(f"**JIRA Issue**: {jira_issue_key}\n")

        # Severity
        sections.append("## Severity")
        severity = bug_data.get('severity', 'Medium')
        severity_desc = self._get_severity_description(severity)
        sections.append(f"**{severity}** - {severity_desc}\n")

        # Environment
        sections.append("## Environment")
        env_items = [
            f"- **Language**: C#",
            f"- **Component**: {bug_data.get('component', 'Unknown')}",
        ]
        if bug_data.get('class_name'):
            env_items.append(f"- **Class**: {bug_data['class_name']}")
        if bug_data.get('method'):
            env_items.append(f"- **Method**: {bug_data['method']}")
        if bug_data.get('file_path'):
            file_location = bug_data['file_path']
            if bug_data.get('line_number'):
                file_location += f":{bug_data['line_number']}"
            env_items.append(f"- **File**: `{file_location}`")
        if bug_data.get('namespace'):
            env_items.append(f"- **Namespace**: {bug_data['namespace']}")
        env_items.append(f"- **Reported**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append('\n'.join(env_items) + '\n')

        # Description
        sections.append("## Description")
        if bug_data.get('message'):
            sections.append(f"{bug_data.get('exception_type', 'Exception')}: {bug_data['message']}\n")
        else:
            sections.append(f"A {bug_data.get('exception_type', 'bug')} has been detected.\n")

        if bug_data.get('user_description'):
            sections.append(bug_data['user_description'] + '\n')

        # Steps to Reproduce
        if reproduction_steps:
            sections.append("## Steps to Reproduce")
            for i, step in enumerate(reproduction_steps, 1):
                sections.append(f"{i}. {step}")
            sections.append("")

        # Expected Behavior
        sections.append("## Expected Behavior")
        sections.append(self._get_expected_behavior(bug_data) + '\n')

        # Actual Behavior
        sections.append("## Actual Behavior")
        sections.append(self._get_actual_behavior(bug_data))

        # Exception details (if available)
        if bug_data.get('exception_type'):
            sections.append("\n```csharp")
            stacktrace_lines = [
                f"{bug_data['exception_type']}: {bug_data.get('message', 'No message')}"
            ]
            if bug_data.get('file_path'):
                location = f"   at {bug_data.get('class_name', '')}.{bug_data.get('method', '')}"
                if bug_data.get('file_path'):
                    location += f" in {bug_data['file_path']}"
                    if bug_data.get('line_number'):
                        location += f":line {bug_data['line_number']}"
                stacktrace_lines.append(location)
            sections.append('\n'.join(stacktrace_lines))
            sections.append("```\n")

        # Root Cause
        if bug_data.get('root_cause'):
            sections.append("## Root Cause")
            sections.append(bug_data['root_cause'] + '\n')

        # Suggested Fix
        if suggested_fix:
            sections.append("## Suggested Fix")
            sections.append("```csharp")
            sections.append(suggested_fix)
            sections.append("```\n")

        # Impact
        if impact:
            sections.append("## Impact")
            for item in impact:
                sections.append(f"- {item}")
            sections.append("")

        # Footer
        sections.append("---")
        footer_items = []
        if jira_issue_key:
            footer_items.append(f"**JIRA**: {jira_issue_key}")
        footer_items.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        footer_items.append("**Reporter**: Claude (C# Bug Documentation Skill)")
        sections.append("  \n".join(footer_items))

        return '\n'.join(sections)

    def _create_title(self, bug_data: Dict) -> str:
        """Create report title"""
        exception_type = bug_data.get('exception_type', 'Exception')
        class_name = bug_data.get('class_name', 'unknown')
        method = bug_data.get('method', 'unknown method')

        return f"{exception_type} in {class_name}.{method}"

    def _generate_filename(self, bug_data: Dict, jira_issue_key: Optional[str] = None) -> str:
        """Generate filename for the report"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        # Sanitize summary for filename
        exception_type = bug_data.get('exception_type', 'exception')
        class_name = bug_data.get('class_name', 'unknown')

        # Create safe filename
        safe_name = f"{exception_type}-{class_name}".lower()
        safe_name = re.sub(r'[^a-z0-9-]', '-', safe_name)
        safe_name = re.sub(r'-+', '-', safe_name)  # Remove duplicate hyphens

        if jira_issue_key:
            filename = f"{jira_issue_key}-{timestamp}-{safe_name}.md"
        else:
            filename = f"BUG-{timestamp}-{safe_name}.md"

        return filename

    def _get_severity_description(self, severity: str) -> str:
        """Get severity description"""
        descriptions = {
            'Critical': 'Application crash or complete service disruption',
            'High': 'Feature unavailable or severely degraded',
            'Medium': 'Reduced functionality, workaround available',
            'Low': 'Minor inconvenience or cosmetic issue',
        }
        return descriptions.get(severity, 'Unknown severity')

    def _get_expected_behavior(self, bug_data: Dict) -> str:
        """Generate expected behavior description"""
        exception_type = bug_data.get('exception_type', '')

        if exception_type == 'NullReferenceException':
            return "The method should handle null inputs gracefully or validate parameters before use."
        elif exception_type == 'InvalidOperationException':
            return "The operation should complete without modifying collections during enumeration."
        elif exception_type == 'DivideByZeroException':
            return "Division operations should check for zero divisor and handle appropriately."
        elif exception_type == 'IndexOutOfRangeException':
            return "Array/list access should validate index bounds before accessing elements."
        else:
            return "The code should execute without throwing an exception."

    def _get_actual_behavior(self, bug_data: Dict) -> str:
        """Generate actual behavior description"""
        exception_type = bug_data.get('exception_type', 'exception')
        message = bug_data.get('message', 'An error occurred')

        return f"The code throws `{exception_type}`: {message}"


def generate_bug_report(
    bug_data: Dict,
    reproduction_steps: List[str],
    suggested_fix: Optional[str] = None,
    impact: Optional[List[str]] = None,
    jira_issue_key: Optional[str] = None,
    jira_url: Optional[str] = None,
    output_dir: str = "bugs"
) -> str:
    """
    Convenience function to generate a bug report.

    Usage:
        filepath = generate_bug_report(
            bug_data=analyzer_result,
            reproduction_steps=["Step 1", "Step 2"],
            suggested_fix="// Fixed code",
            impact=["Impact 1", "Impact 2"],
            jira_issue_key="ECOM-1234",
            jira_url="https://company.atlassian.net/browse/ECOM-1234"
        )

    Returns:
        Path to generated Markdown file
    """
    generator = MarkdownReportGenerator(output_dir=output_dir)
    return generator.generate_report(
        bug_data,
        reproduction_steps,
        suggested_fix,
        impact,
        jira_issue_key,
        jira_url
    )


if __name__ == '__main__':
    # Example usage
    from bug_analyzer import analyze_bug

    sample_stacktrace = """
System.NullReferenceException: Object reference not set to an instance of an object.
   at OrderProcessor.ProcessOrder(Order order) in OrderProcessor.cs:line 45
"""

    # Analyze the bug
    bug_data = analyze_bug(stacktrace=sample_stacktrace)

    # Generate report
    filepath = generate_bug_report(
        bug_data=bug_data,
        reproduction_steps=[
            "Create Order with null Items property",
            "Call ProcessOrder(order)",
            "Observe NullReferenceException"
        ],
        suggested_fix="""if (order?.Items != null) {
    var total = order.Items.Sum(i => i.Price);
    Console.WriteLine($"Total: {total}");
}""",
        impact=[
            "Orders with null Items cause crashes",
            "Impacts checkout flow",
            "User experience degraded"
        ],
        jira_issue_key="ECOM-1234",
        jira_url="https://company.atlassian.net/browse/ECOM-1234"
    )

    print(f"Bug report generated: {filepath}")

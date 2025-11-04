"""
JIRA Reporter for Atlassian MCP Integration

Formats bug data for JIRA issues using JIRA wiki markup.
Claude will use this to prepare data before calling Atlassian MCP tools.
"""

from typing import Dict, List, Optional
from datetime import datetime


class JiraFormatter:
    """Formats bug data for JIRA issues"""

    PRIORITY_MAP = {
        'Critical': 'Highest',
        'High': 'High',
        'Medium': 'Medium',
        'Low': 'Low',
    }

    def format_issue_payload(
        self,
        bug_data: Dict,
        project_key: str,
        reproduction_steps: List[str],
        suggested_fix: Optional[str] = None,
        impact: List[str] = None
    ) -> Dict:
        """
        Format bug data into JIRA issue payload.

        Args:
            bug_data: Bug analysis data from bug_analyzer.py
            project_key: JIRA project key (e.g., "ECOM", "PAY")
            reproduction_steps: List of steps to reproduce
            suggested_fix: Code suggestion to fix the bug
            impact: List of impact points

        Returns:
            Dict ready for mcp__atlassian__jira_create_issue
        """
        summary = self._create_summary(bug_data)
        description = self._create_description(
            bug_data,
            reproduction_steps,
            suggested_fix,
            impact
        )

        payload = {
            'project_key': project_key,
            'issue_type': 'Bug',
            'summary': summary,
            'description': description,
            'priority': self.PRIORITY_MAP.get(bug_data.get('severity', 'Medium'), 'Medium'),
            'labels': ['csharp', 'bug', 'automated'],
        }

        # Add component if available
        if bug_data.get('component'):
            payload['components'] = [bug_data['component']]

        return payload

    def _create_summary(self, bug_data: Dict) -> str:
        """Create concise JIRA issue summary"""
        exception_type = bug_data.get('exception_type', 'Exception')
        class_name = bug_data.get('class_name', 'unknown')
        method = bug_data.get('method', 'unknown method')

        # Format: "ExceptionType in ClassName.Method"
        summary = f"{exception_type} in {class_name}.{method}"

        # Add brief context if available from root cause
        root_cause = bug_data.get('root_cause', '')
        if 'null check' in root_cause.lower():
            summary += " - missing null check"
        elif 'collection' in root_cause.lower() and 'modified' in root_cause.lower():
            summary += " - collection modified during iteration"
        elif 'division by zero' in root_cause.lower():
            summary += " - division by zero"

        # Limit to 255 characters (JIRA limit)
        return summary[:255]

    def _create_description(
        self,
        bug_data: Dict,
        reproduction_steps: List[str],
        suggested_fix: Optional[str],
        impact: List[str]
    ) -> str:
        """Create JIRA wiki markup description"""
        sections = []

        # Header
        sections.append("h2. Environment")
        env_items = [
            f"* Language: C#",
            f"* Component: {bug_data.get('component', 'Unknown')}",
        ]
        if bug_data.get('file_path'):
            env_items.append(f"* File: {bug_data['file_path']}")
            if bug_data.get('line_number'):
                env_items[-1] += f":{bug_data['line_number']}"
        if bug_data.get('namespace'):
            env_items.append(f"* Namespace: {bug_data['namespace']}")
        env_items.append(f"* Reported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sections.append('\n'.join(env_items))

        # Description
        sections.append("\nh2. Description")
        if bug_data.get('message'):
            sections.append(f"{bug_data['exception_type']}: {bug_data['message']}")
        else:
            sections.append(f"A {bug_data.get('exception_type', 'bug')} has been detected.")

        if bug_data.get('root_cause'):
            sections.append(f"\n{bug_data['root_cause']}")

        # Steps to Reproduce
        if reproduction_steps:
            sections.append("\nh2. Steps to Reproduce")
            for i, step in enumerate(reproduction_steps, 1):
                sections.append(f"# {step}")

        # Expected vs Actual Behavior
        sections.append("\nh2. Expected Behavior")
        sections.append(self._get_expected_behavior(bug_data))

        sections.append("\nh2. Actual Behavior")
        sections.append(self._get_actual_behavior(bug_data))

        # Stacktrace (if available in original data)
        if bug_data.get('exception_type'):
            sections.append("\nh2. Exception Details")
            sections.append("{code:csharp}")
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
            sections.append("{code}")

        # Root Cause Analysis
        if bug_data.get('root_cause'):
            sections.append("\nh2. Root Cause Analysis")
            sections.append(bug_data['root_cause'])

        # Suggested Fix
        if suggested_fix:
            sections.append("\nh2. Suggested Fix")
            sections.append("{code:csharp}")
            sections.append(suggested_fix)
            sections.append("{code}")

        # Impact
        if impact:
            sections.append("\nh2. Impact")
            for item in impact:
                sections.append(f"* {item}")

        # Footer
        sections.append("\n----")
        sections.append("_Automated bug report generated by Claude Code (C# Bug Documentation Skill)_")

        return '\n'.join(sections)

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

        return f"The code throws {exception_type}: {message}"

    def format_comment(self, comment_text: str, code_snippet: Optional[str] = None) -> str:
        """
        Format a comment to add to an existing JIRA issue.

        Args:
            comment_text: The comment text
            code_snippet: Optional code snippet to include

        Returns:
            JIRA wiki markup formatted comment
        """
        parts = [comment_text]

        if code_snippet:
            parts.append("\n{code:csharp}")
            parts.append(code_snippet)
            parts.append("{code}")

        return '\n'.join(parts)


class JiraIssueBuilder:
    """Builder pattern for creating JIRA issues"""

    def __init__(self, project_key: str):
        self.project_key = project_key
        self.formatter = JiraFormatter()
        self.bug_data = {}
        self.reproduction_steps = []
        self.suggested_fix = None
        self.impact = []

    def with_bug_data(self, bug_data: Dict) -> 'JiraIssueBuilder':
        """Set bug analysis data"""
        self.bug_data = bug_data
        return self

    def with_reproduction_steps(self, steps: List[str]) -> 'JiraIssueBuilder':
        """Set reproduction steps"""
        self.reproduction_steps = steps
        return self

    def with_suggested_fix(self, fix: str) -> 'JiraIssueBuilder':
        """Set suggested fix"""
        self.suggested_fix = fix
        return self

    def with_impact(self, impact: List[str]) -> 'JiraIssueBuilder':
        """Set impact list"""
        self.impact = impact
        return self

    def build(self) -> Dict:
        """Build the JIRA issue payload"""
        return self.formatter.format_issue_payload(
            self.bug_data,
            self.project_key,
            self.reproduction_steps,
            self.suggested_fix,
            self.impact
        )


def create_jira_issue_payload(
    project_key: str,
    bug_data: Dict,
    reproduction_steps: List[str],
    suggested_fix: Optional[str] = None,
    impact: Optional[List[str]] = None
) -> Dict:
    """
    Convenience function to create JIRA issue payload.

    Usage:
        payload = create_jira_issue_payload(
            project_key="ECOM",
            bug_data=analyzer_result,
            reproduction_steps=["Step 1", "Step 2"],
            suggested_fix="// Fixed code here",
            impact=["Production impact", "User experience degraded"]
        )

        # Then Claude calls:
        # mcp__atlassian__jira_create_issue(**payload)
    """
    formatter = JiraFormatter()
    return formatter.format_issue_payload(
        bug_data,
        project_key,
        reproduction_steps,
        suggested_fix,
        impact or []
    )


def format_stacktrace_for_jira(stacktrace: str) -> str:
    """
    Format a stacktrace for JIRA wiki markup.

    Args:
        stacktrace: Raw stacktrace text

    Returns:
        JIRA wiki markup with code block
    """
    return f"{{code:csharp}}\n{stacktrace}\n{{code}}"


def create_jira_comment_with_fix(fix_description: str, code: str) -> str:
    """
    Create a JIRA comment with a suggested fix.

    Usage:
        comment = create_jira_comment_with_fix(
            "Added null check to prevent exception",
            "if (obj != null) { ... }"
        )
        # Then Claude calls:
        # mcp__atlassian__jira_add_comment(issue_key="ECOM-123", comment=comment)
    """
    formatter = JiraFormatter()
    return formatter.format_comment(fix_description, code)


if __name__ == '__main__':
    # Example usage
    from bug_analyzer import analyze_bug

    sample_stacktrace = """
System.NullReferenceException: Object reference not set to an instance of an object.
   at OrderProcessor.ProcessOrder(Order order) in OrderProcessor.cs:line 45
"""

    # Analyze the bug
    bug_data = analyze_bug(stacktrace=sample_stacktrace)

    # Create JIRA issue payload
    payload = create_jira_issue_payload(
        project_key="ECOM",
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
        ]
    )

    print("JIRA Issue Payload:")
    print(f"Project: {payload['project_key']}")
    print(f"Summary: {payload['summary']}")
    print(f"Priority: {payload['priority']}")
    print(f"\nDescription preview:")
    print(payload['description'][:500] + "...")

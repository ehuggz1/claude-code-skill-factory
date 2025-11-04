"""
Field Validator Module

Validates JIRA issue data against GitHub bug template requirements.
Identifies missing required and recommended fields.
"""

from typing import Dict, List, Any


class GitHubFieldValidator:
    """Validate fields against GitHub bug template requirements"""

    # GitHub Standard Bug Template - Required Fields
    REQUIRED_FIELDS = [
        'Title',
        'Description',
        'Steps to Reproduce',
        'Expected Behavior',
        'Actual Behavior',
        'Environment',
        'Severity'
    ]

    # Recommended but not strictly required
    RECOMMENDED_FIELDS = [
        'Workaround',
        'Related Issues',
        'Screenshots',
        'Root Cause'
    ]

    # Environment sub-fields
    ENVIRONMENT_SUBFIELDS = [
        'OS',
        '.NET Version'
    ]

    def __init__(self, jira_data: Dict[str, Any]):
        """
        Initialize validator with JIRA data.

        Args:
            jira_data: Parsed JIRA issue data from jira_reader
        """
        self.jira = jira_data
        self.missing_required = []
        self.missing_recommended = []
        self.present_fields = []

    def validate(self) -> Dict[str, Any]:
        """
        Validate all fields and return results.

        Returns:
            Dictionary with:
            - missing_required: List of missing required fields
            - missing_recommended: List of missing recommended fields
            - present_fields: List of fields that are present
            - is_complete: Boolean indicating if all required fields present
            - completeness_score: Percentage of all fields present
        """
        self.missing_required = []
        self.missing_recommended = []
        self.present_fields = []

        # Validate required fields
        self._validate_required_fields()

        # Validate recommended fields
        self._validate_recommended_fields()

        # Calculate completeness
        total_fields = len(self.REQUIRED_FIELDS) + len(self.RECOMMENDED_FIELDS)
        present_count = len(self.present_fields)
        completeness = (present_count / total_fields) * 100

        return {
            'missing_required': self.missing_required,
            'missing_recommended': self.missing_recommended,
            'present_fields': self.present_fields,
            'is_complete': len(self.missing_required) == 0,
            'completeness_score': round(completeness, 1),
            'total_required': len(self.REQUIRED_FIELDS),
            'total_recommended': len(self.RECOMMENDED_FIELDS)
        }

    def _validate_required_fields(self):
        """Validate required fields"""
        # Title (from Summary)
        if self._is_field_present(self.jira.get('summary', '')):
            self.present_fields.append('Title')
        else:
            self.missing_required.append('Title')

        # Description
        if self._is_field_present(self.jira.get('description', '')):
            self.present_fields.append('Description')
        else:
            self.missing_required.append('Description')

        # Steps to Reproduce
        if self._is_field_present(self.jira.get('steps_to_reproduce', '')):
            self.present_fields.append('Steps to Reproduce')
        else:
            self.missing_required.append('Steps to Reproduce')

        # Expected Behavior
        if self._is_field_present(self.jira.get('expected_behavior', '')):
            self.present_fields.append('Expected Behavior')
        else:
            self.missing_required.append('Expected Behavior')

        # Actual Behavior
        if self._is_field_present(self.jira.get('actual_behavior', '')):
            self.present_fields.append('Actual Behavior')
        else:
            self.missing_required.append('Actual Behavior')

        # Environment (overall)
        env_text = self.jira.get('environment', '')
        if self._is_field_present(env_text):
            self.present_fields.append('Environment')
        else:
            self.missing_required.append('Environment')

        # Environment sub-fields
        if not self._has_os_info(env_text):
            self.missing_required.append('OS')
        else:
            self.present_fields.append('OS')

        if not self._has_dotnet_version(env_text):
            self.missing_required.append('.NET Version')
        else:
            self.present_fields.append('.NET Version')

        # Severity (from Priority)
        if self._is_field_present(self.jira.get('priority', '')):
            self.present_fields.append('Severity')
        else:
            self.missing_required.append('Severity')

    def _validate_recommended_fields(self):
        """Validate recommended fields"""
        # Workaround
        if self._has_workaround():
            self.present_fields.append('Workaround')
        else:
            self.missing_recommended.append('Workaround')

        # Related Issues
        if self.jira.get('links'):
            self.present_fields.append('Related Issues')
        else:
            self.missing_recommended.append('Related Issues')

        # Screenshots
        if self.jira.get('attachments'):
            self.present_fields.append('Screenshots')
        else:
            self.missing_recommended.append('Screenshots')

        # Root Cause
        if self._is_field_present(self.jira.get('root_cause', '')):
            self.present_fields.append('Root Cause')
        else:
            self.missing_recommended.append('Root Cause')

    def _is_field_present(self, value: Any) -> bool:
        """Check if field has meaningful content"""
        if value is None:
            return False

        if isinstance(value, str):
            # Strip whitespace and check length
            cleaned = value.strip()
            # Consider field present if it has at least 3 characters
            return len(cleaned) >= 3

        if isinstance(value, (list, dict)):
            return len(value) > 0

        return bool(value)

    def _has_os_info(self, env_text: str) -> bool:
        """Check if environment text contains OS information"""
        if not env_text:
            return False

        import re
        # Look for OS indicators
        os_patterns = [
            r'(?:os|operating system)[:\s]*(\w+)',
            r'\bwindows\b',
            r'\blinux\b',
            r'\bmac\b',
            r'\bmacos\b',
            r'\bubuntu\b'
        ]

        for pattern in os_patterns:
            if re.search(pattern, env_text, re.IGNORECASE):
                return True

        return False

    def _has_dotnet_version(self, env_text: str) -> bool:
        """Check if environment text contains .NET version"""
        if not env_text:
            return False

        import re
        # Look for .NET version indicators
        dotnet_patterns = [
            r'\.net\s+[\d\.]+',
            r'framework\s+[\d\.]+',
            r'core\s+[\d\.]+',
            r'runtime\s+[\d\.]+'
        ]

        for pattern in dotnet_patterns:
            if re.search(pattern, env_text, re.IGNORECASE):
                return True

        return False

    def _has_workaround(self) -> bool:
        """Check if workaround is documented"""
        # Check root_cause field
        if self._is_field_present(self.jira.get('root_cause', '')):
            return True

        # Check comments for workaround
        comments = self.jira.get('comments', [])
        for comment in comments:
            body = comment.get('body', '').lower()
            if 'workaround' in body:
                return True

        return False

    def generate_summary(self) -> str:
        """Generate human-readable validation summary"""
        lines = []

        if not self.missing_required:
            lines.append("✓ All required fields present")
        else:
            lines.append(f"⚠️ {len(self.missing_required)} required fields missing:")
            for field in self.missing_required:
                lines.append(f"  - {field}")

        if not self.missing_recommended:
            lines.append("✓ All recommended fields present")
        else:
            lines.append(f"  {len(self.missing_recommended)} recommended fields missing:")
            for field in self.missing_recommended:
                lines.append(f"  - {field}")

        return '\n'.join(lines)


def validate_fields(jira_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate JIRA data fields.

    Usage:
        from jira_reader import retrieve_jira_issue
        from field_validator import validate_fields

        jira_data = retrieve_jira_issue("PROJ-123", jira_response)
        validation = validate_fields(jira_data)

        if not validation['is_complete']:
            print(f"Missing required fields: {validation['missing_required']}")

    Args:
        jira_data: Parsed JIRA issue data

    Returns:
        Validation results dictionary
    """
    validator = GitHubFieldValidator(jira_data)
    return validator.validate()


def get_validation_summary(jira_data: Dict[str, Any]) -> str:
    """
    Get human-readable validation summary.

    Args:
        jira_data: Parsed JIRA issue data

    Returns:
        Human-readable summary string
    """
    validator = GitHubFieldValidator(jira_data)
    validator.validate()
    return validator.generate_summary()


if __name__ == '__main__':
    # Example usage
    sample_jira_data = {
        'summary': 'NullReferenceException in OrderProcessor',
        'description': 'Sample description with details',
        'steps_to_reproduce': '1. Create Order\n2. Call ProcessOrder',
        'expected_behavior': 'Method handles null gracefully',
        'actual_behavior': 'Throws NullReferenceException',
        'environment': 'Windows 11, .NET 6.0',
        'priority': 'High',
        'root_cause': '',
        'links': [],
        'attachments': [],
        'comments': []
    }

    # Validate
    result = validate_fields(sample_jira_data)

    print(f"Complete: {result['is_complete']}")
    print(f"Completeness Score: {result['completeness_score']}%")
    print(f"\nMissing Required: {result['missing_required']}")
    print(f"Missing Recommended: {result['missing_recommended']}")
    print(f"\nSummary:")
    print(get_validation_summary(sample_jira_data))

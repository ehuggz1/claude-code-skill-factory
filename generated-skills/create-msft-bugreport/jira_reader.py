"""
JIRA Reader Module

Retrieves JIRA issues using Atlassian MCP and extracts relevant fields.
Downloads attachments locally for inclusion in GitHub issues.
Claude will use this module to fetch issue data before formatting.
"""

from typing import Dict, Any, Optional, List
import re
import os
import requests


class JiraReader:
    """Retrieve and parse JIRA issues via Atlassian MCP"""

    def __init__(self, issue_key: str):
        """
        Initialize reader with JIRA issue key.

        Args:
            issue_key: JIRA issue identifier (e.g., "PROJ-123")
        """
        self.issue_key = issue_key.upper()
        self.raw_data = {}
        self.parsed_data = {}

    def extract_issue_data(self, jira_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and structure data from JIRA MCP response.

        Args:
            jira_response: Raw response from mcp__atlassian__jira_get_issue

        Returns:
            Structured dictionary with standardized field names
        """
        self.raw_data = jira_response
        fields = jira_response.get('fields', {})

        self.parsed_data = {
            # Basic info
            'issue_key': jira_response.get('key', self.issue_key),
            'issue_id': jira_response.get('id'),
            'self_url': jira_response.get('self'),

            # Core fields
            'summary': fields.get('summary', ''),
            'description': fields.get('description', ''),
            'issue_type': fields.get('issuetype', {}).get('name', 'Bug'),
            'status': fields.get('status', {}).get('name', ''),
            'priority': fields.get('priority', {}).get('name', 'Medium'),

            # People
            'reporter': self._extract_user(fields.get('reporter')),
            'assignee': self._extract_user(fields.get('assignee')),

            # Dates
            'created': fields.get('created', ''),
            'updated': fields.get('updated', ''),
            'resolved': fields.get('resolutiondate'),

            # Version info
            'fix_versions': self._extract_versions(fields.get('fixVersions', [])),
            'affected_versions': self._extract_versions(fields.get('versions', [])),

            # Categorization
            'labels': fields.get('labels', []),
            'components': self._extract_components(fields.get('components', [])),

            # Environment and details
            'environment': fields.get('environment', ''),

            # Relationships
            'attachments': self._extract_attachments(fields.get('attachment', [])),
            'links': self._extract_links(jira_response.get('fields', {}).get('issuelinks', [])),
            'comments': self._extract_comments(fields.get('comment', {})),

            # Custom fields (if available)
            'custom_fields': self._extract_custom_fields(fields),
        }

        # Parse description sections
        self.parsed_data.update(self._parse_description_sections(self.parsed_data['description']))

        return self.parsed_data

    def _extract_user(self, user_obj: Optional[Dict]) -> Dict[str, str]:
        """Extract user information"""
        if not user_obj:
            return {'name': 'Unknown', 'email': '', 'display_name': 'Unknown'}

        return {
            'name': user_obj.get('name', ''),
            'email': user_obj.get('emailAddress', ''),
            'display_name': user_obj.get('displayName', user_obj.get('name', 'Unknown'))
        }

    def _extract_versions(self, versions: List[Dict]) -> List[str]:
        """Extract version names from version objects"""
        return [v.get('name', '') for v in versions if v.get('name')]

    def _extract_components(self, components: List[Dict]) -> List[str]:
        """Extract component names"""
        return [c.get('name', '') for c in components if c.get('name')]

    def _extract_attachments(self, attachments: List[Dict]) -> List[Dict[str, str]]:
        """Extract attachment information"""
        return [
            {
                'filename': att.get('filename', ''),
                'url': att.get('content', ''),
                'size': att.get('size', 0),
                'mime_type': att.get('mimeType', ''),
                'local_path': ''  # Will be set when downloaded
            }
            for att in attachments
        ]

    def download_attachments(self, output_dir: str, auth_token: Optional[str] = None) -> List[str]:
        """
        Download all attachments to the specified directory.

        Args:
            output_dir: Directory to save attachments
            auth_token: Optional authentication token for JIRA API

        Returns:
            List of local file paths for downloaded attachments
        """
        if not self.parsed_data.get('attachments'):
            return []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        downloaded_files = []

        for attachment in self.parsed_data['attachments']:
            url = attachment.get('url', '')
            filename = attachment.get('filename', '')

            if not url or not filename:
                continue

            try:
                # Prepare headers
                headers = {}
                if auth_token:
                    headers['Authorization'] = f'Bearer {auth_token}'

                # Download file
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()

                # Save to local file
                local_path = os.path.join(output_dir, filename)

                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Update attachment info with local path
                attachment['local_path'] = local_path
                downloaded_files.append(local_path)

            except Exception as e:
                # Log error but continue with other attachments
                print(f"Warning: Failed to download {filename}: {str(e)}")
                continue

        return downloaded_files

    def _extract_links(self, links: List[Dict]) -> List[Dict[str, str]]:
        """Extract issue links"""
        extracted_links = []
        for link in links:
            link_type = link.get('type', {}).get('name', '')

            # Handle inward links
            if 'inwardIssue' in link:
                extracted_links.append({
                    'type': link_type,
                    'direction': 'inward',
                    'issue_key': link['inwardIssue'].get('key', ''),
                    'summary': link['inwardIssue'].get('fields', {}).get('summary', '')
                })

            # Handle outward links
            if 'outwardIssue' in link:
                extracted_links.append({
                    'type': link_type,
                    'direction': 'outward',
                    'issue_key': link['outwardIssue'].get('key', ''),
                    'summary': link['outwardIssue'].get('fields', {}).get('summary', '')
                })

        return extracted_links

    def _extract_comments(self, comment_obj: Dict) -> List[Dict[str, str]]:
        """Extract comments"""
        comments = comment_obj.get('comments', [])
        return [
            {
                'author': self._extract_user(c.get('author'))['display_name'],
                'body': c.get('body', ''),
                'created': c.get('created', ''),
                'updated': c.get('updated', '')
            }
            for c in comments
        ]

    def _extract_custom_fields(self, fields: Dict) -> Dict[str, Any]:
        """Extract any custom fields (customfield_*)"""
        custom = {}
        for key, value in fields.items():
            if key.startswith('customfield_') and value is not None:
                custom[key] = value
        return custom

    def _parse_description_sections(self, description: str) -> Dict[str, str]:
        """
        Parse JIRA description into sections.

        Looks for common section headers like:
        - Steps to Reproduce
        - Expected Behavior
        - Actual Behavior
        - Root Cause
        - Environment
        """
        if not description:
            return {
                'steps_to_reproduce': '',
                'expected_behavior': '',
                'actual_behavior': '',
                'root_cause': '',
                'description_parsed': description
            }

        sections = {
            'steps_to_reproduce': '',
            'expected_behavior': '',
            'actual_behavior': '',
            'root_cause': '',
            'description_parsed': description
        }

        # Try to extract sections using common headers
        # JIRA wiki markup uses h2., h3., etc.
        patterns = {
            'steps_to_reproduce': r'(?:h[23]\.\s*)?Steps?\s+to\s+Reproduce[:\s]*(.*?)(?=\n\s*h[23]\.|$)',
            'expected_behavior': r'(?:h[23]\.\s*)?Expected\s+(?:Behavior|Result)[:\s]*(.*?)(?=\n\s*h[23]\.|$)',
            'actual_behavior': r'(?:h[23]\.\s*)?Actual\s+(?:Behavior|Result)[:\s]*(.*?)(?=\n\s*h[23]\.|$)',
            'root_cause': r'(?:h[23]\.\s*)?Root\s+Cause[:\s]*(.*?)(?=\n\s*h[23]\.|$)',
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                sections[field] = match.group(1).strip()

        return sections

    def convert_jira_markup_to_markdown(self, text: str) -> str:
        """
        Convert JIRA wiki markup to GitHub markdown.

        JIRA → GitHub conversions:
        - h2. Header → ## Header
        - {code:csharp}...{code} → ```csharp...```
        - *bold* → **bold**
        - _italic_ → *italic*
        - # numbered list → 1. numbered list
        - * bullet → - bullet
        """
        if not text:
            return text

        # Headers: h2. → ##, h3. → ###, etc.
        text = re.sub(r'^h([1-6])\.\s+(.+)$', lambda m: '#' * int(m.group(1)) + ' ' + m.group(2), text, flags=re.MULTILINE)

        # Code blocks: {code:lang}...{code} → ```lang...```
        text = re.sub(r'\{code:(\w+)\}(.*?)\{code\}', r'```\1\2```', text, flags=re.DOTALL)
        text = re.sub(r'\{code\}(.*?)\{code\}', r'```\1```', text, flags=re.DOTALL)

        # Bold: *text* → **text**
        text = re.sub(r'\*(\S[^*]*?)\*', r'**\1**', text)

        # Italic: _text_ → *text*
        text = re.sub(r'_(\S[^_]*?)_', r'*\1*', text)

        # Strikethrough: -text- → ~~text~~
        text = re.sub(r'-(\S[^-]*?)-', r'~~\1~~', text)

        # Links: [text|url] → [text](url)
        text = re.sub(r'\[([^\|]+?)\|([^\]]+?)\]', r'[\1](\2)', text)

        # Monospace: {{text}} → `text`
        text = re.sub(r'\{\{([^}]+?)\}\}', r'`\1`', text)

        # Bullet lists: * → -
        text = re.sub(r'^\*\s+', '- ', text, flags=re.MULTILINE)

        # Numbered lists: # → 1., 2., etc. (keep simple, just use 1.)
        text = re.sub(r'^#\s+', '1. ', text, flags=re.MULTILINE)

        return text


def retrieve_jira_issue(issue_key: str, jira_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to retrieve and parse JIRA issue.

    Usage in Claude:
        # First, call Atlassian MCP:
        # jira_response = mcp__atlassian__jira_get_issue(issue_key="PROJ-123")

        # Then parse:
        from jira_reader import retrieve_jira_issue
        parsed_data = retrieve_jira_issue("PROJ-123", jira_response)

    Args:
        issue_key: JIRA issue identifier
        jira_response: Response from mcp__atlassian__jira_get_issue

    Returns:
        Structured and parsed issue data
    """
    reader = JiraReader(issue_key)
    parsed_data = reader.extract_issue_data(jira_response)

    # Convert all text fields from JIRA markup to markdown
    parsed_data['description'] = reader.convert_jira_markup_to_markdown(parsed_data['description'])
    parsed_data['steps_to_reproduce'] = reader.convert_jira_markup_to_markdown(parsed_data['steps_to_reproduce'])
    parsed_data['expected_behavior'] = reader.convert_jira_markup_to_markdown(parsed_data['expected_behavior'])
    parsed_data['actual_behavior'] = reader.convert_jira_markup_to_markdown(parsed_data['actual_behavior'])
    parsed_data['root_cause'] = reader.convert_jira_markup_to_markdown(parsed_data['root_cause'])

    return parsed_data


if __name__ == '__main__':
    # Example JIRA response structure for testing
    sample_jira_response = {
        "key": "PROJ-123",
        "id": "10001",
        "self": "https://company.atlassian.net/rest/api/2/issue/10001",
        "fields": {
            "summary": "NullReferenceException in OrderProcessor.ProcessOrder",
            "description": """h2. Environment
* Language: C#
* Component: OrderProcessing

h2. Steps to Reproduce
# Create Order with null Items property
# Call ProcessOrder(order)
# Observe NullReferenceException

h2. Expected Behavior
The method should handle null inputs gracefully.

h2. Actual Behavior
The code throws NullReferenceException: Object reference not set to an instance of an object.

{code:csharp}
System.NullReferenceException: Object reference not set to an instance of an object.
   at OrderProcessor.ProcessOrder(Order order) in OrderProcessor.cs:line 45
{code}""",
            "issuetype": {"name": "Bug"},
            "status": {"name": "Open"},
            "priority": {"name": "High"},
            "labels": ["csharp", "bug", "automated"],
            "components": [{"name": "OrderProcessing"}]
        }
    }

    reader = JiraReader("PROJ-123")
    parsed = reader.extract_issue_data(sample_jira_response)

    print(f"Issue Key: {parsed['issue_key']}")
    print(f"Summary: {parsed['summary']}")
    print(f"Steps to Reproduce: {parsed['steps_to_reproduce'][:100]}...")

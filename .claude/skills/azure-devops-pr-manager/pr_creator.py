"""
PR Creator for Azure DevOps

Generates PR descriptions, suggests reviewers, and creates pull requests.
"""

import re
from typing import Dict, List, Optional, Set
from datetime import datetime
from collections import defaultdict


class PRCreator:
    """Creates pull requests with smart descriptions and reviewer suggestions"""

    def __init__(self):
        # Common commit message patterns
        self.feat_pattern = re.compile(r'feat(\([\w-]+\))?:', re.IGNORECASE)
        self.fix_pattern = re.compile(r'fix(\([\w-]+\))?:', re.IGNORECASE)
        self.docs_pattern = re.compile(r'docs(\([\w-]+\))?:', re.IGNORECASE)
        self.refactor_pattern = re.compile(r'refactor(\([\w-]+\))?:', re.IGNORECASE)
        self.test_pattern = re.compile(r'test(\([\w-]+\))?:', re.IGNORECASE)

        # Work item reference patterns
        self.work_item_patterns = [
            re.compile(r'#(\d+)'),  # #1234
            re.compile(r'AB#(\d+)', re.IGNORECASE),  # AB#1234
            re.compile(r'(?:fixes?|closes?|resolves?)\s+#(\d+)', re.IGNORECASE),
        ]

    def analyze_changes(self, commits: List[Dict], diff: Optional[str] = None) -> Dict:
        """
        Analyze commits and diff to understand changes.

        Args:
            commits: List of commit objects with 'message', 'author', 'date'
            diff: Git diff string (optional)

        Returns:
            Dict with analysis results
        """
        analysis = {
            'commit_count': len(commits),
            'authors': set(),
            'change_types': defaultdict(int),
            'work_items': set(),
            'changed_files': [],
            'additions': 0,
            'deletions': 0,
            'scope': None,
            'breaking_changes': False,
        }

        # Analyze commits
        for commit in commits:
            message = commit.get('message', '')
            author = commit.get('author', 'Unknown')

            analysis['authors'].add(author)

            # Categorize commit type
            if self.feat_pattern.search(message):
                analysis['change_types']['feature'] += 1
            if self.fix_pattern.search(message):
                analysis['change_types']['fix'] += 1
            if self.docs_pattern.search(message):
                analysis['change_types']['docs'] += 1
            if self.refactor_pattern.search(message):
                analysis['change_types']['refactor'] += 1
            if self.test_pattern.search(message):
                analysis['change_types']['test'] += 1

            # Extract work items
            for pattern in self.work_item_patterns:
                matches = pattern.findall(message)
                analysis['work_items'].update(matches)

            # Check for breaking changes
            if 'BREAKING CHANGE' in message or '!' in message.split(':')[0]:
                analysis['breaking_changes'] = True

        # Analyze diff if provided
        if diff:
            diff_analysis = self._analyze_diff(diff)
            analysis.update(diff_analysis)

        # Convert sets to lists for JSON serialization
        analysis['authors'] = list(analysis['authors'])
        analysis['work_items'] = list(analysis['work_items'])

        return analysis

    def _analyze_diff(self, diff: str) -> Dict:
        """Analyze git diff to extract file changes and stats"""
        result = {
            'changed_files': [],
            'additions': 0,
            'deletions': 0,
        }

        current_file = None

        for line in diff.split('\n'):
            # Track file changes
            if line.startswith('diff --git'):
                # Extract filename from: diff --git a/file.py b/file.py
                match = re.search(r'b/(.*?)(?:\s|$)', line)
                if match:
                    current_file = match.group(1)
                    result['changed_files'].append(current_file)

            # Count additions/deletions
            elif line.startswith('+') and not line.startswith('+++'):
                result['additions'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                result['deletions'] += 1

        return result

    def generate_description(
        self,
        commits: List[Dict],
        diff: Optional[str] = None,
        analysis: Optional[Dict] = None,
        template: Optional[str] = None
    ) -> str:
        """
        Generate PR description from commits and analysis.

        Args:
            commits: List of commit objects
            diff: Git diff string (optional)
            analysis: Pre-computed analysis (optional)
            template: Custom PR template (optional)

        Returns:
            Formatted PR description in Markdown
        """
        if analysis is None:
            analysis = self.analyze_changes(commits, diff)

        if template:
            return self._apply_template(template, commits, analysis)

        # Default template
        sections = []

        # Summary
        sections.append("## Summary\n")
        summary = self._generate_summary(commits, analysis)
        sections.append(summary + "\n")

        # Changes
        if analysis['change_types']:
            sections.append("## Changes\n")
            for change_type, count in analysis['change_types'].items():
                sections.append(f"- **{change_type.title()}**: {count} commit(s)")
            sections.append("")

        # Detailed changes list
        sections.append("## What Changed\n")
        for commit in commits[:10]:  # Limit to first 10 commits
            message = commit.get('message', '').split('\n')[0]  # First line only
            sections.append(f"- {message}")
        if len(commits) > 10:
            sections.append(f"- ...and {len(commits) - 10} more commits")
        sections.append("")

        # Files changed
        if analysis.get('changed_files'):
            sections.append("## Files Changed\n")
            sections.append(f"**{len(analysis['changed_files'])}** files modified ")
            sections.append(f"(+{analysis['additions']} additions, -{analysis['deletions']} deletions)\n")

            # Show top 10 files
            for file in analysis['changed_files'][:10]:
                sections.append(f"- `{file}`")
            if len(analysis['changed_files']) > 10:
                sections.append(f"- ...and {len(analysis['changed_files']) - 10} more files")
            sections.append("")

        # Testing checklist
        sections.append("## Testing\n")
        sections.append("- [ ] Unit tests added/updated")
        sections.append("- [ ] Integration tests pass")
        sections.append("- [ ] Manual testing completed")
        sections.append("- [ ] No breaking changes (or documented if present)")
        sections.append("")

        # Breaking changes warning
        if analysis['breaking_changes']:
            sections.append("## ⚠️ Breaking Changes\n")
            sections.append("This PR contains breaking changes. Please review carefully.\n")

        # Related work items
        if analysis['work_items']:
            sections.append("## Related Work Items\n")
            for work_item in analysis['work_items']:
                sections.append(f"- Closes #{work_item}")
            sections.append("")

        # Footer
        sections.append("---")
        sections.append(f"*Generated by Claude Code (Azure DevOps PR Manager)*")

        return '\n'.join(sections)

    def _generate_summary(self, commits: List[Dict], analysis: Dict) -> str:
        """Generate a concise summary of the changes"""
        change_types = analysis['change_types']

        # Determine primary change type
        if change_types:
            primary_type = max(change_types, key=change_types.get)
        else:
            primary_type = 'update'

        commit_count = analysis['commit_count']
        file_count = len(analysis.get('changed_files', []))

        # Build summary
        parts = []

        if primary_type == 'feature':
            parts.append("This PR adds new features")
        elif primary_type == 'fix':
            parts.append("This PR fixes bugs")
        elif primary_type == 'refactor':
            parts.append("This PR refactors code")
        elif primary_type == 'docs':
            parts.append("This PR updates documentation")
        else:
            parts.append("This PR makes changes")

        if commit_count == 1:
            parts.append("in 1 commit")
        else:
            parts.append(f"across {commit_count} commits")

        if file_count:
            parts.append(f"affecting {file_count} file(s)")

        summary = ' '.join(parts) + "."

        # Add breaking change warning
        if analysis['breaking_changes']:
            summary += " ⚠️ Contains breaking changes."

        return summary

    def _apply_template(self, template: str, commits: List[Dict], analysis: Dict) -> str:
        """Apply custom PR template with variable substitution"""
        # Available template variables
        variables = {
            'commit_count': analysis['commit_count'],
            'file_count': len(analysis.get('changed_files', [])),
            'additions': analysis.get('additions', 0),
            'deletions': analysis.get('deletions', 0),
            'work_items': ', '.join(analysis.get('work_items', [])),
            'authors': ', '.join(analysis.get('authors', [])),
            'summary': self._generate_summary(commits, analysis),
        }

        # Replace variables in template
        result = template
        for key, value in variables.items():
            result = result.replace(f'{{{key}}}', str(value))

        return result

    def suggest_reviewers(
        self,
        changed_files: List[str],
        codeowners_content: Optional[str] = None,
        git_blame_data: Optional[Dict[str, List[str]]] = None,
        max_reviewers: int = 3
    ) -> List[str]:
        """
        Suggest reviewers based on code ownership and git blame.

        Args:
            changed_files: List of changed file paths
            codeowners_content: Content of CODEOWNERS file (optional)
            git_blame_data: Dict mapping file paths to list of authors (optional)
            max_reviewers: Maximum number of reviewers to suggest

        Returns:
            List of suggested reviewer usernames
        """
        reviewers = set()

        # Parse CODEOWNERS file
        if codeowners_content:
            codeowners = self._parse_codeowners(codeowners_content)
            for file_path in changed_files:
                owners = self._match_codeowners(file_path, codeowners)
                reviewers.update(owners)

        # Use git blame data
        if git_blame_data:
            author_counts = defaultdict(int)
            for file_path in changed_files:
                authors = git_blame_data.get(file_path, [])
                for author in authors:
                    author_counts[author] += 1

            # Get top contributors
            top_contributors = sorted(
                author_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:max_reviewers]
            reviewers.update([author for author, _ in top_contributors])

        # Limit to max_reviewers
        return list(reviewers)[:max_reviewers]

    def _parse_codeowners(self, content: str) -> List[tuple]:
        """Parse CODEOWNERS file into (pattern, owners) tuples"""
        codeowners = []

        for line in content.split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Format: pattern @owner1 @owner2
            parts = line.split()
            if len(parts) >= 2:
                pattern = parts[0]
                owners = [o.lstrip('@') for o in parts[1:] if o.startswith('@')]
                codeowners.append((pattern, owners))

        return codeowners

    def _match_codeowners(self, file_path: str, codeowners: List[tuple]) -> Set[str]:
        """Match file path against CODEOWNERS patterns"""
        owners = set()

        for pattern, pattern_owners in codeowners:
            # Simple glob-like matching
            if self._matches_pattern(file_path, pattern):
                owners.update(pattern_owners)

        return owners

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches CODEOWNERS pattern"""
        # Convert glob pattern to regex
        # Simple implementation - can be enhanced
        pattern_regex = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.match(pattern_regex, file_path))

    def generate_title(self, commits: List[Dict], analysis: Optional[Dict] = None) -> str:
        """
        Generate PR title from commits.

        Args:
            commits: List of commit objects
            analysis: Pre-computed analysis (optional)

        Returns:
            PR title string
        """
        if not commits:
            return "Pull request"

        if analysis is None:
            analysis = self.analyze_changes(commits, None)

        # If single commit, use its message
        if len(commits) == 1:
            message = commits[0].get('message', '').split('\n')[0]
            return message[:100]  # Limit to 100 chars

        # Multiple commits - generate summary title
        change_types = analysis['change_types']

        if change_types:
            primary_type = max(change_types, key=change_types.get)

            if primary_type == 'feature':
                prefix = "feat:"
            elif primary_type == 'fix':
                prefix = "fix:"
            elif primary_type == 'refactor':
                prefix = "refactor:"
            elif primary_type == 'docs':
                prefix = "docs:"
            else:
                prefix = ""
        else:
            prefix = ""

        # Try to extract common scope or theme
        first_commit = commits[0].get('message', '').split('\n')[0]

        if prefix:
            return f"{prefix} {first_commit[:80]}"
        else:
            return first_commit[:100]


def create_pr_description(
    commits: List[Dict],
    diff: Optional[str] = None,
    template: Optional[str] = None
) -> str:
    """
    Convenience function to create PR description.

    Usage:
        description = create_pr_description(
            commits=commit_list,
            diff=git_diff_output
        )
    """
    creator = PRCreator()
    analysis = creator.analyze_changes(commits, diff)
    return creator.generate_description(commits, diff, analysis, template)


if __name__ == '__main__':
    # Example usage
    sample_commits = [
        {
            'message': 'feat(auth): Add JWT authentication\n\nImplements JWT-based auth with refresh tokens.\nCloses #1234',
            'author': 'alice@example.com',
            'date': '2025-11-01'
        },
        {
            'message': 'test(auth): Add authentication tests',
            'author': 'alice@example.com',
            'date': '2025-11-02'
        },
        {
            'message': 'docs(auth): Update API documentation',
            'author': 'bob@example.com',
            'date': '2025-11-03'
        }
    ]

    creator = PRCreator()

    # Analyze changes
    analysis = creator.analyze_changes(sample_commits)
    print("Analysis:")
    print(f"  Commits: {analysis['commit_count']}")
    print(f"  Authors: {analysis['authors']}")
    print(f"  Change types: {dict(analysis['change_types'])}")
    print(f"  Work items: {analysis['work_items']}")
    print()

    # Generate description
    description = creator.generate_description(sample_commits, analysis=analysis)
    print("PR Description:")
    print(description)
    print()

    # Generate title
    title = creator.generate_title(sample_commits, analysis)
    print(f"PR Title: {title}")

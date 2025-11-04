"""
PR Reviewer for Azure DevOps

Analyzes pull request code changes and generates review comments.
"""

import re
from typing import Dict, List, Optional
from collections import defaultdict


class PRReviewer:
    """Analyzes PR code changes and generates review feedback"""

    # Security patterns
    SECURITY_PATTERNS = [
        (r'eval\s*\(', 'security', 'high', 'Use of eval() is dangerous - consider safer alternatives'),
        (r'exec\s*\(', 'security', 'high', 'Use of exec() is dangerous - consider safer alternatives'),
        (r'os\.system\s*\(', 'security', 'high', 'Use subprocess module instead of os.system()'),
        (r'shell=True', 'security', 'high', 'Avoid shell=True in subprocess calls'),
        (r'password\s*=\s*["\'][\w]+["\']', 'security', 'critical', 'Hardcoded password detected'),
        (r'api[_-]?key\s*=\s*["\'][\w]+["\']', 'security', 'critical', 'Hardcoded API key detected'),
        (r'SELECT.*\+.*FROM', 'security', 'critical', 'Potential SQL injection - use parameterized queries'),
        (r'innerHTML\s*=', 'security', 'medium', 'Potential XSS vulnerability - use textContent or sanitize'),
    ]

    # Code quality patterns
    QUALITY_PATTERNS = [
        (r'TODO|FIXME|XXX|HACK', 'quality', 'low', 'TODO/FIXME comment - consider addressing before merging'),
        (r'console\.log\(', 'quality', 'low', 'Remove console.log before merging'),
        (r'print\s*\(.*#.*debug', 'quality', 'low', 'Remove debug print statement'),
        (r'debugger;', 'quality', 'medium', 'Remove debugger statement'),
        (r'except:\s*pass', 'quality', 'medium', 'Empty except clause - add error handling'),
        (r'catch\s*\(\w+\)\s*{\s*}', 'quality', 'medium', 'Empty catch block - add error handling'),
    ]

    # Performance patterns
    PERFORMANCE_PATTERNS = [
        (r'for\s+\w+\s+in.*:.*for\s+\w+\s+in', 'performance', 'medium', 'Nested loops - consider optimization'),
        (r'\.find\(.*\).*for\s+\w+\s+in', 'performance', 'medium', 'find() in loop - inefficient, use filter() or dict'),
        (r'SELECT\s+\*\s+FROM', 'performance', 'low', 'SELECT * is inefficient - specify needed columns'),
    ]

    def __init__(self):
        self.all_patterns = (
            self.SECURITY_PATTERNS +
            self.QUALITY_PATTERNS +
            self.PERFORMANCE_PATTERNS
        )

    def analyze_pull_request(
        self,
        pr_data: Dict,
        commits: List[Dict],
        changes: List[Dict]
    ) -> Dict:
        """
        Analyze PR for issues and generate review.

        Args:
            pr_data: PR metadata (title, description, etc.)
            commits: List of commits in PR
            changes: List of file changes with diffs

        Returns:
            Dict with analysis results
        """
        analysis = {
            'pr_id': pr_data.get('pullRequestId'),
            'title': pr_data.get('title'),
            'quality_score': 0,
            'risk_level': 'low',
            'issues': [],
            'positives': [],
            'recommendations': [],
            'complexity': self._calculate_complexity(changes),
            'test_coverage': self._check_test_coverage(changes),
        }

        # Analyze each file change
        for change in changes:
            file_issues = self._analyze_file_change(change)
            analysis['issues'].extend(file_issues)

        # Calculate quality score
        analysis['quality_score'] = self._calculate_quality_score(analysis)

        # Determine risk level
        analysis['risk_level'] = self._determine_risk_level(analysis)

        # Generate positives
        analysis['positives'] = self._identify_positives(pr_data, commits, changes)

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _analyze_file_change(self, change: Dict) -> List[Dict]:
        """Analyze a single file change for issues"""
        issues = []

        file_path = change.get('item', {}).get('path', 'unknown')
        change_type = change.get('changeType', 'edit')

        # Skip deleted files
        if change_type == 'delete':
            return issues

        # Get diff content
        diff_content = change.get('diff', '')
        if not diff_content:
            return issues

        # Analyze added lines
        lines = diff_content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Only check added lines (starting with +)
            if not line.startswith('+'):
                continue

            line_content = line[1:]  # Remove + prefix

            # Check against patterns
            for pattern, category, severity, message in self.all_patterns:
                if re.search(pattern, line_content, re.IGNORECASE):
                    issues.append({
                        'file_path': file_path,
                        'line': line_num,
                        'category': category,
                        'severity': severity,
                        'message': message,
                        'code_snippet': line_content.strip(),
                    })

        return issues

    def _calculate_complexity(self, changes: List[Dict]) -> Dict:
        """Calculate PR complexity metrics"""
        total_additions = 0
        total_deletions = 0
        files_changed = len(changes)

        for change in changes:
            # Count lines from diff
            diff = change.get('diff', '')
            for line in diff.split('\n'):
                if line.startswith('+') and not line.startswith('+++'):
                    total_additions += 1
                elif line.startswith('-') and not line.startswith('---'):
                    total_deletions += 1

        total_changes = total_additions + total_deletions

        # Complexity categories
        if total_changes < 100:
            complexity = 'small'
        elif total_changes < 500:
            complexity = 'medium'
        else:
            complexity = 'large'

        return {
            'files_changed': files_changed,
            'additions': total_additions,
            'deletions': total_deletions,
            'total_changes': total_changes,
            'complexity': complexity,
        }

    def _check_test_coverage(self, changes: List[Dict]) -> Dict:
        """Check if PR includes tests"""
        test_files = 0
        source_files = 0

        test_patterns = [r'test_', r'_test\.', r'\.test\.', r'/tests?/', r'\.spec\.']

        for change in changes:
            file_path = change.get('item', {}).get('path', '')

            # Check if test file
            is_test = any(re.search(pattern, file_path, re.IGNORECASE) for pattern in test_patterns)

            if is_test:
                test_files += 1
            else:
                source_files += 1

        has_tests = test_files > 0
        test_ratio = test_files / max(source_files, 1)

        return {
            'has_tests': has_tests,
            'test_files': test_files,
            'source_files': source_files,
            'test_ratio': test_ratio,
        }

    def _calculate_quality_score(self, analysis: Dict) -> int:
        """Calculate quality score (0-10)"""
        score = 10

        # Deduct for issues
        for issue in analysis['issues']:
            if issue['severity'] == 'critical':
                score -= 2
            elif issue['severity'] == 'high':
                score -= 1
            elif issue['severity'] == 'medium':
                score -= 0.5
            elif issue['severity'] == 'low':
                score -= 0.2

        # Bonus for tests
        if analysis['test_coverage']['has_tests']:
            score += 1

        # Deduct for large PRs
        if analysis['complexity']['complexity'] == 'large':
            score -= 1

        return max(0, min(10, int(score)))

    def _determine_risk_level(self, analysis: Dict) -> str:
        """Determine overall risk level"""
        critical_issues = sum(1 for i in analysis['issues'] if i['severity'] == 'critical')
        high_issues = sum(1 for i in analysis['issues'] if i['severity'] == 'high')

        if critical_issues > 0 or high_issues >= 3:
            return 'high'
        elif high_issues > 0 or analysis['complexity']['complexity'] == 'large':
            return 'medium'
        else:
            return 'low'

    def _identify_positives(self, pr_data: Dict, commits: List[Dict], changes: List[Dict]) -> List[str]:
        """Identify positive aspects of the PR"""
        positives = []

        # Good commit messages
        if commits:
            well_formatted = sum(
                1 for c in commits
                if len(c.get('message', '').split('\n')) > 1  # Has description
            )
            if well_formatted / len(commits) > 0.5:
                positives.append("Clear and detailed commit messages")

        # Tests included
        test_coverage = self._check_test_coverage(changes)
        if test_coverage['has_tests']:
            positives.append(f"Includes tests ({test_coverage['test_files']} test file(s))")

        # Reasonable size
        complexity = self._calculate_complexity(changes)
        if complexity['complexity'] == 'small':
            positives.append("Small, focused PR - easy to review")

        # Good PR description
        description = pr_data.get('description', '')
        if len(description) > 100:
            positives.append("Comprehensive PR description")

        return positives

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Critical issues
        critical_count = sum(1 for i in analysis['issues'] if i['severity'] == 'critical')
        if critical_count > 0:
            recommendations.append(f"**MUST FIX**: {critical_count} critical security issue(s) before merging")

        # High priority issues
        high_count = sum(1 for i in analysis['issues'] if i['severity'] == 'high')
        if high_count > 0:
            recommendations.append(f"Fix {high_count} high-priority issue(s)")

        # Test coverage
        if not analysis['test_coverage']['has_tests']:
            recommendations.append("Add tests to verify functionality")

        # Large PR
        if analysis['complexity']['complexity'] == 'large':
            recommendations.append("Consider breaking down large PR into smaller, focused changes")

        # Risk level
        if analysis['risk_level'] == 'high':
            recommendations.append("High-risk PR - request additional reviewer or security review")

        return recommendations

    def generate_review_comments(self, review: Dict, changes: List[Dict]) -> List[Dict]:
        """
        Generate formatted review comments ready for posting.

        Args:
            review: Analysis results from analyze_pull_request
            changes: List of file changes

        Returns:
            List of comment dicts ready for Azure DevOps API
        """
        comments = []

        # Group issues by severity
        issues_by_severity = defaultdict(list)
        for issue in review['issues']:
            issues_by_severity[issue['severity']].append(issue)

        # Generate comments for each issue
        for severity in ['critical', 'high', 'medium', 'low']:
            for issue in issues_by_severity.get(severity, []):
                comment = {
                    'file_path': issue['file_path'],
                    'line': issue['line'],
                    'category': issue['category'],
                    'severity': issue['severity'],
                    'message': self._format_comment_message(issue),
                    'comment_type': 'text',  # or 'suggestion'
                }
                comments.append(comment)

        return comments

    def _format_comment_message(self, issue: Dict) -> str:
        """Format a review comment with severity indicator"""
        severity_icons = {
            'critical': '🔴 CRITICAL',
            'high': '🟠 HIGH',
            'medium': '🟡 MEDIUM',
            'low': '🟢 LOW',
        }

        icon = severity_icons.get(issue['severity'], '⚪')
        category = issue['category'].upper()

        message = f"**{icon} - {category}**\n\n"
        message += f"{issue['message']}\n\n"

        if issue.get('code_snippet'):
            message += f"```\n{issue['code_snippet']}\n```\n\n"

        if issue.get('suggestion'):
            message += f"**Suggested Fix:**\n```\n{issue['suggestion']}\n```"

        return message


def analyze_pr(pr_data: Dict, commits: List[Dict], changes: List[Dict]) -> Dict:
    """
    Convenience function to analyze a PR.

    Usage:
        review = analyze_pr(
            pr_data=pr_info,
            commits=pr_commits,
            changes=pr_changes
        )
    """
    reviewer = PRReviewer()
    return reviewer.analyze_pull_request(pr_data, commits, changes)


if __name__ == '__main__':
    # Example usage
    sample_pr = {
        'pullRequestId': 1234,
        'title': 'Add authentication feature',
        'description': 'Implements JWT-based authentication with refresh tokens.',
    }

    sample_commits = [
        {'message': 'feat: Add JWT authentication'},
        {'message': 'test: Add auth tests'},
    ]

    sample_changes = [
        {
            'item': {'path': '/src/auth.py'},
            'changeType': 'edit',
            'diff': '+password = "hardcoded123"\n+api_key = "secret_key_here"',
        }
    ]

    reviewer = PRReviewer()
    review = reviewer.analyze_pull_request(sample_pr, sample_commits, sample_changes)

    print(f"Quality Score: {review['quality_score']}/10")
    print(f"Risk Level: {review['risk_level']}")
    print(f"Issues Found: {len(review['issues'])}")
    for issue in review['issues']:
        print(f"  - {issue['severity']}: {issue['message']}")

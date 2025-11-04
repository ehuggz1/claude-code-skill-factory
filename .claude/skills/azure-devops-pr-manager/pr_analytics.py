"""PR Analytics - Calculate metrics and trends"""

from typing import Dict, List
from datetime import datetime
from collections import defaultdict
import statistics


class PRAnalytics:
    """Analyze PR metrics and team performance"""

    def calculate_metrics(self, prs: List[Dict]) -> Dict:
        """Calculate comprehensive PR metrics"""
        if not prs:
            return {'error': 'No PRs to analyze'}

        metrics = {
            'total_prs': len(prs),
            'completed': sum(1 for pr in prs if pr.get('status') == 'completed'),
            'active': sum(1 for pr in prs if pr.get('status') == 'active'),
            'abandoned': sum(1 for pr in prs if pr.get('status') == 'abandoned'),
            'cycle_times': self._calculate_cycle_times(prs),
            'size_distribution': self._calculate_size_distribution(prs),
            'top_reviewers': self._calculate_top_reviewers(prs),
            'top_contributors': self._calculate_top_contributors(prs),
        }

        return metrics

    def _calculate_cycle_times(self, prs: List[Dict]) -> Dict:
        """Calculate PR cycle time metrics"""
        cycle_times = []

        for pr in prs:
            if pr.get('status') != 'completed':
                continue

            created = pr.get('creationDate')
            closed = pr.get('closedDate')

            if created and closed:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                closed_dt = datetime.fromisoformat(closed.replace('Z', '+00:00'))
                hours = (closed_dt - created_dt).total_seconds() / 3600
                cycle_times.append(hours)

        if not cycle_times:
            return {'average': 0, 'median': 0, 'p95': 0}

        return {
            'average': round(statistics.mean(cycle_times), 1),
            'median': round(statistics.median(cycle_times), 1),
            'p95': round(sorted(cycle_times)[int(len(cycle_times) * 0.95)], 1) if len(cycle_times) > 1 else 0,
        }

    def _calculate_size_distribution(self, prs: List[Dict]) -> Dict:
        """Calculate PR size distribution"""
        small = sum(1 for pr in prs if pr.get('lines_changed', 0) < 100)
        medium = sum(1 for pr in prs if 100 <= pr.get('lines_changed', 0) < 500)
        large = sum(1 for pr in prs if pr.get('lines_changed', 0) >= 500)

        total = len(prs)
        return {
            'small': {'count': small, 'percent': round(small / total * 100) if total > 0 else 0},
            'medium': {'count': medium, 'percent': round(medium / total * 100) if total > 0 else 0},
            'large': {'count': large, 'percent': round(large / total * 100) if total > 0 else 0},
        }

    def _calculate_top_reviewers(self, prs: List[Dict]) -> List[Dict]:
        """Calculate top reviewers"""
        reviewer_counts = defaultdict(int)

        for pr in prs:
            for reviewer in pr.get('reviewers', []):
                name = reviewer.get('displayName', 'Unknown')
                reviewer_counts[name] += 1

        top = sorted(reviewer_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{'name': name, 'count': count} for name, count in top]

    def _calculate_top_contributors(self, prs: List[Dict]) -> List[Dict]:
        """Calculate top PR authors"""
        author_counts = defaultdict(int)

        for pr in prs:
            author = pr.get('createdBy', {}).get('displayName', 'Unknown')
            author_counts[author] += 1

        top = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{'name': name, 'count': count} for name, count in top]


def calculate_pr_metrics(prs: List[Dict]) -> Dict:
    """Convenience function"""
    analytics = PRAnalytics()
    return analytics.calculate_metrics(prs)

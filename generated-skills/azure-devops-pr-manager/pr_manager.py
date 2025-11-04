"""PR Manager - Handles PR lifecycle operations"""

from typing import Dict, List, Optional


class PRManager:
    """Manages PR lifecycle: complete, abandon, update"""

    def validate_pr_ready(
        self,
        pr_data: Dict,
        required_reviews: int = 1,
        required_checks: Optional[List[str]] = None
    ) -> Dict:
        """Validate if PR is ready to merge"""
        result = {'ready': True, 'blockers': []}

        # Check approvals
        reviewers = pr_data.get('reviewers', [])
        approvals = sum(1 for r in reviewers if r.get('vote') == 10)  # 10 = approved
        if approvals < required_reviews:
            result['ready'] = False
            result['blockers'].append(f"Need {required_reviews - approvals} more approval(s)")

        # Check merge conflicts
        if pr_data.get('mergeStatus') == 'conflicts':
            result['ready'] = False
            result['blockers'].append("Merge conflicts must be resolved")

        # Check policies
        policies = pr_data.get('policies', [])
        failed_policies = [p for p in policies if p.get('status') == 'failed']
        if failed_policies:
            result['ready'] = False
            result['blockers'].append(f"{len(failed_policies)} policy check(s) failed")

        return result


def validate_pr(pr_data: Dict) -> Dict:
    """Convenience function"""
    manager = PRManager()
    return manager.validate_pr_ready(pr_data)

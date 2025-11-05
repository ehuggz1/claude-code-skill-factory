# RREZ PR Manager

**Comprehensive pull request management for Azure DevOps via MCP integration**

---

## Purpose

This skill provides complete pull request lifecycle management for Azure DevOps repositories, including:
1. **Creating PRs** with smart descriptions, reviewers, and work item linking
2. **Reviewing PRs** with automated code analysis and actionable feedback
3. **Managing PRs** through merge, complete, abandon, and update operations
4. **Analyzing PRs** with metrics, trends, and team performance insights

---

## When to Use This Skill

Claude will automatically load this skill when you:
- Ask to "create a pull request in Azure DevOps"
- Request "review this PR" or "analyze PR changes"
- Say "merge this PR" or "complete pull request"
- Need to "check PR status" or "get PR analytics"
- Request "generate PR description from commits"
- Ask about "PR review metrics" or "team PR performance"

---

## What This Skill Does

**Core Capabilities**:

### 1. Create Pull Requests
- Generate PR descriptions from git commits and diff
- Auto-suggest reviewers based on CODEOWNERS or git blame
- Link work items from commit messages
- Set labels, policies, and auto-complete options
- Support draft PRs and PR templates

### 2. Review Pull Requests
- Analyze code changes for issues and improvements
- Check coding standards and best practices
- Identify security vulnerabilities
- Suggest optimizations and refactoring
- Generate review comments with line references
- Assess PR quality and risk level

### 3. Manage Pull Requests
- Complete/merge PRs with validation
- Abandon/close PRs with reasons
- Update PR details (title, description, reviewers)
- Approve or request changes
- Check merge conflicts and policies
- Auto-complete with squash/rebase options

### 4. PR Analytics
- Track PR metrics (cycle time, review time, size)
- Monitor team performance and bottlenecks
- Analyze code review patterns
- Generate PR health reports
- Identify frequently changed files
- Calculate PR velocity trends

---

## Prerequisites

**Azure DevOps MCP Server Must Be Configured**:

This skill requires an Azure DevOps MCP server to be installed and connected. The MCP server provides tools like:
- `mcp__azure_devops__create_pull_request`
- `mcp__azure_devops__get_pull_request`
- `mcp__azure_devops__update_pull_request`
- `mcp__azure_devops__complete_pull_request`
- `mcp__azure_devops__list_pull_requests`
- `mcp__azure_devops__get_pull_request_commits`
- `mcp__azure_devops__get_pull_request_changes`
- `mcp__azure_devops__add_pull_request_comment`

**Check if MCP is available**:
Ask Claude: "Do you have access to Azure DevOps MCP tools?"

**If not installed**, you'll need to set up an Azure DevOps MCP server. This typically involves:
1. Installing the MCP server package
2. Configuring Azure DevOps PAT (Personal Access Token)
3. Connecting to your Azure DevOps organization
4. Enabling the MCP server in Claude settings

---

## Usage Instructions for Claude

### Feature 1: Create Pull Request

When the user asks to create a PR, follow these steps:

**Step 1: Gather PR Context**
```python
from pr_creator import PRCreator

# Get current branch and target branch
current_branch = <from git>
target_branch = <from user or default to 'main'/'develop'>

# Get commit history since divergence
commits = <git log target_branch..current_branch>

# Get code changes
diff = <git diff target_branch...current_branch>

# Analyze changes
creator = PRCreator()
analysis = creator.analyze_changes(commits, diff)
```

**Step 2: Generate PR Description**

Use `pr_creator.py` to generate a comprehensive PR description:
```python
pr_description = creator.generate_description(
    commits=commits,
    diff=diff,
    analysis=analysis
)
```

**Description Format**:
```markdown
## Summary
<1-3 sentence overview of changes>

## Changes
- <bullet point 1>
- <bullet point 2>
- <bullet point 3>

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related Work Items
Closes #<work-item-id>

## Reviewers Suggested
@<reviewer1>, @<reviewer2> (based on code ownership)
```

**Step 3: Suggest Reviewers**

Use `pr_creator.py` to suggest reviewers:
```python
reviewers = creator.suggest_reviewers(
    changed_files=analysis['changed_files'],
    codeowners_file=<path to CODEOWNERS if exists>,
    git_blame_data=<git blame for changed files>
)
```

**Step 4: Create PR via MCP**

Use the Azure DevOps MCP tool:
```python
result = mcp__azure_devops__create_pull_request(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    source_branch=current_branch,
    target_branch=target_branch,
    title=pr_title,
    description=pr_description,
    reviewers=reviewers,
    work_items=<extracted work item IDs>,
    draft=<True if user requested draft>,
    auto_complete=<True if user requested auto-complete>
)

pr_id = result['pullRequestId']
pr_url = result['url']
```

**Step 5: Return Results**

Inform the user:
```
✓ Created pull request: PR #{pr_id}
  URL: {pr_url}

  Title: {title}
  Source: {source_branch} → Target: {target_branch}
  Reviewers: {reviewer_list}
  Work Items: {work_item_list}

Summary: {brief_summary}
```

---

### Feature 2: Review Pull Request

When the user asks to review a PR:

**Step 1: Fetch PR Details**

```python
from pr_reviewer import PRReviewer

# Get PR information
pr_data = mcp__azure_devops__get_pull_request(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    pull_request_id=pr_id
)

# Get PR commits
commits = mcp__azure_devops__get_pull_request_commits(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    pull_request_id=pr_id
)

# Get PR changes/diff
changes = mcp__azure_devops__get_pull_request_changes(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    pull_request_id=pr_id
)
```

**Step 2: Analyze Code Changes**

Use `pr_reviewer.py` to analyze:
```python
reviewer = PRReviewer()

review = reviewer.analyze_pull_request(
    pr_data=pr_data,
    commits=commits,
    changes=changes
)
```

**Analysis includes**:
- Code quality issues
- Security vulnerabilities
- Performance concerns
- Best practice violations
- Complexity metrics
- Test coverage gaps
- Documentation needs
- Breaking changes

**Step 3: Generate Review Comments**

```python
comments = reviewer.generate_review_comments(
    review=review,
    changes=changes
)
```

**Comment Format**:
```python
{
    'file_path': 'src/services/auth.py',
    'line': 45,
    'comment_type': 'security',  # or 'bug', 'style', 'optimization'
    'severity': 'high',  # or 'medium', 'low'
    'message': 'Potential SQL injection vulnerability. Use parameterized queries.',
    'suggestion': 'Use: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
}
```

**Step 4: Post Review Comments** (if user approves)

```python
for comment in comments:
    mcp__azure_devops__add_pull_request_comment(
        organization="<org>",
        project="<project>",
        repository="<repo>",
        pull_request_id=pr_id,
        content=comment['message'],
        file_path=comment['file_path'],
        line=comment['line'],
        comment_type=comment['comment_type']
    )
```

**Step 5: Generate Review Summary**

```markdown
# PR Review Summary

**PR**: #{pr_id} - {title}
**Overall Quality**: {score}/10
**Risk Level**: {Low|Medium|High}

## Issues Found
### 🔴 High Priority ({count})
- {issue 1}
- {issue 2}

### 🟡 Medium Priority ({count})
- {issue 3}
- {issue 4}

### 🟢 Low Priority / Suggestions ({count})
- {issue 5}

## Positive Aspects
- Good test coverage
- Clear commit messages
- Follows coding standards

## Recommendations
1. Fix high-priority security issues before merging
2. Consider refactoring {file} for better maintainability
3. Add documentation for new public APIs

**Approval Status**: ❌ Request Changes / ✅ Approve with Comments / ✅✅ Approve
```

---

### Feature 3: Manage Pull Request

When the user wants to manage a PR:

**Complete/Merge PR**:
```python
from pr_manager import PRManager

manager = PRManager()

# Validate PR is ready to merge
validation = manager.validate_pr_ready(
    pr_data=pr_data,
    required_reviews=<from policy>,
    required_checks=<from policy>
)

if validation['ready']:
    result = mcp__azure_devops__complete_pull_request(
        organization="<org>",
        project="<project>",
        repository="<repo>",
        pull_request_id=pr_id,
        completion_options={
            'merge_strategy': 'squash',  # or 'merge', 'rebase'
            'delete_source_branch': True,
            'commit_message': <custom message if provided>
        }
    )
else:
    # Report blocking issues
    return f"Cannot merge: {validation['blockers']}"
```

**Abandon PR**:
```python
result = mcp__azure_devops__abandon_pull_request(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    pull_request_id=pr_id,
    reason=<user-provided reason>
)
```

**Update PR**:
```python
result = mcp__azure_devops__update_pull_request(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    pull_request_id=pr_id,
    title=<new title>,
    description=<new description>,
    reviewers=<updated reviewer list>
)
```

---

### Feature 4: PR Analytics

When the user requests PR analytics:

**Step 1: Fetch PR Data**

```python
from pr_analytics import PRAnalytics

# Get all PRs in a time range
prs = mcp__azure_devops__list_pull_requests(
    organization="<org>",
    project="<project>",
    repository="<repo>",
    status='completed',  # or 'active', 'abandoned', 'all'
    created_after=<date>,
    created_before=<date>
)
```

**Step 2: Calculate Metrics**

```python
analytics = PRAnalytics()

metrics = analytics.calculate_metrics(prs)
```

**Metrics Include**:
- **Cycle Time**: Time from PR creation to merge
- **Review Time**: Time from creation to first review
- **PR Size**: Lines changed, files modified
- **Review Rounds**: Number of review iterations
- **Approval Time**: Time to get required approvals
- **PR Velocity**: PRs completed per time period
- **Reviewer Load**: PRs per reviewer
- **Hot Files**: Most frequently changed files

**Step 3: Generate Analytics Report**

```markdown
# PR Analytics Report

**Period**: {start_date} to {end_date}
**Total PRs**: {count} ({completed} completed, {active} active, {abandoned} abandoned)

## Cycle Time Metrics
- **Average Cycle Time**: {avg_hours} hours
- **Median Cycle Time**: {median_hours} hours
- **95th Percentile**: {p95_hours} hours

## PR Size Distribution
- Small (<100 lines): {count} ({percent}%)
- Medium (100-500 lines): {count} ({percent}%)
- Large (>500 lines): {count} ({percent}%)

## Top Reviewers
1. {reviewer1}: {count} PRs reviewed, {avg_time} avg review time
2. {reviewer2}: {count} PRs reviewed, {avg_time} avg review time
3. {reviewer3}: {count} PRs reviewed, {avg_time} avg review time

## Top Contributors
1. {author1}: {count} PRs created, {merge_rate}% merge rate
2. {author2}: {count} PRs created, {merge_rate}% merge rate
3. {author3}: {count} PRs created, {merge_rate}% merge rate

## Hot Files (Most Changed)
1. {file1}: {count} PRs
2. {file2}: {count} PRs
3. {file3}: {count} PRs

## Recommendations
- Consider breaking down large PRs for faster review
- {reviewer_with_high_load} has high review load
- {file_with_many_changes} may need refactoring
```

---

## Configuration

**Required** (prompt user if unknown):
- **Azure DevOps Organization**: e.g., "mycompany"
- **Project Name**: e.g., "MyProject"
- **Repository Name**: e.g., "my-repo"

**Optional** (use defaults if not specified):
- **Default Target Branch**: "main" or "develop"
- **Default Merge Strategy**: "squash", "merge", or "rebase"
- **Auto-Complete PRs**: true/false
- **Delete Source Branch After Merge**: true/false
- **Required Reviewers Count**: default 2
- **PR Size Thresholds**: small <100, medium 100-500, large >500 lines

---

## Example Workflows

### Example 1: Create PR

**User**:
```
Claude, create a pull request in Azure DevOps.

Current branch: feature/add-authentication
Target: main
Organization: contoso
Project: MyApp
Repo: backend
```

**Claude** (using this skill):
1. Analyzes commits on feature/add-authentication
2. Generates PR description from commits and diff
3. Suggests reviewers based on changed files
4. Creates PR via MCP
5. Returns:

```
✓ Created pull request: PR #1234
  URL: https://dev.azure.com/contoso/MyApp/_git/backend/pullrequest/1234

  Title: Add JWT authentication for API endpoints
  Source: feature/add-authentication → Target: main
  Reviewers: @alice, @bob (suggested from CODEOWNERS)
  Work Items: #5678, #5679

Summary: Implements JWT-based authentication with refresh token support,
updates middleware, and adds comprehensive tests.

Files changed: 12 (+450, -120)
```

### Example 2: Review PR

**User**:
```
Claude, review PR #1234 in Azure DevOps.

Organization: contoso
Project: MyApp
Repo: backend
```

**Claude** (using this skill):
1. Fetches PR details, commits, and changes
2. Analyzes code for issues
3. Generates review comments
4. Returns:

```
# PR Review Summary

**PR**: #1234 - Add JWT authentication for API endpoints
**Overall Quality**: 7/10
**Risk Level**: Medium

## Issues Found
### 🔴 High Priority (2)
- auth.py:45 - Hardcoded secret key. Use environment variable instead.
- token_service.py:78 - Token expiration not validated properly.

### 🟡 Medium Priority (3)
- middleware.py:23 - Missing error handling for malformed tokens.
- auth_controller.py:156 - Consider rate limiting for token refresh endpoint.
- user_service.py:89 - Database query could be optimized with index.

### 🟢 Low Priority / Suggestions (4)
- Add docstrings for public methods in auth.py
- Consider extracting token validation logic into separate method
- Test coverage for edge cases (expired tokens, invalid signatures)
- README.md needs authentication setup instructions

## Positive Aspects
- Good test coverage (85%)
- Clear commit messages
- Follows project coding standards
- Proper error handling in most places

## Recommendations
1. **MUST FIX**: Remove hardcoded secrets before merging
2. Fix token validation vulnerability
3. Add rate limiting for security endpoints
4. Consider security review for authentication changes

**Approval Status**: ❌ Request Changes
**Estimated Fix Time**: 2-3 hours

Would you like me to post these review comments to the PR?
```

### Example 3: Merge PR

**User**:
```
Claude, merge PR #1234 with squash merge and delete source branch.

Organization: contoso
Project: MyApp
Repo: backend
```

**Claude** (using this skill):
1. Validates PR is ready (approvals, policies, checks)
2. Completes PR with squash merge
3. Deletes source branch
4. Returns:

```
✓ Pull request #1234 merged successfully

  Merge Strategy: Squash
  Source Branch: feature/add-authentication (deleted)
  Target Branch: main

  Commit: abc1234 - Add JWT authentication for API endpoints

  Completed by: Claude (on behalf of user)
  Work Items Closed: #5678, #5679
```

### Example 4: PR Analytics

**User**:
```
Claude, show me PR analytics for the last 30 days.

Organization: contoso
Project: MyApp
Repo: backend
```

**Claude** (using this skill):
1. Fetches all PRs from last 30 days
2. Calculates metrics
3. Returns:

```
# PR Analytics Report

**Period**: 2025-10-05 to 2025-11-04 (30 days)
**Total PRs**: 45 (38 completed, 5 active, 2 abandoned)

## Cycle Time Metrics
- **Average Cycle Time**: 18.5 hours
- **Median Cycle Time**: 12.0 hours
- **95th Percentile**: 48.0 hours
- **Fastest PR**: 2.5 hours (PR #1198)
- **Slowest PR**: 96.0 hours (PR #1210)

## PR Size Distribution
- Small (<100 lines): 18 PRs (40%)
- Medium (100-500 lines): 22 PRs (49%)
- Large (>500 lines): 5 PRs (11%)

**Insight**: Large PRs take 3x longer to review. Consider breaking them down.

## Top Reviewers (Last 30 Days)
1. Alice Chen: 28 PRs reviewed, 4.2 hours avg review time
2. Bob Smith: 24 PRs reviewed, 6.1 hours avg review time
3. Carol Lee: 19 PRs reviewed, 3.8 hours avg review time

**Insight**: Bob has slower review times. May need support or prioritization help.

## Top Contributors
1. David Wang: 12 PRs created, 92% merge rate
2. Eve Martinez: 9 PRs created, 100% merge rate
3. Frank Wilson: 8 PRs created, 88% merge rate

## Hot Files (Most Changed in PRs)
1. src/api/routes.py: 15 PRs
2. src/services/user_service.py: 12 PRs
3. tests/test_api.py: 11 PRs

**Insight**: routes.py is frequently changed. Consider refactoring for better modularity.

## Review Efficiency
- **Average Time to First Review**: 3.2 hours
- **Average Review Rounds**: 1.8
- **PR Abandonment Rate**: 4.4%

## Recommendations
1. ✅ Good: Fast time to first review (< 4 hours)
2. ⚠️  Consider: Large PRs slow down the pipeline
3. ⚠️  Monitor: Bob's review load may be too high
4. 💡 Suggestion: Refactor frequently changed files to reduce coupling
```

---

## File Structure

```
rrez-pr-mgr/
├── SKILL.md                    # This file (skill instructions)
├── README.md                   # User-facing documentation
├── INSTALL.md                  # Installation guide
├── pr_creator.py               # PR creation logic
├── pr_reviewer.py              # Code review analysis
├── pr_manager.py               # PR lifecycle management
├── pr_analytics.py             # PR metrics and analytics
├── requirements.txt            # Python dependencies
└── examples/
    ├── example-pr-description.md
    ├── example-review-summary.md
    └── example-analytics-report.md
```

---

## Version

**1.0.0** - Initial release

**Changelog**:
- Azure DevOps MCP integration
- PR creation with smart descriptions
- Automated code review analysis
- PR lifecycle management
- Comprehensive PR analytics

---

## License

MIT License

---

**Generated by**: Claude Code Skills Factory
**Category**: SaaS/Software > DevOps > Azure DevOps > PR Management
**MCP**: Azure DevOps MCP
**Git Integration**: Yes
**Output**: PRs, reviews, analytics reports

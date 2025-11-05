#!/usr/bin/env python3
"""
Process MM-300 JIRA issue and generate GitHub bug report
Uses create-msft-bugreport skill
"""
import json
from datetime import datetime

def sanitize_filename(text):
    """Convert text to safe filename"""
    return ''.join(c if c.isalnum() or c in '-_' else '-' for c in text.lower())[:50]

def main():
    # Load JIRA data
    with open('migrated-bugs/MM-300-jira-data.json', 'r', encoding='utf-8') as f:
        jira_data = json.load(f)

    fields = jira_data['fields']
    issue_key = jira_data['key']

    # Extract data
    title = fields.get('summary', 'Untitled Issue')
    description = fields.get('description', '')
    priority = fields.get('priority', {}).get('name', 'Normal')
    status = fields.get('status', {}).get('name', 'Unknown')
    created = fields.get('created', '')
    updated = fields.get('updated', '')
    reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
    assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
    labels = fields.get('labels', [])
    attachments = fields.get('attachment', [])
    project = fields.get('project', {}).get('name', 'Unknown Project')

    # Create GitHub bug report
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename_safe_title = sanitize_filename(title)
    output_filename = f"migrated-bugs/{issue_key}-{timestamp}-{filename_safe_title}.md"

    # Build GitHub markdown
    github_report = f"""# [BUG] {title}

**Source**: Migrated from JIRA [MM-300](https://rightrez.atlassian.net/browse/MM-300)
**Project**: {project}
**Status**: {status}
**Priority**: {priority}

## Description

{description}

## Environment

- **Project**: {project}
- **Issue Type**: Spike (Research Task)
- **Azure Functions**: Isolated Mode Migration
- **Telemetry**: Application Insights
- **OperationID**: 13d7a73cad0859013f68e6ecefe0ef44

## Problem Statement

OperationIDs are being reused across multiple callback operations after migrating Azure Functions to isolated mode. This causes:

1. **Telemetry Mixing**: Multiple callbacks appear under one OperationID
2. **Information Loss**: Unable to get detailed information for individual callbacks
3. **Debugging Challenges**: Cannot isolate specific callback failures

## Observed Behavior

### Before Migration (Sunday - Good Telemetry)
- Each callback had its own unique telemetry
- Clear separation of operation traces
- Full information available for each callback

### After Migration (Current - Bad Telemetry)
- Multiple callbacks share same OperationID
- Successful and failed callbacks mixed together
- Missing detailed information for individual operations

## Screenshots

The issue is documented with 3 screenshots showing the telemetry differences:

"""

    # Add attachment links
    for i, attachment in enumerate(attachments, 1):
        filename = attachment.get('filename', f'attachment-{i}')
        content_url = attachment.get('content', '')
        github_report += f"{i}. [{filename}]({content_url})\n"

    github_report += f"""
## Azure Portal Links

Investigation links from the original email:
- [Dependency Event 1](https://portal.azure.com/#view/AppInsightsExtension/DetailsV2Blade/...) - October 26, 2025
- [Dependency Event 2](https://portal.azure.com/#view/AppInsightsExtension/DetailsV2Blade/...) - October 28, 2025

## Steps to Reproduce

1. Migrate Azure Function from in-process model to isolated mode
2. Trigger multiple TST callbacks
3. View telemetry in Application Insights
4. Search for OperationID: `13d7a73cad0859013f68e6ecefe0ef44`
5. Observe multiple operations under same ID

## Expected Behavior

Each callback operation should have:
- Unique OperationID
- Isolated telemetry trace
- Complete operation details
- Clear success/failure status

## Actual Behavior

Multiple callbacks share the same OperationID, causing:
- Mixed telemetry (successful + failed operations together)
- Loss of individual operation details
- Difficult to trace specific callback issues

## Severity

**High** - Impacts ability to debug production callback failures and monitor system health

## Related Work

**Research Spike**: This is a research task to investigate the root cause and determine the fix for OperationID reuse in isolated mode Azure Functions.

## Labels

{', '.join(['`' + label + '`' for label in labels])} `migrated-from-jira` `azure-functions` `isolated-mode` `telemetry`

---

## ⚠️ Missing Information

### Required Fields (Update Before Creating GitHub Issue)
- [ ] ⚠️ **Specific .NET Version**: Not specified in JIRA - UPDATE REQUIRED
- [ ] ⚠️ **Azure Functions Runtime Version**: Not specified - UPDATE REQUIRED
- [ ] ⚠️ **Root Cause Analysis**: Research in progress - UPDATE WHEN COMPLETE

### Recommended Fields (Should Complete)
- [ ] **Workaround**: Not yet identified
- [ ] **Fix Timeline**: To be determined after research
- [ ] **Impact Metrics**: Number of affected operations/callbacks

---

## Migration Metadata

**Migrated from**: JIRA MM-300
**Original URL**: https://rightrez.atlassian.net/browse/MM-300
**JIRA Project**: {project}
**Reporter**: {reporter}
**Assignee**: {assignee}
**Created**: {created}
**Last Updated**: {updated}
**Migration Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Migrated by**: Claude (JIRA to Microsoft Bug Migrator Skill)

---

## Additional Context

**Email Chain**: Original issue reported via email on Tuesday, October 28, 2025 9:10 AM
**Team**: Metrics and Monitoring (MM project)
**Priority**: 2. Normal
**Issue Type**: Spike (Research)

This issue requires investigation to identify why Azure Functions isolated mode is reusing OperationIDs instead of generating unique IDs for each callback operation.
"""

    # Write the file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(github_report)

    print(f"✓ Generated GitHub bug report: {output_filename}")
    print(f"  Source: https://rightrez.atlassian.net/browse/MM-300")
    print()
    print("⚠️ Missing Required Fields (update before creating GitHub issue):")
    print("  - Specific .NET Version")
    print("  - Azure Functions Runtime Version")
    print("  - Root Cause Analysis (pending research)")
    print()
    print("Recommended fields to add:")
    print("  - Workaround")
    print("  - Fix Timeline")
    print("  - Impact Metrics")

if __name__ == '__main__':
    main()

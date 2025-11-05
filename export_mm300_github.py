#!/usr/bin/env python3
"""
Export MM-300 to GitHub bug report with attachments
Uses create-msft-bugreport skill
"""
import json
import sys
import os
from datetime import datetime

# Add skill modules to path
sys.path.insert(0, '.claude/skills/create-msft-bugreport')

from jira_reader import JiraReader
from field_validator import GitHubFieldValidator
from microsoft_template import GitHubBugTemplate
from report_generator import BugReportGenerator

def main():
    # Load JIRA data from previous fetch
    with open('migrated-bugs/MM-300-jira-data.json', 'r', encoding='utf-8') as f:
        jira_response = json.load(f)

    # Create JIRA reader
    reader = JiraReader('MM-300')
    parsed_data = reader.extract_issue_data(jira_response)

    # Convert markup to markdown
    parsed_data['description'] = reader.convert_jira_markup_to_markdown(parsed_data['description'])

    # Create output directory structure
    output_base = 'migrated-bugs'
    issue_dir = os.path.join(output_base, 'MM-300')
    os.makedirs(issue_dir, exist_ok=True)

    print(f"Created directory: {issue_dir}")

    # Download attachments
    print("\nDownloading attachments...")
    try:
        downloaded = reader.download_attachments(issue_dir)
        print(f"✓ Downloaded {len(downloaded)} attachments:")
        for filepath in downloaded:
            filename = os.path.basename(filepath)
            print(f"  - {filename}")
    except Exception as e:
        print(f"Warning: Error downloading attachments: {e}")
        print("Continuing with report generation...")

    # Enhanced context from user conversation
    enhanced_description = f"""{parsed_data['description']}

## Additional Context

**Migration Context**:
- This issue occurred during migration to **Azure Functions Isolated Mode**
- Framework: **.NET 8**
- Environment: **Production**
- Impact: **Production rollback trigger** - This bug was a primary reason for rolling back the isolated mode deployment

**Pattern Observed**:
- This is a **recurring issue** that has happened multiple times
- **Temporary Workaround**: Restarting the Azure Function clears the OperationID reuse
- Issue appears specific to isolated mode (did not occur in in-process model)

**Rollback Decision**:
- Production was rolled back from isolated functions to previous version
- Previous version also uses .NET 8 but runs in-process model (not isolated)
- Full telemetry data is available in Azure Application Insights for detailed analysis

**Research Focus**:
This is a research spike to determine:
1. Root cause of OperationID reuse in isolated mode
2. Differences in telemetry initialization between in-process and isolated mode
3. Whether this is a known Azure Functions runtime issue
4. Permanent fix or workaround for production deployment
"""

    parsed_data['description'] = enhanced_description

    # Validate fields
    validator = GitHubFieldValidator(parsed_data)
    validation_result = validator.validate()

    # Add critical missing fields
    validation_result['missing_required'].extend([
        '.NET Version (8.0 confirmed, need specific patch)',
        'Azure Functions Runtime Version',
        'Root Cause Analysis (pending research)'
    ])

    validation_result['missing_recommended'].extend([
        'Permanent Fix or Workaround',
        'Reproduction Steps (non-production)',
        'Known Microsoft Issues Check'
    ])

    # Generate GitHub bug report
    template = GitHubBugTemplate(parsed_data, validation_result)
    markdown = template.generate_markdown()

    # Enhance markdown with additional sections
    enhanced_sections = """

## Steps to Reproduce

1. Deploy Azure Function to isolated mode (.NET 8)
2. Trigger multiple TST callback operations
3. Monitor Application Insights telemetry
4. Search for OperationID: `13d7a73cad0859013f68e6ecefe0ef44`
5. Observe multiple distinct operations sharing the same OperationID

## Expected Behavior

Each callback operation should have:
- **Unique OperationID** for proper distributed tracing
- Isolated telemetry trace (not mixed with other operations)
- Complete operation details (start, end, dependencies)
- Clear success/failure status per operation

## Actual Behavior

Multiple callback operations share the same OperationID, causing:
- **Telemetry Corruption**: Successful and failed callbacks mixed together
- **Information Loss**: Cannot get detailed information for individual callbacks
- **Debugging Impossibility**: Cannot isolate specific callback failures
- **Production Impact**: Unable to effectively monitor and troubleshoot production issues

## Environment

- **Framework**: .NET 8.0
- **Azure Functions Mode**: Isolated Worker Process (bug occurs) vs In-Process (bug does not occur)
- **Azure Functions Runtime**: [Need to verify version]
- **Application Insights**: P-RREZ-V10-AI
- **Subscription**: ba3bdab0-9c6d-4336-9bba-e938d5bd34cf
- **Resource Group**: P-RREZ-V10-CORE-01RG
- **Environment**: Production
- **Issue Type**: Intermittent (happens periodically)

## Severity

**Critical** - Production rollback trigger

**Impact**:
- Cannot effectively monitor production callback operations
- Unable to debug callback failures in isolated mode
- Blocks migration to Azure Functions isolated mode
- Affects production observability and incident response

## Workaround

**Temporary**: Restart the Azure Function app to clear the OperationID reuse
- This is only a temporary fix
- Issue recurs after some time
- Not a sustainable production solution

**Long-term**: Rolled back to in-process model (non-isolated)
- Previous .NET 8 version without isolated mode
- Issue does not occur in in-process model
- Blocks adoption of isolated mode benefits

## Research Questions

1. **Root Cause**: Why does isolated mode cause OperationID reuse?
2. **Telemetry Initialization**: What changed between in-process and isolated mode?
3. **Activity Context**: Is DistributedContext/Activity being properly propagated?
4. **Azure Functions Runtime**: Is this a known issue in the isolated worker model?
5. **Microsoft Guidance**: Are there documented best practices for telemetry in isolated mode?
6. **Reproducibility**: Can this be reproduced in non-production environments?

"""

    # Insert enhanced sections before the "Missing Information" section
    missing_info_marker = "## ⚠️ Missing Information"
    if missing_info_marker in markdown:
        parts = markdown.split(missing_info_marker)
        markdown = parts[0] + enhanced_sections + "\n---\n\n" + missing_info_marker + parts[1]

    # Save report
    generator = BugReportGenerator(output_dir=output_base, create_issue_subdir=True)
    filepath = generator.save_report(
        markdown,
        'MM-300',
        parsed_data['summary']
    )

    print(f"\n✓ Generated GitHub bug report: {filepath}")
    print(f"  Source: https://rightrez.atlassian.net/browse/MM-300")
    print()
    print("⚠️ Missing Required Fields (update before creating GitHub issue):")
    print("  - Specific .NET 8 patch version")
    print("  - Azure Functions Runtime Version")
    print("  - Root Cause Analysis (pending research)")
    print()
    print("Recommended fields to add:")
    print("  - Permanent Fix or Workaround")
    print("  - Reproduction Steps (non-production)")
    print("  - Known Microsoft Issues Check")
    print()
    print(f"📁 All files saved to: {issue_dir}/")

    # List all files in directory
    files = os.listdir(issue_dir)
    print(f"\nDirectory contents ({len(files)} files):")
    for f in sorted(files):
        size = os.path.getsize(os.path.join(issue_dir, f))
        print(f"  - {f} ({size:,} bytes)")

if __name__ == '__main__':
    main()

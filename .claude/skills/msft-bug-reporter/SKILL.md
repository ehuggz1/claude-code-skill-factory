---
name: msft-bug-reporter
description: Fetches JIRA bugs, sanitizes for public disclosure, and generates Microsoft GitHub bug reports with separate private Azure information
---

# Microsoft Bug Reporter Skill

This skill automates the process of converting JIRA bug reports into sanitized Microsoft GitHub-ready bug reports, while maintaining separate private Azure-specific information for direct submission to Microsoft support.

## Capabilities

- **JIRA Integration**: Fetches bug data from JIRA using Atlassian MCP integration
- **Advanced Sanitization**: Removes PII, internal URLs, credentials, secrets, and Azure resource names to ensure public safety
- **Dual Report Generation**: Creates both public GitHub-ready markdown and private Azure-specific markdown
- **Field Validation**: Validates required and recommended Microsoft bug report fields with completeness scoring
- **Automated Formatting**: Applies Microsoft GitHub bug report template with proper markdown structure

## Input Requirements

### Required Inputs

User must provide:
1. **JIRA Ticket Reference**: JIRA ticket key (e.g., "JIRA-1234") or full JIRA URL
2. **Bug Description**: Brief description of the issue being reported to Microsoft
3. **Confirmation**: Whether to generate the reports after preview

### Optional Inputs

- Additional context not in JIRA
- Specific Azure private information to include in the private report

### JIRA Ticket Requirements

The JIRA ticket should contain:
- **Title/Summary**: Clear bug title
- **Description**: Detailed bug description
- **Steps to Reproduce**: Step-by-step reproduction instructions
- **Environment**: OS, .NET version, Azure services affected
- **Expected vs Actual Behavior**: What should happen vs what happens
- **Attachments**: Screenshots, logs, stack traces (if applicable)

## Output Formats

### Public Report: `bug-report/msft-bug-[jira-key].md`

Sanitized markdown file ready for Microsoft GitHub public repositories:

```markdown
# [Bug Title]

**JIRA Reference**: [JIRA-KEY]
**Date Created**: [ISO Timestamp]
**Sanitization Level**: [Level - e.g., "High - PII/Credentials/Azure Resources Removed"]

## Description
[Sanitized description]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
...

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [Operating System]
- .NET Version: [Version]
- Azure Service: [Service Name - Sanitized]

## Additional Context
[Logs, screenshots, stack traces - all sanitized]

---
*This report was auto-generated from JIRA-[KEY] and sanitized for public disclosure*
```

### Private Report: `bug-report/PRIVATE-[jira-key].md`

**CLEARLY MARKED PRIVATE** - Contains Azure-specific information for direct Microsoft support:

```markdown
# PRIVATE - Azure Specific Information for [Bug Title]

**⚠️ CONFIDENTIAL - DO NOT UPLOAD TO PUBLIC REPOSITORIES ⚠️**

**JIRA Reference**: [JIRA-KEY]
**Date Created**: [ISO Timestamp]
**Public Report**: msft-bug-[jira-key].md

## Azure Resource Information

- **Subscription ID**: [Full Azure Subscription ID]
- **Resource Group**: [Resource Group Name]
- **Resource Names**: [Actual resource names]
- **Region**: [Azure region]
- **Tenant ID**: [Tenant ID if applicable]

## Internal URLs/Paths

[Original internal URLs that were sanitized in public report]

## Original Error Messages

[Complete error messages with Azure resource names]

## Additional Private Context

[Any information that should only go to Microsoft support directly]

---
*This file contains sensitive information. Share only through secure Microsoft support channels.*
```

### Metadata Output: Sanitization Log

Embedded in both reports:
- Timestamp of generation
- JIRA reference
- List of sanitization actions performed (e.g., "Removed 3 email addresses, 2 Azure subscription IDs, 1 API key")

## How to Use

### Basic Usage

**Trigger phrases** (skill auto-invokes):
- "Create a Microsoft bug report from JIRA-1234"
- "Generate MSFT bug report for JIRA-5678"
- "Report JIRA-9012 to Microsoft GitHub"

### Workflow

1. **Provide JIRA Reference**: "Create Microsoft bug report from JIRA-1234"
2. **Skill Fetches JIRA Data**: Retrieves bug information via Atlassian MCP
3. **Field Validation**: Checks for required/recommended Microsoft bug fields
4. **Sanitization Preview**: Shows what will be removed (PII, credentials, Azure resources)
5. **User Confirmation**: Review and confirm report generation
6. **Report Generation**: Creates public and private markdown files in `bug-report/` directory
7. **Next Steps Guidance**: Instructions for uploading to Microsoft GitHub and submitting private info

### Example Invocation

```
User: "Create a Microsoft bug report from JIRA-4567 about Azure App Service authentication failures"

Skill response:
1. Fetches JIRA-4567 data
2. Shows field validation results
3. Previews sanitization actions
4. Generates both reports in bug-report/ directory
5. Provides next steps for submission
```

## Scripts

This skill uses the following Python modules for implementation:

### Core Modules

**jira_fetcher.py**
- Fetches JIRA issue data via Atlassian MCP integration
- Extracts title, description, steps, environment, attachments
- Returns typed Dict structure with JIRA data
- **Key Function**: `fetch_jira_issue(issue_key: str) -> Dict[str, Any]`

**sanitizer.py**
- Advanced text sanitization for public disclosure
- Removes: PII (emails, names, IPs), internal URLs/paths, credentials/secrets, Azure resource names
- Uses compiled regex patterns for performance
- Maintains sanitization log of all actions
- **Key Functions**:
  - `sanitize_text(text: str) -> Tuple[str, List[str]]`
  - `sanitize_jira_data(jira_data: Dict) -> Tuple[Dict, List[str]]`

**msft_template.py**
- Microsoft GitHub bug report markdown template
- Formats sections: Title, Description, Steps, Expected/Actual Behavior, Environment
- Ensures proper markdown structure (headers, code blocks, lists)
- **Key Function**: `generate_msft_report(sanitized_data: Dict, metadata: Dict) -> str`

**field_validator.py**
- Validates required and recommended Microsoft bug report fields
- Calculates completeness score (e.g., 8/10 fields present)
- Provides missing field warnings
- **Key Function**: `validate_fields(jira_data: Dict) -> Dict[str, Any]`

**report_generator.py**
- Generates public and private markdown files
- Creates bug-report/ directory if needed
- Writes files with proper encoding and timestamps
- **Key Functions**:
  - `generate_public_report(data: Dict, output_path: str) -> str`
  - `generate_private_report(data: Dict, output_path: str) -> str`

## Detailed Workflow

### Step-by-Step Process

1. **User Invocation**
   - User provides JIRA ticket key (e.g., "JIRA-1234")
   - Skill extracts ticket key from various formats (JIRA-1234, full URL, etc.)

2. **JIRA Data Retrieval** (jira_fetcher.py)
   - Calls `mcp__atlassian__jira_get_issue(issue_key)`
   - Extracts: summary, description, customfield data, attachments
   - Handles missing/null fields gracefully
   - Returns structured data dictionary

3. **Field Validation** (field_validator.py)
   - Checks for required fields: Title, Description, Steps to Reproduce
   - Checks for recommended fields: Expected Behavior, Actual Behavior, Environment, Workaround
   - Calculates completeness score (e.g., 7/10)
   - Warns user if critical fields are missing

4. **Sanitization Process** (sanitizer.py)
   - **PII Removal**: Emails, names, IP addresses → `[REDACTED-PII]`
   - **Internal URLs**: Company URLs, internal paths → `[REDACTED-URL]`
   - **Credentials**: API keys, passwords, tokens → `[REDACTED-CREDENTIAL]`
   - **Azure Resources**: Subscription IDs, resource names → `[REDACTED-AZURE-RESOURCE]`
   - Logs all sanitization actions for transparency

5. **Preview & Confirmation**
   - Shows sanitization summary: "Will remove: 2 emails, 1 API key, 3 Azure resource names"
   - Shows field validation results: "Completeness: 8/10 fields present"
   - Asks user: "Generate reports? (yes/no)"

6. **Report Generation** (report_generator.py + msft_template.py)
   - Creates `bug-report/` directory if it doesn't exist
   - Generates public report: `bug-report/msft-bug-[jira-key].md` (sanitized)
   - Generates private report: `bug-report/PRIVATE-[jira-key].md` (with Azure details)
   - Includes metadata headers in both files

7. **Next Steps Guidance**
   - Instructions to upload public report to Microsoft GitHub
   - Instructions to submit private report through Microsoft support channels
   - Reminder to NOT upload PRIVATE-*.md to public repositories

## Best Practices

### Before Generating Reports

1. **Review JIRA Ticket**: Ensure JIRA ticket is complete with all necessary information
2. **Field Completeness**: Aim for 8/10 or higher field completeness score
3. **Preview Sanitization**: Always review what will be sanitized before confirming
4. **Azure Information**: Have Azure subscription IDs, resource names ready for private report

### After Generating Reports

1. **Review Public Report**: Manually verify all sensitive information is removed
2. **Verify Private Report**: Ensure all Azure-specific details are captured
3. **Separate Submission**: NEVER upload PRIVATE-*.md to public GitHub repositories
4. **Track Reports**: Keep generated reports in bug-report/ for reference

### Security Considerations

- **Sanitization is Pattern-Based**: While comprehensive, manual review is still recommended
- **Private Files**: Add `bug-report/PRIVATE-*.md` to .gitignore if in a git repo
- **Credential Detection**: Skill detects common patterns, but custom credentials may need manual removal
- **Azure Resource Redaction**: Generic Azure resource patterns are removed, but verify specific cases

## Limitations

1. **JIRA Access Required**: Requires Atlassian MCP integration configured with JIRA credentials
2. **Pattern-Based Sanitization**: Uses regex patterns; may miss uncommon credential formats
3. **Manual Review Recommended**: Automated sanitization should be verified manually before public upload
4. **No Direct GitHub Upload**: Generates markdown files locally; user must upload manually
5. **JIRA Field Mapping**: Assumes standard JIRA fields; custom fields may need manual extraction
6. **English Language**: Sanitization patterns optimized for English text
7. **Azure-Specific**: Private report structure optimized for Azure issues; may need adaptation for other cloud providers

## Context Considerations

- **Main SKILL.md**: ~230 lines (implementation delegated to Python modules)
- **Total Implementation**: ~600-700 lines across 5 Python modules
- **Context Efficiency**: Uses modular architecture to keep Claude Code main context minimal
- **Type Safety**: All modules use type hints for clear data contracts

---

**Version**: 1.0
**Last Updated**: 2025-01-04
**Maintained By**: Skills Factory
---
name: create-msft-bugreport
description: Retrieves JIRA issues via Atlassian MCP and generates GitHub-compliant bug reports with validation of required and recommended fields
---

# Create Microsoft Bug Report

This skill retrieves bug information from JIRA issues and generates Microsoft GitHub-compliant bug report markdown files with comprehensive field validation and missing data tracking.

## Capabilities

- **JIRA Issue Retrieval**: Fetch complete issue data via Atlassian MCP
- **GitHub Format Conversion**: Transform JIRA wiki markup to GitHub markdown
- **Field Validation**: Check required and recommended fields against GitHub bug template
- **Missing Field Detection**: Generate checklists and warnings for incomplete data
- **Custom Output Location**: Save reports to user-specified directories
- **JIRA Field Mapping**: Automatic mapping of JIRA fields to GitHub issue format

## Input Requirements

**Required Input:**
- **JIRA Issue Key**: The issue identifier (e.g., "PROJ-123", "BUG-456")
- **Output Directory**: Where to save the generated markdown file (can prompt user)

**Optional Input:**
- **Additional Context**: Any extra information to include in the report
- **Custom Mappings**: Override default JIRA → GitHub field mappings

**Atlassian MCP Required:**
- This skill requires the Atlassian MCP server to be configured
- Uses `mcp__atlassian__jira_get_issue` to retrieve issue data

## Output Formats

**GitHub Issue Markdown:**
- Complete bug report following GitHub's standard template
- Proper markdown formatting (not JIRA wiki markup)
- Code blocks with correct syntax highlighting
- Embedded links and references

**Missing Fields Section:**
- Required fields checklist (must complete)
- Recommended fields checklist (should complete)
- Warning badges for critical missing data
- Placeholder text for manual updates

**Directory Structure:**
```
{output-dir}/
  {JIRA-KEY}/
    {JIRA-KEY}-{timestamp}-{sanitized-title}.md
    attachment1.png
    attachment2.png
    ...

Example: migrated-bugs/PROJ-123/
  PROJ-123-20251104-153045-nullreferenceexception-orderprocessor.md
  screenshot-error.png
  stack-trace.txt
```

Each JIRA issue gets its own subdirectory containing:
- The bug report markdown file
- All downloaded attachments from JIRA
- Ready to upload to GitHub as a complete package

## How to Use

**Basic Usage:**
```
Claude, export JIRA issue PROJ-123 to GitHub bug report format
```

**With Output Directory:**
```
Claude, migrate JIRA issue BUG-456 to Microsoft GitHub format and save to migrated-bugs/
```

**Multiple Issues (user will call skill multiple times):**
```
Claude, export these JIRA issues to GitHub:
- PROJ-123
- PROJ-124
- PROJ-125

Save them to migrated-bugs/
```

## Scripts

- **jira_reader.py**: Retrieves JIRA issues using Atlassian MCP tools and downloads attachments
- **microsoft_template.py**: Formats bug reports for GitHub Issues with local attachment references
- **field_validator.py**: Validates required and recommended fields
- **report_generator.py**: Generates final markdown output with issue-specific subdirectories

## Workflow

When this skill is invoked, Claude will:

1. **Retrieve JIRA Issue**
   - Use `mcp__atlassian__jira_get_issue` with the provided issue key
   - Extract all relevant fields from the JIRA response
   - Parse JIRA wiki markup content
   - Identify all attachments for download

2. **Download Attachments**
   - Create issue-specific subdirectory: `{output-dir}/{JIRA-KEY}/`
   - Download all attachments from JIRA to the subdirectory
   - Update attachment references to point to local files
   - Handle download errors gracefully (continues with other attachments)

3. **Validate Fields**
   - Check for GitHub-required fields (Title, Description, Steps, Expected, Actual, Environment, Severity)
   - Check for recommended fields (Workaround, Related Issues, Screenshots, Root Cause)
   - Generate missing fields lists

4. **Convert to GitHub Format**
   - Map JIRA fields to GitHub issue structure
   - Convert JIRA wiki markup → GitHub markdown
   - Format code blocks, tables, and lists properly
   - Reference local attachment files (not URLs)
   - Add migration metadata

5. **Generate Report**
   - Create complete GitHub-compliant markdown
   - Add missing fields section with checkboxes and warnings
   - Include JIRA source link and migration timestamp
   - Save to issue subdirectory: `{output-dir}/{JIRA-KEY}/{JIRA-KEY}-{timestamp}-{title}.md`

6. **Return Results**
   - Confirm file location and attachments downloaded
   - Summarize missing fields that need manual update
   - Provide JIRA source link
   - List all files in the issue directory

## Field Mapping (JIRA → GitHub)

**Required Fields:**
- JIRA Summary → GitHub Title
- JIRA Description → GitHub Description
- JIRA Description (steps section) → Steps to Reproduce
- JIRA Description (expected section) → Expected Behavior
- JIRA Description (actual section) → Actual Behavior
- JIRA Environment field → Environment section
- JIRA Priority → GitHub Severity label

**Recommended Fields:**
- JIRA Comments → Workaround (if marked as workaround)
- JIRA Links → Related Issues
- JIRA Attachments → Screenshots section (with links)
- JIRA Root Cause field → Root Cause Analysis

**Metadata:**
- JIRA Labels → GitHub Tags (+ "migrated-from-jira")
- JIRA Fix Version → Affected Version
- JIRA Reporter → Migration metadata
- JIRA Created Date → Migration metadata

## GitHub Bug Report Template

The generated markdown follows this structure:

```markdown
# [BUG] {Title from JIRA}

**Source**: Migrated from JIRA [{issue-key}]({jira-url})

## Description
{Converted from JIRA description}

## Steps to Reproduce
1. {Step 1}
2. {Step 2}
3. {Step 3}

## Expected Behavior
{What should happen}

## Actual Behavior
{What actually happens}

## Environment
- **OS**: {Operating system}
- **.NET Version**: {Framework version}
- **Component**: {Component name}
- **Affected Version**: {Version}

## Stack Trace / Error Output
```csharp
{Exception or error details}
```

## Severity
**{High/Medium/Low}** - {Impact description}

## Workaround
{If available}

## Related Issues
- #{related-issue-1}
- #{related-issue-2}

## Screenshots
{Attachment links if available}

## Root Cause Analysis
{If available in JIRA}

---

## ⚠️ Missing Information

### Required Fields (Update Before Creating GitHub Issue)
- [ ] ⚠️ **.NET Version**: Not specified in JIRA - UPDATE REQUIRED
- [ ] ⚠️ **OS Information**: Missing - UPDATE REQUIRED

### Recommended Fields (Should Complete)
- [ ] **Workaround**: Not documented
- [ ] **Screenshots**: No attachments found
- [ ] **Related Issues**: No links in JIRA

---

**Migration Metadata**
**Migrated from**: JIRA {issue-key}
**Original URL**: {jira-url}
**Migration Date**: {timestamp}
**Migrated by**: Claude (JIRA to Microsoft Bug Migrator Skill)
```

## Best Practices

1. **Always Retrieve Full Issue**: Use `expand` parameters to get all JIRA fields including comments, attachments, and links

2. **Validate Before Generating**: Run field validation first to identify missing data early

3. **Preserve Code Formatting**: Convert JIRA `{code:csharp}...{code}` to GitHub ```csharp...``` correctly

4. **Link Preservation**: Convert JIRA issue links to relative GitHub issue references when possible

5. **Prompt for Missing Info**: If critical fields are missing, ask user if they want to provide them before generating

6. **Directory Creation**: Automatically create output directory if it doesn't exist

## Limitations

- **Requires Atlassian MCP**: Cannot retrieve JIRA data without MCP server configured
- **One Issue at a Time**: Does not support batch migration (user must call skill multiple times)
- **Manual Field Updates**: Generated reports may require manual completion of missing fields
- **No Direct GitHub Creation**: Generates markdown files only, does not create GitHub issues directly
- **JIRA Wiki Markup**: Complex JIRA macros may not convert perfectly to markdown
- **Custom Fields**: JIRA custom fields may need manual mapping configuration

## Troubleshooting

**Error: "Atlassian MCP not available"**
- Install Atlassian MCP server: https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian
- Configure in Claude Code settings
- Restart Claude Code

**Error: "JIRA issue not found"**
- Verify issue key format (e.g., "PROJ-123")
- Check JIRA permissions (user must have access to issue)
- Ensure issue exists in JIRA

**Error: "Permission denied creating directory"**
- Create directory manually first
- Check file system permissions
- Use different output directory

**Missing fields in output**
- JIRA issue may not have all required data
- Check ⚠️ Missing Information section in generated file
- Manually update fields before creating GitHub issue

## Example Usage

**Example 1: Single Issue Migration**

**User:**
```
Claude, export JIRA issue ECOM-1234 to GitHub bug report format.
Save it to migrated-bugs/
```

**Claude (using this skill):**
1. Retrieves JIRA issue ECOM-1234 via Atlassian MCP
2. Validates fields (finds .NET version missing)
3. Generates GitHub-compliant markdown with missing fields checklist
4. Saves to `migrated-bugs/ECOM-1234-20251104-153045-nullref-orderprocessor.md`
5. Reports:
```
✓ Generated GitHub bug report: migrated-bugs/ECOM-1234-20251104-153045-nullref-orderprocessor.md
  Source: https://company.atlassian.net/browse/ECOM-1234

⚠️ Missing Required Fields (update before creating GitHub issue):
  - .NET Version
  - OS Information

Recommended fields to add:
  - Workaround
  - Screenshots
```

**Example 2: Issue with Complete Data**

**User:**
```
Claude, migrate JIRA issue PAY-567 to GitHub format, save to bugs/
```

**Claude (using this skill):**
1. Retrieves JIRA issue PAY-567
2. Validates fields (all required fields present)
3. Generates complete GitHub bug report
4. Reports:
```
✓ Generated GitHub bug report: bugs/PAY-567-20251104-154022-invalidop-paymentservice.md
  Source: https://company.atlassian.net/browse/PAY-567

✓ All required fields present
✓ All recommended fields present

Report is ready to create GitHub issue.
```

## Installation

**Project-level:**
```bash
mkdir -p .claude/skills/jira-to-microsoft-bug-migrator
cp -r generated-skills/jira-to-microsoft-bug-migrator/* .claude/skills/jira-to-microsoft-bug-migrator/
```

**User-level:**
```bash
mkdir -p ~/.claude/skills/jira-to-microsoft-bug-migrator
cp -r generated-skills/jira-to-microsoft-bug-migrator/* ~/.claude/skills/jira-to-microsoft-bug-migrator/
```

**Verify Atlassian MCP:**
Ask Claude: "Do you have access to Atlassian MCP tools?"

---

**Version**: 1.0.0
**Generated by**: Claude Code Skills Factory
**Category**: SaaS/Software > Bug Management > JIRA Integration > GitHub Migration
**MCP**: Atlassian MCP (JIRA)

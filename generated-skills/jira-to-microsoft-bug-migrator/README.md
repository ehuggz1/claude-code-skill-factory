# JIRA to Microsoft Bug Migrator

**Export JIRA issues to GitHub-compliant bug reports with field validation and missing data tracking**

---

## Quick Start

### 1. Install the Skill

**Project-level:**
```bash
mkdir -p .claude/skills/jira-to-microsoft-bug-migrator
cp -r generated-skills/jira-to-microsoft-bug-migrator/* .claude/skills/jira-to-microsoft-bug-migrator/
```

**User-level (recommended):**
```bash
mkdir -p ~/.claude/skills/jira-to-microsoft-bug-migrator
cp -r generated-skills/jira-to-microsoft-bug-migrator/* ~/.claude/skills/jira-to-microsoft-bug-migrator/
```

### 2. Verify Atlassian MCP is Configured

This skill requires the Atlassian MCP server to retrieve JIRA issues.

**Check if MCP is available:**
```
Ask Claude: "Do you have access to Atlassian MCP tools?"
```

**If not installed**, follow the setup guide:
https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian

### 3. Use the Skill

**Example:**
```
Claude, export JIRA issue ECOM-1234 to GitHub bug report format.
Save it to migrated-bugs/
```

---

## Features

### JIRA to GitHub Migration
- **Retrieve JIRA Issues**: Fetch complete issue data via Atlassian MCP
- **Convert Format**: Transform JIRA wiki markup to GitHub markdown
- **Field Mapping**: Automatic mapping of JIRA fields to GitHub issue template
- **Preserve Links**: Convert JIRA attachments and issue links

### Field Validation
- **Required Fields Check**: Validates against GitHub's standard bug template
- **Recommended Fields**: Identifies missing optional fields
- **Environment Validation**: Checks for OS and .NET version
- **Completeness Score**: Calculate percentage of fields present

### Missing Data Tracking
- **Checklist Generation**: Creates checkbox list for missing fields
- **Warning Badges**: Highlights critical missing data with ⚠️
- **Placeholder Text**: Adds [TODO] markers for manual updates
- **Field Reasons**: Explains why each field is missing

### GitHub-Compliant Output
- **Standard Template**: Follows GitHub's bug report structure
- **Markdown Format**: Proper GitHub markdown (not JIRA wiki markup)
- **Code Highlighting**: Converts {code:csharp} to ```csharp
- **Migration Metadata**: Links back to original JIRA issue

---

## Usage Examples

### Example 1: Complete Migration

**Input:**
```
Claude, export JIRA issue ECOM-1234 to GitHub format, save to migrated-bugs/
```

**JIRA Issue Has:**
- ✓ Summary, Description, Steps, Expected, Actual
- ✓ Environment with OS and .NET version
- ✓ Workaround in comments
- ✓ Related issue links
- ✓ Screenshot attachments
- ✓ Root cause analysis

**Output:**
```
✓ Generated GitHub bug report: migrated-bugs/ECOM-1234-20251104-153045-nullref-orderprocessor.md
  Source: https://company.atlassian.net/browse/ECOM-1234

✓ All required fields present
✓ All recommended fields present
✓ Completeness: 100%

Report is ready to create GitHub issue.
```

### Example 2: Missing Fields

**Input:**
```
Claude, migrate JIRA issue PAY-567 to GitHub format, save to bugs/
```

**JIRA Issue Has:**
- ✓ Summary, Description
- ⚠️ No steps to reproduce
- ⚠️ Environment field empty
- ⚠️ No workaround
- ⚠️ No attachments

**Output:**
```
✓ Generated GitHub bug report: bugs/PAY-567-20251104-154022-invalidop-paymentservice.md
  Source: https://company.atlassian.net/browse/PAY-567

⚠️ Missing Required Fields:
  - Steps to Reproduce
  - OS
  - .NET Version

Recommended fields to add:
  - Workaround
  - Screenshots

Completeness: 54.5%

Review the "Missing Information" section in the generated file and update before creating GitHub issue.
```

### Example 3: Multiple Issues

**Input:**
```
Claude, export these JIRA issues to GitHub format:
- PROJ-123
- PROJ-124
- PROJ-125

Save to migrated-bugs/
```

**Output:**
```
✓ Exported 3 issues to migrated-bugs/

1. PROJ-123: All fields present (100%)
2. PROJ-124: Missing .NET version (90%)
3. PROJ-125: Missing steps and environment (63%)

All files ready for review.
```

---

## File Structure

```
jira-to-microsoft-bug-migrator/
├── SKILL.md                    # Claude's instructions
├── README.md                   # This file
├── HOW_TO_USE.md              # Quick usage guide
├── jira_reader.py             # Retrieve JIRA via Atlassian MCP
├── microsoft_template.py      # GitHub formatting logic
├── field_validator.py         # Required/recommended field validation
├── report_generator.py        # Save markdown files
├── sample_input.json          # Example JIRA response
├── expected_output.json       # Example output
└── requirements.txt           # Dependencies (none!)
```

---

## Field Mapping Reference

| JIRA Field | GitHub Field | Required | Notes |
|------------|-------------|----------|-------|
| Summary | Title | ✓ | Prefixed with [BUG] |
| Description | Description | ✓ | Converted from wiki markup |
| Description sections | Steps/Expected/Actual | ✓ | Parsed from headings |
| Environment | Environment section | ✓ | Must include OS + .NET |
| Priority | Severity | ✓ | Maps High→High, etc. |
| Fix Version | Affected Version | - | First version listed |
| Labels | Tags | - | + "migrated-from-jira" |
| Comments | Workaround | - | If "workaround" mentioned |
| Issue Links | Related Issues | - | Converted to markdown links |
| Attachments | Screenshots | - | Links to JIRA attachments |
| Custom fields | Root Cause | - | If root cause field exists |

---

## GitHub Bug Report Template

Generated reports follow this structure:

```markdown
# [BUG] {Title}

**Source**: Migrated from JIRA [{KEY}]({URL})

## Description
{Converted from JIRA}

## Steps to Reproduce
1. {Step 1}
2. {Step 2}

## Expected Behavior
{What should happen}

## Actual Behavior
{What actually happens}

## Environment
- **OS**: {Operating System}
- **.NET Version**: {Framework version}
- **Component**: {Component name}
- **Affected Version**: {Version}

## Stack Trace / Error Output
```csharp
{Exception details}
```

## Severity
**{High/Medium/Low}** - {Description}

## Workaround
{If available}

## Related Issues
- #{issue-1}

## Screenshots
{Attachment links}

## Root Cause Analysis
{If available}

---

## ⚠️ Missing Information

### Required Fields
- [ ] ⚠️ {Field}: {Reason}

### Recommended Fields
- [ ] {Field}: {Reason}

---

**Migration Metadata**
- Migrated from: JIRA {KEY}
- Original URL: {URL}
- Migration Date: {Timestamp}
```

---

## Configuration

### Output Directory

Default: `migrated-bugs/`

**Change via request:**
```
Claude, save to bugs/from-jira/ instead
```

### Required Fields

Based on GitHub's standard bug template:
- Title
- Description
- Steps to Reproduce
- Expected Behavior
- Actual Behavior
- Environment (OS + .NET Version)
- Severity

### Recommended Fields

Optional but helpful:
- Workaround
- Related Issues
- Screenshots/Attachments
- Root Cause Analysis

---

## Troubleshooting

### Error: "Atlassian MCP tools not available"

**Solution:**
1. Install Atlassian MCP server
2. Configure in Claude Code settings
3. Restart Claude Code
4. Verify: "Claude, do you have access to mcp__atlassian__jira_get_issue?"

### Error: "JIRA issue not found"

**Solution:**
1. Verify issue key format (uppercase, e.g., "PROJ-123" not "proj-123")
2. Check JIRA permissions (user must have read access)
3. Confirm issue exists in JIRA

### Error: "Permission denied creating directory"

**Solution:**
1. Create directory manually: `mkdir migrated-bugs`
2. Check file system permissions
3. Use different output directory

### Missing fields in report

**Expected Behavior:**
- JIRA may not contain all required GitHub fields
- Check "⚠️ Missing Information" section in generated file
- Manually update fields before creating GitHub issue

### JIRA wiki markup not converting

**Solution:**
- Common macros convert automatically
- Complex custom macros may need manual formatting
- Check generated file and adjust if needed

---

## Advanced Usage

### Validate Before Generating

```
Claude, check JIRA issue PROJ-123 and tell me which fields are missing before generating the report.
```

### Custom Output Path

```
Claude, export PROJ-123 to ~/Documents/github-bugs/
```

### Include Additional Context

```
Claude, export PROJ-123 and add a note that this is blocking release 2.4.
```

---

## Requirements

**Required:**
- Claude Code with Atlassian MCP server configured
- Python 3.7+ (included with Claude Code)
- JIRA read permissions for the issues you want to export

**Optional:**
- None! Uses only Python standard library

---

## Version

**1.0.0** - Initial release

**Features:**
- Atlassian MCP integration for JIRA
- GitHub bug report template formatting
- Field validation (required + recommended)
- Missing field detection and checklists
- JIRA wiki markup → GitHub markdown conversion
- User-specified output directories
- Migration metadata tracking

---

## License

MIT License

---

## Support

**Questions or Issues?**
- Review [SKILL.md](SKILL.md) for Claude's detailed instructions
- Check [HOW_TO_USE.md](HOW_TO_USE.md) for quick examples
- See [sample_input.json](sample_input.json) and [expected_output.json](expected_output.json) for examples

---

**Generated by**: Claude Code Skills Factory
**Category**: SaaS/Software > Bug Management > JIRA Integration > GitHub Migration
**MCP**: Atlassian MCP (JIRA)
**Output**: GitHub-compliant markdown bug reports

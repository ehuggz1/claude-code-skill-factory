# How to Use This Skill

Hey Claude—I just added the "jira-to-microsoft-bug-migrator" skill. Can you export JIRA issue PROJ-123 to GitHub bug report format and save it to migrated-bugs/?

## Example Invocations

**Example 1: Basic Migration**
```
Hey Claude—I just added the "jira-to-microsoft-bug-migrator" skill.
Can you export JIRA issue ECOM-1234 to GitHub bug report format?
Save it to migrated-bugs/
```

**Example 2: Custom Output Directory**
```
Hey Claude—I just added the "jira-to-microsoft-bug-migrator" skill.
Can you migrate JIRA issue BUG-456 to Microsoft GitHub format and save to bugs/from-jira/?
```

**Example 3: Multiple Issues**
```
Hey Claude—I just added the "jira-to-microsoft-bug-migrator" skill.
Can you export these JIRA issues to GitHub format:
- PROJ-123
- PROJ-124
- PROJ-125

Save them all to migrated-bugs/
```

**Example 4: Check What's Missing**
```
Hey Claude—I just added the "jira-to-microsoft-bug-migrator" skill.
Can you export JIRA issue PAY-789 and tell me which fields are missing before I create the GitHub issue?
```

## What to Provide

**Required:**
- **JIRA Issue Key**: The issue identifier (e.g., "PROJ-123", "BUG-456")
- **Output Directory**: Where to save the markdown file (optional, defaults to "migrated-bugs")

**Optional:**
- Additional context or notes to include
- Specific fields to validate

## What You'll Get

**When All Fields Are Present:**
```
✓ Generated GitHub bug report: migrated-bugs/ECOM-1234-20251104-153045-nullref-orderprocessor.md
  Source: https://company.atlassian.net/browse/ECOM-1234

✓ All required fields present
✓ All recommended fields present

Report is ready to create GitHub issue.
```

**When Fields Are Missing:**
```
✓ Generated GitHub bug report: migrated-bugs/PROJ-456-20251104-154022-invalidop-processor.md
  Source: https://company.atlassian.net/browse/PROJ-456

⚠️ Missing Required Fields (update before creating GitHub issue):
  - .NET Version
  - OS Information

Recommended fields to add:
  - Workaround
  - Screenshots

The generated report includes a checklist for these missing fields.
```

**The Generated File Contains:**
- GitHub-compliant bug report markdown
- All available JIRA data converted to GitHub format
- Missing fields section with checkboxes for manual updates
- Migration metadata linking back to JIRA
- Ready to paste into GitHub issue or save as documentation

## Prerequisites

This skill requires:
- **Atlassian MCP Server** configured and connected
- **JIRA Access**: User must have permission to read the issue
- **File System Access**: Permission to create output directory and files

**Verify MCP is available:**
```
Claude, do you have access to Atlassian MCP tools?
```

If not, see: https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian

## Tips for Best Results

1. **Specify Output Directory**: Always tell Claude where to save the file for easy retrieval

2. **Review Missing Fields**: Check the "Missing Information" section in the generated file before creating a GitHub issue

3. **Batch Processing**: If you have multiple issues, process them in one request to save time

4. **Validate First**: Ask Claude to show you what's missing before generating the full report

5. **Complete Environment Info**: The more complete the JIRA environment field, the better the GitHub report will be

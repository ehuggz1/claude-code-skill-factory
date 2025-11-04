# Installation Guide: C# Bug Documentation Skill

This guide explains how to install the C# Bug Documentation skill in **Claude Code**, **Claude Desktop**, and **Claude Web**.

---

## Option 1: Claude Code (CLI)

### Project-Level Installation

Install the skill for a specific project (recommended for C# projects):

```bash
# Navigate to your C# project
cd /path/to/your/csharp/project

# Create skills directory
mkdir -p .claude/skills

# Extract the skill
unzip /path/to/csharp-bug-documentation.zip -d .claude/skills/

# Verify installation
ls .claude/skills/csharp-bug-documentation/
```

### User-Level Installation

Install the skill globally for all projects:

```bash
# Create user-level skills directory
mkdir -p ~/.claude/skills

# Extract the skill
unzip /path/to/csharp-bug-documentation.zip -d ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/csharp-bug-documentation/
```

### Test the Skill

```bash
# Start Claude Code
claude

# Test the skill
claude> Document this bug in JIRA:
System.NullReferenceException at line 45
Project: TEST
```

---

## Option 2: Claude Desktop

### Installation Steps

1. **Open Claude Desktop**

2. **Navigate to Skills Settings**:
   - Click on your profile icon (top-right)
   - Select **Settings**
   - Click **Skills** tab

3. **Import the Skill**:
   - Click **Import Skill** or **Add Skill**
   - Select the `csharp-bug-documentation.zip` file
   - Click **Open** or **Import**

4. **Verify Installation**:
   - The skill should appear in your skills list
   - Name: "C# Bug Documentation with JIRA Integration"
   - Status: Active

5. **Configure Atlassian MCP** (if not already done):
   - Go to **Settings** → **Integrations**
   - Add **Atlassian MCP** server
   - Follow the connection wizard

### Test the Skill

1. Open a new conversation
2. Type:
   ```
   Claude, document this bug in JIRA:

   NullReferenceException in OrderProcessor.ProcessOrder
   Project: TEST
   ```
3. Claude should use the skill to analyze and create a JIRA issue

---

## Option 3: Claude Web

### Installation Steps

1. **Go to Claude Web**: https://claude.ai

2. **Access Skills Settings**:
   - Click your profile icon (bottom-left)
   - Select **Settings**
   - Navigate to **Skills** section

3. **Upload the Skill**:
   - Click **Upload Skill** or **Import**
   - Drag and drop `csharp-bug-documentation.zip` or click to browse
   - Select the zip file
   - Click **Upload**

4. **Enable the Skill**:
   - Find "C# Bug Documentation" in your skills list
   - Toggle it to **Active**

5. **Configure Atlassian MCP**:
   - In Settings, go to **Integrations**
   - Connect your Atlassian account
   - Authorize JIRA access

### Test the Skill

1. Start a new conversation
2. Ask Claude:
   ```
   Document this C# bug in JIRA:

   InvalidOperationException in PaymentService.ProcessPayments
   Line 78 in PaymentService.cs
   Project: PAY
   ```

---

## Prerequisites

### Required for All Platforms

1. **Atlassian MCP Server**:
   - The skill requires Atlassian MCP to create JIRA issues
   - Install from: https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian
   - Configure with your JIRA credentials

2. **JIRA Account**:
   - Active JIRA project
   - Permission to create bug issues
   - Project key (e.g., "ECOM", "PAY")

3. **Python 3.7+** (for Claude Code/Desktop):
   - Already included with Claude Code and Claude Desktop
   - No additional packages required (uses stdlib only)

### Optional

- **Git**: For version control of generated bug reports
- **C# Project**: For context-aware bug analysis

---

## Verification

### Check Skill is Loaded

**Claude Code**:
```bash
claude> /skills
# Should show "csharp-bug-documentation" in the list
```

**Claude Desktop / Web**:
- Go to Settings → Skills
- Verify "C# Bug Documentation" appears and is Active

### Check Atlassian MCP Connection

Ask Claude:
```
Do you have access to mcp__atlassian__jira_create_issue?
```

Expected response:
```
Yes, I have access to the Atlassian MCP tools including:
- mcp__atlassian__jira_create_issue
- mcp__atlassian__jira_get_issue
- mcp__atlassian__jira_search_issues
```

---

## Configuration

### Set JIRA Project Key

You can configure a default JIRA project key:

**Claude Code** (create config file):
```bash
# Create skill config
mkdir -p .claude/skills/csharp-bug-documentation/config
cat > .claude/skills/csharp-bug-documentation/config/settings.json << EOF
{
  "default_project_key": "ECOM",
  "default_priority": "High",
  "auto_create_bugs_dir": true
}
EOF
```

**Claude Desktop/Web**:
- The skill will prompt you for the project key when needed
- Or include it in your request: `Project: ECOM`

---

## Troubleshooting

### Skill Not Loading

**Claude Code**:
```bash
# Check skill directory
ls .claude/skills/csharp-bug-documentation/

# Verify SKILL.md exists
cat .claude/skills/csharp-bug-documentation/SKILL.md | head -20

# Restart Claude Code
exit
claude
```

**Claude Desktop/Web**:
- Go to Settings → Skills
- Remove and re-import the skill
- Restart the application

### MCP Connection Issues

1. **Check MCP server is running**:
   - Claude Desktop: Settings → Integrations → Atlassian MCP
   - Status should be "Connected"

2. **Verify credentials**:
   - Test JIRA access manually: https://your-domain.atlassian.net
   - Check API token is valid

3. **Re-authorize**:
   - Settings → Integrations → Atlassian
   - Click "Re-authorize" or "Reconnect"

### Permission Errors

**Error**: "Permission denied creating bugs/ directory"

**Solution**:
```bash
# Create bugs directory manually
mkdir bugs
chmod 755 bugs

# Or specify different output path
# (Edit report_generator.py line 17)
```

**Error**: "Cannot create JIRA issue - permission denied"

**Solution**:
- Check your JIRA user has "Create Issues" permission
- Verify project key is correct (uppercase)
- Ask JIRA admin to grant permissions

---

## Uninstallation

### Claude Code

**Project-level**:
```bash
rm -rf .claude/skills/csharp-bug-documentation
```

**User-level**:
```bash
rm -rf ~/.claude/skills/csharp-bug-documentation
```

### Claude Desktop / Web

1. Go to Settings → Skills
2. Find "C# Bug Documentation"
3. Click the trash icon or **Remove**
4. Confirm deletion

---

## File Structure After Installation

```
.claude/skills/csharp-bug-documentation/
├── SKILL.md                          # Instructions for Claude
├── README.md                         # User documentation
├── INSTALL.md                        # This file
├── bug_analyzer.py                   # Bug analysis logic
├── jira_reporter.py                  # JIRA integration
├── report_generator.py               # Markdown reports
├── requirements.txt                  # Dependencies (none!)
├── .gitignore                        # Excludes bugs/ directory
└── examples/
    ├── example-report.md             # Sample output
    └── example-jira-issue.json       # Sample JIRA payload
```

After using the skill, a `bugs/` directory will be created for local reports:

```
bugs/
├── ECOM-1234-20251104-143022-nullreferenceexception-orderprocessor.md
├── PAY-567-20251104-141533-invalidoperationexception-paymentservice.md
└── ...
```

---

## Support

**Issues or Questions?**

1. Check the [README.md](README.md) for usage examples
2. Review [SKILL.md](SKILL.md) for Claude's instructions
3. See [examples/](examples/) for sample outputs
4. Check Atlassian MCP documentation: https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian

---

## Next Steps After Installation

1. ✅ Install the skill (you just did this!)
2. ✅ Verify Atlassian MCP is configured
3. 📝 Test with a simple bug: `"Claude, document this: NullReferenceException at line 10"`
4. 🔍 Review the generated JIRA issue and local report
5. 🚀 Start using it for real C# bugs in your projects!

---

**Skill Version**: 1.0.0
**Platform Compatibility**: Claude Code, Claude Desktop, Claude Web
**MCP Required**: Atlassian MCP (JIRA)
**License**: MIT

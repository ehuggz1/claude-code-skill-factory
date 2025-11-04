# C# Bug Documentation with JIRA Integration

**Analyze C# bugs, create JIRA issues via Atlassian MCP, and generate local Markdown reports**

---

## Purpose

This skill helps you document bugs in C# codebases by:
1. Analyzing C# code and exceptions to identify root causes
2. Creating JIRA bug issues automatically via Atlassian MCP
3. Generating local Markdown reports for reference

---

## When to Use This Skill

Claude will automatically load this skill when you:
- Ask to "document this bug in JIRA"
- Request "create a JIRA issue for this C# bug"
- Say "analyze and report this exception"
- Need to "file a bug report for [code/stacktrace]"
- Request "document this C# bug"

---

## What This Skill Does

**Workflow**:
```
User provides C# code/stacktrace/bug description
    ↓
1. Analyze code to identify root cause
    ↓
2. Create JIRA bug issue (via Atlassian MCP)
    ↓
3. Generate local Markdown report
    ↓
4. Return JIRA issue key + local file path
```

**JIRA Issue Fields**:
- **Summary**: Clear, concise bug title
- **Description**: Formatted with:
  - Environment details
  - Steps to reproduce
  - Expected vs. actual behavior
  - Root cause analysis
  - Code snippets
  - Suggested fixes
- **Issue Type**: Bug
- **Priority**: Critical/High/Medium/Low (based on severity)
- **Labels**: `csharp`, `bug`, `automated`
- **Components**: (derived from code analysis)

**Local Markdown Report**:
- Same content as JIRA issue
- Microsoft-style formatting
- Saved to `bugs/` directory
- Filename: `BUG-{timestamp}-{summary}.md`

---

## Prerequisites

**Atlassian MCP Server Must Be Configured**:

This skill requires the Atlassian MCP server to be installed and connected. The MCP server provides tools like:
- `mcp__atlassian__jira_create_issue`
- `mcp__atlassian__jira_update_issue`
- `mcp__atlassian__jira_get_issue`

**Check if MCP is available**:
Ask Claude: "Do you have access to Atlassian MCP tools?"

**If not installed**, see: https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian

---

## Usage Instructions for Claude

When this skill is invoked:

### Step 1: Analyze the Bug

Use `bug_analyzer.py` to examine the provided:
- C# code snippet
- Exception stacktrace
- Bug description

**Extract**:
- Exception type and message
- File and line number
- Method/class context
- Root cause
- Severity level (Critical/High/Medium/Low)

### Step 2: Create JIRA Issue

Use the Atlassian MCP tool `mcp__atlassian__jira_create_issue` with:

```python
{
  "project_key": "<user's JIRA project key>",
  "issue_type": "Bug",
  "summary": "<concise bug title>",
  "description": """
h2. Environment
- Language: C#
- Component: <component name>
- File: <file path>:<line number>

h2. Description
<1-2 sentence description>

h2. Steps to Reproduce
# <step 1>
# <step 2>
# <step 3>

h2. Expected Behavior
<what should happen>

h2. Actual Behavior
<what actually happens>

{code:csharp}
<exception stacktrace or error output>
{code}

h2. Root Cause
<analysis of why this is happening>

h2. Suggested Fix
{code:csharp}
<fixed code example>
{code}

h2. Impact
- <impact point 1>
- <impact point 2>
  """,
  "priority": "<Critical|High|Medium|Low>",
  "labels": ["csharp", "bug", "automated"],
  "components": ["<component name>"]
}
```

**JIRA Description Formatting**:
- Use JIRA wiki markup (not Markdown)
- Headers: `h2.`, `h3.`
- Code blocks: `{code:csharp}...{code}`
- Lists: `#` for numbered, `*` for bullets

**Prompt user for JIRA project key** if not known.

### Step 3: Generate Local Markdown Report

Use `report_generator.py` to create a Markdown file:

**Content**:
```markdown
# Bug Report: <Summary>

**JIRA Issue**: <issue-key> (<JIRA URL>)

## Severity
**<Critical|High|Medium|Low>** - <impact description>

## Environment
- Language: C#
- Component: <component>
- File: <file>:<line>
- Reported: <timestamp>

## Description
<bug description>

## Steps to Reproduce
1. <step 1>
2. <step 2>
3. <step 3>

## Expected Behavior
<expected>

## Actual Behavior
<actual>

```csharp
<stacktrace or error>
```

## Root Cause
<analysis>

## Suggested Fix
```csharp
<fixed code>
```

## Impact
- <impact 1>
- <impact 2>

---
**JIRA**: <issue-key>
**Generated**: <timestamp>
**Reporter**: Claude (C# Bug Documentation Skill)
```

**Save to**: `bugs/BUG-<timestamp>-<sanitized-summary>.md`

### Step 4: Return Results

Inform the user:
```
✓ Created JIRA issue: <ISSUE-KEY>
  URL: <JIRA URL>

✓ Saved local report: bugs/BUG-<timestamp>-<summary>.md

Summary: <bug title>
Priority: <priority>
Components: <components>
```

---

## Example Usage

### Example 1: NullReferenceException

**User**:
```
Document this bug in JIRA:

public class OrderProcessor {
    public void ProcessOrder(Order order) {
        var total = order.Items.Sum(i => i.Price);
        Console.WriteLine($"Total: {total}");
    }
}

Getting: NullReferenceException when order.Items is null
Project: ECOM
```

**Claude** (using this skill):

1. **Analyzes code**: Identifies missing null check
2. **Creates JIRA issue** in project `ECOM`:
   - Summary: "NullReferenceException in OrderProcessor.ProcessOrder when Items is null"
   - Priority: High
   - Components: OrderProcessing
   - Full description with repro steps, root cause, fix
3. **Saves Markdown**: `bugs/BUG-20251104-143022-nullref-orderprocessor.md`
4. **Returns**:
```
✓ Created JIRA issue: ECOM-1234
  URL: https://your-domain.atlassian.net/browse/ECOM-1234

✓ Saved local report: bugs/BUG-20251104-143022-nullref-orderprocessor.md

Summary: NullReferenceException in OrderProcessor.ProcessOrder when Items is null
Priority: High
Components: OrderProcessing
```

### Example 2: InvalidOperationException from Logs

**User**:
```
File a bug for this exception:

[ERROR] 2025-11-04 14:15:33 - PaymentService crashed
System.InvalidOperationException: Collection was modified; enumeration operation may not execute.
   at System.Collections.Generic.List`1.Enumerator.MoveNextRare()
   at PaymentService.ProcessPendingPayments() in PaymentService.cs:line 45

Project: PAY
```

**Claude** (using this skill):

1. **Analyzes stacktrace**: Collection modification during enumeration
2. **Creates JIRA issue** in project `PAY`:
   - Summary: "InvalidOperationException in PaymentService.ProcessPendingPayments - collection modified during iteration"
   - Priority: Critical
   - Components: Payments
3. **Saves Markdown**: `bugs/BUG-20251104-141533-invalidop-paymentservice.md`
4. **Returns**:
```
✓ Created JIRA issue: PAY-567
  URL: https://your-domain.atlassian.net/browse/PAY-567

✓ Saved local report: bugs/BUG-20251104-141533-invalidop-paymentservice.md

Summary: InvalidOperationException in PaymentService.ProcessPendingPayments
Priority: Critical
Components: Payments
```

---

## MCP Tools Used

This skill relies on these Atlassian MCP tools:

**Primary**:
- `mcp__atlassian__jira_create_issue` - Creates JIRA bug issues

**Optional** (for enhanced workflows):
- `mcp__atlassian__jira_get_project` - Validate project keys
- `mcp__atlassian__jira_search_issues` - Check for duplicate bugs
- `mcp__atlassian__jira_add_comment` - Add updates to existing issues

---

## Configuration

**Required** (prompt user if unknown):
- **JIRA Project Key**: e.g., "ECOM", "PAY", "PLATFORM"
- **Atlassian Domain**: e.g., "your-company.atlassian.net"

**Optional** (use defaults if not specified):
- **Component Mapping**: Map C# namespaces to JIRA components
- **Priority Rules**: Auto-assign priority based on exception type
- **Labels**: Additional labels beyond `csharp`, `bug`, `automated`

**Default Priorities**:
- `Critical`: NullReferenceException, OutOfMemoryException, StackOverflowException, data loss bugs
- `High`: InvalidOperationException, ArgumentException, unhandled exceptions
- `Medium`: Known exceptions with workarounds
- `Low`: Minor issues, cosmetic bugs

---

## Installation

**1. Create skill directory**:
```bash
mkdir -p generated-skills/csharp-bug-documentation
cd generated-skills/csharp-bug-documentation
```

**2. Install skill files** (generated by this build process):
- `SKILL.md` (this file)
- `bug_analyzer.py` - Bug analysis logic
- `jira_reporter.py` - Atlassian MCP integration
- `report_generator.py` - Markdown generation
- `requirements.txt` - Dependencies
- `README.md` - User guide

**3. Copy to Claude skills directory**:

**Project-level**:
```bash
mkdir -p .claude/skills/csharp-bug-documentation
cp -r generated-skills/csharp-bug-documentation/* .claude/skills/csharp-bug-documentation/
```

**User-level** (all projects):
```bash
mkdir -p ~/.claude/skills/csharp-bug-documentation
cp -r generated-skills/csharp-bug-documentation/* ~/.claude/skills/csharp-bug-documentation/
```

**4. Verify Atlassian MCP is configured**:
Ask Claude: "Do you have access to mcp__atlassian__jira_create_issue?"

---

## Testing

**Test 1: Simple Bug**:
```
Claude, document this bug in JIRA:

string[] names = null;
Console.WriteLine(names.Length); // NullReferenceException

Project: TEST
```

**Expected**:
- JIRA issue created in project TEST
- Local Markdown file saved
- Issue includes root cause and fix

**Test 2: Stacktrace**:
```
Claude, file a JIRA bug for this:

System.DivideByZeroException: Attempted to divide by zero.
   at Calculator.Divide(Int32 a, Int32 b) in Calculator.cs:line 12

Project: CALC
```

**Expected**:
- JIRA issue with stacktrace formatted correctly
- Suggested fix includes zero check
- Priority set appropriately

---

## Troubleshooting

**Error: "Atlassian MCP tools not available"**:
- Install Atlassian MCP server
- Configure in Claude Code settings
- Restart Claude Code

**Error: "Invalid project key"**:
- Check JIRA project exists
- Verify user has permission to create issues
- Use uppercase project key (e.g., "ECOM" not "ecom")

**Error: "Permission denied creating bugs/ directory"**:
- Create directory manually: `mkdir bugs`
- Check file system permissions
- Try different output path

---

## Advanced Usage

**Check for duplicate bugs before creating**:
```
Claude, check if this bug exists in JIRA before filing:
<bug description>
```

**Update existing issue instead of creating new**:
```
Claude, update JIRA issue ECOM-1234 with this analysis:
<updated information>
```

**Batch bug reporting**:
```
Claude, analyze these 5 exceptions and create JIRA issues for each:
<multiple stacktraces>
```

---

## File Structure

```
csharp-bug-documentation/
├── SKILL.md                    # This file (skill instructions)
├── README.md                   # User-facing documentation
├── bug_analyzer.py             # C# bug analysis logic
├── jira_reporter.py            # Atlassian MCP integration
├── report_generator.py         # Markdown report generation
├── requirements.txt            # Python dependencies
└── examples/
    ├── example-jira-issue.json # Sample JIRA payload
    └── example-report.md       # Sample Markdown report
```

---

## Version

**1.0.0** - Initial release with JIRA integration

**Changelog**:
- Atlassian MCP integration for JIRA issue creation
- Local Markdown report generation
- C# exception analysis
- Microsoft-style bug documentation
- Auto-priority assignment

---

## License

MIT License

---

**Generated by**: Claude Code Skills Factory
**Category**: SaaS/Software > Bug Documentation > C# > JIRA Integration
**MCP**: Atlassian MCP (JIRA)
**Output**: JIRA issues + Markdown reports

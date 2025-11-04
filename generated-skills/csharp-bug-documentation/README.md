# C# Bug Documentation with JIRA Integration

**Automatically document C# bugs, create JIRA issues via Atlassian MCP, and generate local Markdown reports.**

---

## Quick Start

### 1. Install the Skill

**Project-level** (recommended for C# projects):
```bash
mkdir -p .claude/skills/csharp-bug-documentation
cp -r generated-skills/csharp-bug-documentation/* .claude/skills/csharp-bug-documentation/
```

**User-level** (available across all projects):
```bash
mkdir -p ~/.claude/skills/csharp-bug-documentation
cp -r generated-skills/csharp-bug-documentation/* ~/.claude/skills/csharp-bug-documentation/
```

### 2. Verify Atlassian MCP is Configured

This skill requires the Atlassian MCP server to create JIRA issues.

**Check if MCP is available**:
```
Ask Claude: "Do you have access to Atlassian MCP tools?"
```

**If not installed**, follow the setup guide:
https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian

### 3. Use the Skill

**Example 1: Document a bug from stacktrace**:
```
Claude, document this bug in JIRA:

System.NullReferenceException: Object reference not set to an instance of an object.
   at OrderProcessor.ProcessOrder(Order order) in OrderProcessor.cs:line 45

Project: ECOM
```

**Example 2: Document a bug from code**:
```
Claude, create a JIRA bug for this:

public void ProcessPayment(Payment payment) {
    var total = payment.Items.Sum(i => i.Price); // NullReferenceException here
}

The Items collection is sometimes null.
Project: PAY
```

---

## What This Skill Does

**Workflow**:
1. **Analyzes** C# code/stacktraces to identify root causes
2. **Creates JIRA issue** automatically via Atlassian MCP
3. **Generates local Markdown report** for quick reference
4. **Returns** JIRA issue key + local file path

**JIRA Issue includes**:
- Clear, concise summary
- Environment details (component, file, line number)
- Steps to reproduce
- Expected vs. actual behavior
- Root cause analysis
- Code snippets
- Suggested fixes
- Impact assessment

**Local Markdown Report includes**:
- Same content as JIRA issue
- Microsoft-style formatting
- Link to JIRA issue
- Saved to `bugs/` directory

---

## Usage Examples

### Example 1: NullReferenceException

**Input**:
```
Claude, document this bug in JIRA:

public class OrderProcessor {
    public void ProcessOrder(Order order) {
        var total = order.Items.Sum(i => i.Price);
        Console.WriteLine($"Total: {total}");
    }
}

Getting: NullReferenceException when order.Items is null
Project: ECOM
```

**Output**:
```
✓ Created JIRA issue: ECOM-1234
  URL: https://your-domain.atlassian.net/browse/ECOM-1234

✓ Saved local report: bugs/ECOM-1234-20251104-143022-nullreferenceexception-orderprocessor.md

Summary: NullReferenceException in OrderProcessor.ProcessOrder - missing null check
Priority: High
Components: OrderProcessing
```

### Example 2: InvalidOperationException

**Input**:
```
Claude, file a bug for this exception:

[ERROR] 2025-11-04 14:15:33 - PaymentService crashed
System.InvalidOperationException: Collection was modified; enumeration operation may not execute.
   at System.Collections.Generic.List`1.Enumerator.MoveNextRare()
   at PaymentService.ProcessPendingPayments() in PaymentService.cs:line 45

Project: PAY
```

**Output**:
```
✓ Created JIRA issue: PAY-567
  URL: https://your-domain.atlassian.net/browse/PAY-567

✓ Saved local report: bugs/PAY-567-20251104-141533-invalidoperationexception-paymentservice.md

Summary: InvalidOperationException in PaymentService.ProcessPendingPayments - collection modified during iteration
Priority: Critical
Components: Payments
```

### Example 3: Batch Bug Reporting

**Input**:
```
Claude, analyze these 3 exceptions and create JIRA issues:

1. NullReferenceException in UserService.GetProfile at line 23
2. DivideByZeroException in Calculator.Divide at line 12
3. IndexOutOfRangeException in DataProcessor.ProcessRow at line 78

Project: PLATFORM
```

**Output**:
```
✓ Created 3 JIRA issues:
  - PLATFORM-101: NullReferenceException in UserService.GetProfile
  - PLATFORM-102: DivideByZeroException in Calculator.Divide
  - PLATFORM-103: IndexOutOfRangeException in DataProcessor.ProcessRow

✓ Saved 3 local reports to bugs/
```

---

## Configuration

### Required Settings

**JIRA Project Key**: The skill will prompt you for the JIRA project key if not provided in your request.

Example: `ECOM`, `PAY`, `PLATFORM`

### Optional Settings

**Component Mapping**: The skill automatically maps C# namespaces to JIRA components:
- `MyApp.Services.Payment` → Component: `Payment`
- `MyApp.Controllers.Order` → Component: `Order`

**Priority Assignment**: Auto-assigned based on exception type:
- **Critical**: NullReferenceException, OutOfMemoryException, StackOverflowException, SqlException
- **High**: InvalidOperationException, ArgumentException, UnauthorizedAccessException
- **Medium**: FileNotFoundException, TimeoutException
- **Low**: Minor exceptions

**Labels**: All issues are labeled with `csharp`, `bug`, `automated`

---

## File Structure

```
csharp-bug-documentation/
├── SKILL.md                    # Claude's instructions for using the skill
├── README.md                   # This file (user documentation)
├── bug_analyzer.py             # C# bug analysis logic
├── jira_reporter.py            # Atlassian MCP integration helpers
├── report_generator.py         # Markdown report generation
├── requirements.txt            # Python dependencies (none required!)
└── examples/
    ├── example-jira-issue.json # Sample JIRA issue payload
    └── example-report.md       # Sample Markdown report
```

---

## Advanced Usage

### Check for Duplicate Bugs

```
Claude, check if this bug exists in JIRA before filing:

NullReferenceException in OrderProcessor.ProcessOrder

Project: ECOM
```

### Update Existing Issue

```
Claude, update JIRA issue ECOM-1234 with this analysis:

Found root cause: Missing null check on line 45.
Suggested fix: Add `if (order?.Items != null)` check.
```

### Custom Priority

```
Claude, document this bug as Critical priority:

OutOfMemoryException in DataProcessor.LoadLargeFile

Project: DATA
```

### Add to Specific Component

```
Claude, file this bug in the Authentication component:

UnauthorizedAccessException in AuthService.ValidateToken

Project: AUTH
```

---

## Troubleshooting

### Error: "Atlassian MCP tools not available"

**Solution**:
1. Install Atlassian MCP server: https://github.com/modelcontextprotocol/servers/tree/main/src/atlassian
2. Configure in Claude Code settings
3. Restart Claude Code
4. Verify with: "Claude, do you have access to mcp__atlassian__jira_create_issue?"

### Error: "Invalid project key"

**Solution**:
1. Check that JIRA project exists: `https://your-domain.atlassian.net/projects`
2. Verify you have permission to create issues in the project
3. Use uppercase project key (e.g., `ECOM` not `ecom`)

### Error: "Permission denied creating bugs/ directory"

**Solution**:
1. Create directory manually: `mkdir bugs`
2. Check file system permissions: `chmod 755 bugs`
3. Or specify different output path when prompted

### Bug report missing details

**Solution**:
- Provide complete stacktrace when available
- Include relevant code context (not just the crashing line)
- Mention framework/library versions if relevant
- Describe expected behavior clearly

---

## Tips for Best Results

**Provide Complete Information**:
- Include full stacktraces when available
- Show relevant code context (not just error line)
- Mention C# version, framework (.NET 6, .NET Framework 4.8, etc.)
- Describe what you expected to happen

**Use Clear Language**:
- "Document this bug in JIRA"
- "Create a JIRA issue for this exception"
- "File a bug report for [description]"

**Specify Project Key**:
- Always include `Project: [KEY]` in your request
- Or the skill will prompt you for it

**Common Use Cases**:
- Document production bugs from logs
- Create issues from code reviews
- Track recurring exceptions
- Onboard new team members with bug history
- Build bug knowledge base

---

## Python Support Files

The skill includes Python modules that Claude uses to analyze bugs and format reports:

### `bug_analyzer.py`
- Parses C# stacktraces
- Identifies exception types and locations
- Determines severity levels
- Analyzes root causes
- Generates reproduction steps
- Suggests fixes

### `jira_reporter.py`
- Formats bug data for JIRA issues
- Uses JIRA wiki markup (not Markdown)
- Creates issue payloads for Atlassian MCP
- Handles priority mapping
- Formats code blocks and stacktraces

### `report_generator.py`
- Generates Microsoft-style Markdown reports
- Creates sanitized filenames
- Manages `bugs/` output directory
- Links to JIRA issues
- Formats code snippets

---

## Requirements

**Required**:
- Claude Code with Atlassian MCP server configured
- Python 3.7+ (already included with Claude Code)
- JIRA project with issue creation permissions

**Optional**:
- None! The skill uses only Python standard library

---

## Version

**1.0.0** - Initial release

**Features**:
- Atlassian MCP integration for JIRA
- C# exception analysis
- Microsoft-style bug documentation
- Local Markdown report generation
- Auto-priority assignment
- Component auto-detection
- Suggested fixes
- Impact assessment

---

## License

MIT License - Free to use and modify

---

## Support

**Issues or Questions?**
- Check the [SKILL.md](SKILL.md) file for Claude's detailed instructions
- Review [examples/](examples/) for sample outputs
- Open an issue in the Claude Code Skills Factory repo

---

**Generated by**: Claude Code Skills Factory
**Category**: SaaS/Software > Bug Documentation > C# > JIRA Integration
**MCP**: Atlassian MCP (JIRA)
**Output**: JIRA issues + Markdown reports

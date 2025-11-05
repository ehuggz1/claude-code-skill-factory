# Atlassian MCP Server Setup Guide

This guide will help you connect Claude Code to your RightRez JIRA instance using the official Atlassian MCP Server.

---

## What's Been Configured

✅ **MCP Server Configuration Added**: `.mcp.json` file has been created with the Atlassian MCP server configuration.

---

## Authentication Setup

### Step 1: Restart Claude Code

After creating the `.mcp.json` file, you need to restart Claude Code to load the new MCP server.

```bash
# Exit Claude Code and restart it
```

### Step 2: Approve the MCP Server

When you restart Claude Code, you'll be prompted to approve the Atlassian MCP server. Click **"Approve"** or **"Allow"**.

You can also manually approve it by updating `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(rm:*)",
      "Bash(python -m zipfile:*)"
    ],
    "deny": [],
    "ask": []
  },
  "enableAllProjectMcpServers": true
}
```

Or approve it selectively:

```json
{
  "permissions": {
    "allow": [
      "Bash(rm:*)",
      "Bash(python -m zipfile:*)"
    ],
    "deny": [],
    "ask": []
  },
  "enabledMcpjsonServers": ["atlassian"]
}
```

### Step 3: Authenticate with RightRez JIRA

When you first use the Atlassian MCP server, it will automatically trigger an OAuth 2.0 authentication flow:

1. **A browser window will open** pointing to the Atlassian authentication page
2. **Log in with your RightRez credentials**:
   - Use your RightRez Atlassian email
   - Enter your password or use SSO if configured
3. **Authorize the application**:
   - Review the requested permissions
   - Click **"Approve"** or **"Allow access"**
4. **Return to Claude Code**:
   - The browser may show a success message
   - Close the browser tab
   - Claude Code will now have access to your JIRA instance

---

## What You Can Do Now

Once authenticated, you can use the JIRA skills in this repository:

### 1. **C# Bug Documentation Skill**
```
Claude, document this C# bug in JIRA:

[code snippet or error]

Project: [RightRez JIRA Project Key]
```

### 2. **JIRA to Microsoft Bug Migrator**
```
Claude, export JIRA issue PROJ-123 to GitHub bug report format.
Save it to migrated-bugs/
```

### 3. **Direct JIRA Queries**
```
Claude, show me all open bugs in project PROJ assigned to me.
```

```
Claude, create a JIRA issue in project PROJ:
Title: New feature request
Description: Add user authentication
Type: Story
```

---

## Verifying Your Setup

To confirm the Atlassian MCP server is working:

1. **Check Available Tools**:
```
Claude, do you have access to Atlassian MCP tools?
```

2. **List Your JIRA Projects**:
```
Claude, what JIRA projects do I have access to?
```

3. **Search for Issues**:
```
Claude, find all issues in JIRA project PROJ updated in the last 7 days.
```

---

## Configuration Details

### MCP Server Configuration (`.mcp.json`)

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"]
    }
  }
}
```

**What this does**:
- Uses `npx` to run `mcp-remote` (installed automatically on first use)
- Connects to Atlassian's remote MCP server at `https://mcp.atlassian.com/v1/sse`
- Enables secure OAuth 2.0 authentication
- Respects your existing JIRA permissions

---

## Security & Permissions

### Data Access
- **Secure OAuth 2.0**: All authentication uses OAuth 2.0
- **Encrypted Traffic**: All data is encrypted via HTTPS (TLS 1.2+)
- **Permission-Based**: You only see JIRA data you already have access to
- **Session-Based Tokens**: OAuth tokens are scoped and session-based

### What the MCP Server Can Access
- ✅ JIRA issues you have permission to view
- ✅ JIRA projects you're a member of
- ✅ Confluence pages you can access (if enabled)
- ❌ Nothing outside your existing permissions

### Revoking Access

If you need to revoke access later:

1. **In Your Atlassian Account**:
   - Go to: https://id.atlassian.com/manage-profile/security/connected-apps
   - Find "MCP Remote Server"
   - Click "Revoke access"

2. **In Claude Code**:
   - Remove or disable the MCP server in `.mcp.json`
   - Restart Claude Code

---

## Troubleshooting

### Problem: Browser doesn't open for authentication

**Solution**:
```bash
# Manually run the authentication command:
npx -y mcp-remote https://mcp.atlassian.com/v1/sse
```

This will open the browser and start the OAuth flow.

---

### Problem: "MCP server not found" error

**Solution**:
1. Verify `.mcp.json` exists in the project root
2. Restart Claude Code
3. Check that you approved the MCP server when prompted

---

### Problem: "Authentication failed" or "Token expired"

**Solution**:
1. Revoke access in Atlassian (see above)
2. Restart Claude Code
3. Re-authenticate when prompted

---

### Problem: "Permission denied" when accessing JIRA

**Solution**:
- Verify you have access to the JIRA project in RightRez
- Check your JIRA permissions in the web UI
- Ensure you're logged in with the correct account

---

### Problem: Rate limit errors

**Solution**:
The Atlassian MCP server has usage limits:
- **Standard Plan**: Moderate usage thresholds
- **Premium/Enterprise**: 1,000 requests/hour + per-user limits

If you hit rate limits:
- Wait for the rate limit window to reset (usually 1 hour)
- Reduce the frequency of requests
- Contact your RightRez admin about upgrading to Premium/Enterprise

---

## Additional Resources

- **Official Atlassian MCP Documentation**: https://www.atlassian.com/blog/announcements/remote-mcp-server
- **Setting up Claude.ai**: https://support.atlassian.com/rovo/docs/setting-up-claude-ai/
- **Authentication & OAuth**: https://support.atlassian.com/rovo/docs/authentication-and-authorization/
- **Troubleshooting Guide**: https://support.atlassian.com/rovo/docs/troubleshooting-and-verifying-your-setup/

---

## Quick Reference Card

### RightRez JIRA Project Keys
(Update these with your actual project keys)

- **Main Project**: `PROJ` (replace with actual key)
- **Bug Tracking**: `BUG` (replace with actual key)
- **Feature Requests**: `FEAT` (replace with actual key)

### Common Commands

```bash
# Create a bug in JIRA
Claude, create a bug in JIRA project PROJ:
Title: [Bug title]
Description: [Bug description]
Priority: High

# Search for issues
Claude, find all critical bugs in PROJ assigned to me.

# Get issue details
Claude, show me the details of JIRA issue PROJ-123.

# Update an issue
Claude, update JIRA issue PROJ-123:
Add comment: "Fixed in PR #456"
Status: In Progress
```

---

**Setup Date**: 2025-11-04
**Status**: ✅ MCP Server Configured (Authentication Required)
**Next Step**: Restart Claude Code and authenticate with RightRez credentials

# Installation Guide: RREZ PR Manager

## Installation

### Claude Code (CLI)

**Project-level**:
```bash
mkdir -p .claude/skills
unzip rrez-pr-mgr.zip -d .claude/skills/
```

**User-level**:
```bash
mkdir -p ~/.claude/skills
unzip rrez-pr-mgr.zip -d ~/.claude/skills/
```

### Claude Desktop

1. Open Claude Desktop
2. Settings → Skills → Import Skill
3. Select `rrez-pr-mgr.zip`
4. Click Import

### Claude Web

1. Go to https://claude.ai
2. Profile → Settings → Skills
3. Upload `rrez-pr-mgr.zip`
4. Enable the skill

---

## Prerequisites

**Required**:
- Azure DevOps MCP server
- Azure DevOps PAT (Personal Access Token)
- Python 3.7+ (included with Claude)

**Check MCP**:
```
Claude, do you have access to Azure DevOps MCP tools?
```

---

## Testing

```
Claude, check Azure DevOps connection.

Organization: contoso
Project: MyProject
```

---

## Troubleshooting

### MCP Not Available
- Install Azure DevOps MCP server
- Configure PAT in MCP settings
- Restart Claude

### Permission Errors
- Verify PAT has required scopes
- Check project access permissions
- Confirm organization name is correct

---

**Skill Version**: 1.0.0
**Platform**: Claude Code, Desktop, Web
**MCP**: Azure DevOps MCP

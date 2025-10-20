# Windsurf Configuration Directory

This directory contains configuration files for Windsurf IDE and MCP (Model Context Protocol) servers.

## Files

### `mcp.json`
MCP server configuration for Playwright browser automation.

**Purpose**: Enables the AI assistant to browse documentation websites in real-time.

**Configured Services**:
- Playwright MCP server for browser automation

**Access Policy**:
- Unrestricted web access (can browse any public website)
- Optimized for documentation sites but not limited to them

**Primary Documentation Sources**:
- OpenAI API Documentation (platform.openai.com)
- Supabase Documentation (supabase.com)
- CrewAI Documentation (docs.crewai.com)
- React Documentation (react.dev)
- TypeScript Documentation (typescriptlang.org)
- Plus any other website as needed!

## Usage

After adding this configuration:
1. **Restart Windsurf** to load the MCP server
2. Test with: "Navigate to https://docs.crewai.com"
3. Use queries like: "Check OpenAI docs for GPT-4o pricing"

## Troubleshooting

If Playwright MCP doesn't work:
1. Install Playwright browsers: `npx playwright install chromium`
2. Check Windsurf output panel for MCP logs
3. Verify internet connectivity
4. Try basic config first (remove optional args)

## More Info

See project root files:
- `PLAYWRIGHT_MCP_QUICK_START.md` - Quick setup guide
- `MCP_SETUP_GUIDE.md` - Comprehensive documentation
- `MCP_CONTEXT.md` - Manual tracking fallback

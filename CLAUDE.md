# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository (BarTC YT) is an AI agent configuration project focused on product development workflows. It contains specialized agent definitions rather than traditional software code.

## Project Structure

```
BarTC YT/
└── agents/
    └── prd-generator.md    # Product Requirements Document generator agent
```

## Working with AI Agents

### PRD Generator Agent
Located in `agents/prd-generator.md`, this agent creates comprehensive Product Requirements Documents following a structured template:
- Problem Definition and User Impact
- Solution Proposal and Implementation Details
- Business Value and Success Metrics
- Research-based approach using WebSearch and WebFetch tools

## Development Notes

Since this is an agent configuration repository:
- No build, test, or lint commands are needed
- Focus on maintaining and improving agent definitions
- Agent markdown files should follow the existing structure and format
- When modifying agents, ensure tool requirements and prompts remain clear and actionable

## MCP Server Configuration

**Preferred MCP Servers to use proactively:**
- **Serena MCP**: Use for semantic code analysis, intelligent file operations, and LSP-powered code understanding
- **Context 7 MCP**: Use for enhanced context management and workflow optimization

These servers provide superior performance and capabilities compared to standard file system operations.

## Key Considerations

1. **Agent Quality**: Ensure agent prompts are clear, comprehensive, and produce consistent results
2. **Template Structure**: Maintain the structured format in agent outputs for consistency
3. **Tool Usage**: Agents should specify required tools clearly (WebSearch, WebFetch, Read, Write, etc.)
4. **Documentation**: Keep agent descriptions and methodologies up-to-date
5. **MCP Integration**: Leverage Serena MCP and Context 7 MCP for enhanced development capabilities

## Memory Notes

- Use context 7 mcp whenever checking doc
- whenever I say something like, search x doc, use context7 mcp
- OpenAI API key is configured in tts-addon/fast_tts.py: [REDACTED - stored in environment]

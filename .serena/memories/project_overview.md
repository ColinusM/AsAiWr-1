# Project Overview - BarTC YT

## Purpose
This repository (BarTC YT) is an AI agent configuration project focused on product development workflows. It contains specialized agent definitions rather than traditional software code.

## Tech Stack
- **Language**: TypeScript (project configured as TypeScript, though contains primarily Markdown agent definitions)
- **AI Agents**: Claude Code agent configurations stored in `.claude/agents/` directory
- **Markdown**: Agent definitions written in structured Markdown with YAML frontmatter
- **MCP Servers**: Serena MCP and Context7 MCP for enhanced functionality

## Project Structure
```
BarTC YT/
├── .claude/
│   ├── agents/
│   │   ├── prd-generator.md     # Product Requirements Document generator agent
│   │   └── example-agent.md     # Sample agent configuration
│   └── settings.json            # Claude Code settings
├── .serena/
│   ├── memories/               # Project memories for Serena MCP
│   └── project.yml            # Serena project configuration
├── CLAUDE.md                  # Project instructions for Claude Code
├── PRD-BarTC.md               # Example PRD output
├── .env.example               # Environment variable template
└── Gmail_Latest_Email.kmmacros # Keyboard Maestro macro file

## Key Components

### Agent Definitions
- Located in `.claude/agents/` directory
- Written in Markdown with YAML frontmatter configuration
- Include tool requirements, model specifications, and detailed instructions
- Follow structured template for consistency

### MCP Integration
- **Preferred MCP Servers**: Serena MCP and Context7 MCP
- Serena MCP: Semantic code analysis, intelligent file operations, LSP-powered understanding
- Context7 MCP: Enhanced context management and workflow optimization

## Development Focus
This is NOT a traditional software project but an AI agent configuration repository for product development workflows.
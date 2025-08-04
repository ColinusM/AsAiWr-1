# Code Style and Conventions - BarTC YT

## Agent Definition Structure

### YAML Frontmatter Format
```yaml
---
name: agent-name
description: Brief description of agent purpose
model: sonnet
color: Blue
type: code-assistant (optional)
tools: (optional)
  - Bash
  - Read
  - Write
---
```

### Markdown Structure
1. **# Purpose** - Clear agent role definition
2. **## Instructions** - Systematic step-by-step process
3. **## Template Structure** - Any output templates (if applicable)
4. **## Research Questions** - Discovery and validation questions
5. **## Research Methodology** - Approach and best practices
6. **## MCP Tool Usage** - Leverage enhanced capabilities
7. **## Report / Response** - Output format requirements
8. **## File Output Requirements** - Specific file creation needs

## Naming Conventions

### Files and Directories
- Agent files: `kebab-case.md` (e.g., `prd-generator.md`, `tts-reader.md`)
- Output files: `PascalCase-kebab-case.md` (e.g., `PRD-Product-Name.md`)
- Memory files: `snake_case.md` (e.g., `project_overview.md`)
- Directories: `kebab-case` or standard names (`.claude`, `.serena`)

### Agent Names
- Use `kebab-case` in YAML frontmatter
- Descriptive but concise (e.g., `prd-generator`, `tts-reader`)
- Reflect primary function/purpose

## Content Guidelines

### Agent Instructions
- Use numbered steps for systematic processes
- Be specific about tool usage and MCP server preferences
- Include error handling and validation steps
- Provide clear success criteria and output requirements

### Documentation Style
- Use clear, professional language
- Include code examples where relevant
- Structure information hierarchically
- Maintain consistency across all agent definitions

### Tool Integration
- Prefer Serena MCP for semantic code analysis
- Use Context7 MCP for documentation and library research
- Specify required tools in YAML frontmatter when known
- Provide fallback approaches when MCP servers unavailable

## Quality Standards

### Agent Definition Requirements
1. Clear purpose and role definition
2. Systematic instruction steps
3. Proper tool usage guidelines
4. Output format specifications
5. File creation requirements (when applicable)
6. Quality assurance steps

### Validation Checklist
- [ ] YAML frontmatter properly formatted
- [ ] Instructions are clear and actionable
- [ ] Tool requirements specified
- [ ] Output format defined
- [ ] File naming conventions followed
- [ ] MCP server usage optimized

## Best Practices

### Agent Development
- Start with existing agent templates
- Test agent functionality before committing
- Document any dependencies or prerequisites
- Include comprehensive instruction steps
- Specify exact output requirements

### File Management
- Keep agent files focused and single-purpose
- Use consistent formatting and structure
- Include comprehensive documentation
- Follow established naming patterns
- Maintain clean directory organization
# Suggested Commands - BarTC YT

## Development Commands

Since this is an AI agent configuration project (not traditional software), there are NO standard build, test, or lint commands.

### File Operations
- `ls -la` - List all files and directories (Darwin/macOS)
- `find . -name "*.md" -type f` - Find all Markdown files
- `grep -r "search_term" .` - Search for text in files
- `cat filename.md` - Display file contents

### Git Operations
- `git status` - Check repository status
- `git add .` - Stage all changes
- `git commit -m "message"` - Commit changes
- `git push` - Push to remote repository

### Directory Navigation
- `cd .claude/agents/` - Navigate to agents directory
- `pwd` - Show current directory
- `tree` - Show directory structure (if installed)

### Agent Development Workflow
1. Create new agent files in `.claude/agents/` directory
2. Follow the YAML frontmatter + Markdown structure
3. Test agent functionality through Claude Code interface
4. Document changes in commit messages

### Useful macOS/Darwin Commands
- `open .` - Open current directory in Finder
- `pbcopy < filename.md` - Copy file contents to clipboard
- `pbpaste > filename.md` - Paste clipboard to file
- `which command` - Find location of command
- `brew install package` - Install packages via Homebrew (if available)

## File Naming Conventions
- Agent files: `kebab-case.md` (e.g., `prd-generator.md`)
- PRD outputs: `PRD-[product-name].md` (e.g., `PRD-BarTC.md`)
- Memory files: `snake_case.md` or `kebab-case.md`

## Important Notes
- No compilation, testing, or linting required
- Focus on maintaining agent definitions and documentation
- Use MCP servers (Serena, Context7) for enhanced functionality
- Always validate agent configurations before committing
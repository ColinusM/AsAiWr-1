# Task Completion Workflow - BarTC YT

## What to Do When Task is Completed

Since this is an AI agent configuration project, there are NO traditional build, test, or lint commands to run.

### Standard Completion Steps

1. **Validate Agent Configuration**
   - Ensure YAML frontmatter is properly formatted
   - Check that all required fields are present
   - Verify tool requirements are correctly specified

2. **Test Agent Functionality**
   - Test the agent through Claude Code interface
   - Verify all instruction steps work as expected
   - Confirm output format matches requirements

3. **File Organization Check**
   - Ensure proper file naming conventions are followed
   - Verify files are in correct directories (`.claude/agents/`)
   - Check that any output files follow naming standards

4. **Documentation Review**
   - Confirm instructions are clear and actionable
   - Verify all sections are complete and well-structured
   - Check that MCP server usage is properly documented

5. **Version Control**
   - Stage changes: `git add .`
   - Commit with descriptive message: `git commit -m "Add/Update [agent-name] agent"`
   - Push to remote: `git push`

### Agent-Specific Completion Tasks

#### For PRD Generator Agent
- Verify PRD template structure is complete
- Test research methodology steps
- Confirm file output requirements work correctly

#### For New TTS Reader Agent
- Test text-to-speech functionality
- Verify file reading capabilities
- Confirm audio output generation works

### Quality Assurance Checklist

- [ ] Agent follows established naming conventions
- [ ] YAML frontmatter is valid and complete
- [ ] Instructions are systematic and clear
- [ ] Tool requirements are properly specified
- [ ] Output format is well-defined
- [ ] File creation requirements are functional
- [ ] MCP server integration is optimized
- [ ] Agent has been tested and validated

### No Additional Commands Required

Unlike traditional software projects, there are NO:
- Build commands to run
- Test suites to execute
- Linting tools to apply
- Formatting tools to run
- Compilation steps to perform

### Final Verification

1. Agent file saved in `.claude/agents/` directory
2. Proper YAML frontmatter and Markdown structure
3. All instruction steps are actionable
4. File naming follows project conventions
5. Changes committed to version control

The task is complete when the agent configuration is properly saved, tested, and committed to the repository.
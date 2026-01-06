---
name: skill-creator
description: Creates new Claude Code skills with proper structure and best practices. Use when the user wants to create a skill, make a new skill, build a custom skill, or asks "how do I make a skill".
---

# Skill Creator

A meta-skill for creating well-structured Claude Code skills.

## Mode Selection

Ask the user which mode they prefer:

1. **Guided Mode**: Walk through a questionnaire to gather all details
2. **Quick Mode**: Infer skill structure from a natural language description

If the user doesn't specify, default to guided mode for first-time skill creators.

---

## Guided Mode Workflow

Ask these questions in order:

### 1. Name
"What should this skill be called? (lowercase, hyphens allowed, e.g., `code-reviewer`)"

### 2. Purpose
"What does this skill do? Describe its main function in 1-2 sentences."

### 3. Trigger Phrases
"What phrases should trigger this skill? List 3-5 examples of what users might say."

### 4. Tools Needed
"Does this skill need specific tools? (e.g., Read, Grep, Bash). Leave blank for no restrictions."

### 5. Template Base
"Would you like to start from a template?"
- Code review
- Refactoring assistant
- Code explainer
- Debugging helper
- Commit message generator
- PR review
- Documentation writer
- Test generator
- Start from scratch

### 6. Best Practices Review
After gathering all inputs, run the **Best Practices Review** (see section below) to suggest enhancements before generating.

---

## Quick Mode Workflow

When the user provides a description like "I want a skill that reviews my SQL queries for performance issues":

1. Extract the core purpose
2. Generate a descriptive name (e.g., `sql-performance-reviewer`)
3. Infer trigger phrases from the description
4. Select appropriate tools based on the task
5. Choose the closest template as a starting point
6. Present the inferred structure for user confirmation
7. **Run Best Practices Review** (see section below) - suggest enhancements before generating

---

## Best Practices (Include in Generated Skills)

### Writing Effective Descriptions
- Include trigger keywords users would naturally say
- Be specific about when the skill applies
- Keep under 1024 characters
- Example: Instead of "Helps with code" write "Reviews code for bugs, security issues, and style violations. Use when reviewing PRs, checking code quality, or asking 'is this code safe?'"

### Writing Clear Instructions
- Use imperative voice ("Run", "Check", "Generate")
- Break complex tasks into numbered steps
- Include concrete examples
- Specify output format expectations

### Scope Discipline
- One primary task per skill
- If a skill does multiple things, consider splitting it
- Keep SKILL.md under 500 lines

---

## Template Library

### Code-Focused Templates

#### code-review
```yaml
---
name: code-review
description: Reviews code for bugs, security issues, and best practices. Use when reviewing code, checking PRs, or asking "is this code okay?"
---

# Code Review

## Instructions
1. Read the code file or diff provided
2. Check for:
   - Bugs and logic errors
   - Security vulnerabilities
   - Performance issues
   - Code style violations
3. Provide specific, actionable feedback
4. Suggest improvements with code examples

## Example Triggers
- "Review this code"
- "Check my PR"
- "Is this implementation correct?"
```

#### refactoring-assistant
```yaml
---
name: refactoring-assistant
description: Helps refactor code for better readability and maintainability. Use when cleaning up code, reducing duplication, or improving structure.
---

# Refactoring Assistant

## Instructions
1. Analyze the code structure
2. Identify refactoring opportunities:
   - Extract methods/functions
   - Remove duplication
   - Simplify conditionals
   - Improve naming
3. Explain the "why" behind each suggestion
4. Show before/after comparisons

## Example Triggers
- "Help me refactor this"
- "This code is messy, clean it up"
- "How can I simplify this function?"
```

#### code-explainer
```yaml
---
name: code-explainer
description: Explains code with analogies and visual diagrams. Use when asking "how does this work?" or "explain this code".
---

# Code Explainer

## Instructions
1. Start with a real-world analogy
2. Draw an ASCII diagram showing flow or structure
3. Walk through the code step-by-step
4. Highlight common gotchas or misconceptions
5. Suggest related concepts to explore

## Example Triggers
- "Explain this code"
- "How does this work?"
- "What does this function do?"
```

#### debugging-helper
```yaml
---
name: debugging-helper
description: Helps debug issues by analyzing errors and suggesting fixes. Use when encountering errors, bugs, or unexpected behavior.
---

# Debugging Helper

## Instructions
1. Analyze the error message or unexpected behavior
2. Identify potential root causes
3. Suggest debugging steps:
   - Add logging/breakpoints
   - Check inputs/outputs
   - Verify assumptions
4. Propose fixes with explanations
5. Suggest preventive measures

## Example Triggers
- "Help me debug this"
- "Why is this failing?"
- "I'm getting an error"
```

### Workflow-Focused Templates

#### commit-message-generator
```yaml
---
name: commit-message-generator
description: Generates clear, conventional commit messages. Use when committing changes or asking for commit message help.
---

# Commit Message Generator

## Instructions
1. Run `git diff --staged` to see changes
2. Analyze what changed and why
3. Generate a commit message:
   - Subject line under 50 characters
   - Use imperative mood ("Add", "Fix", "Update")
   - Include scope if applicable
   - Add body for complex changes
4. Follow conventional commits format if project uses it

## Example Triggers
- "Write a commit message"
- "What should I call this commit?"
- "Generate commit message for these changes"
```

#### pr-review
```yaml
---
name: pr-review
description: Reviews pull requests for quality and completeness. Use when reviewing PRs, checking diffs, or preparing PR feedback.
---

# PR Review

## Instructions
1. Understand the PR's purpose from title/description
2. Review each changed file:
   - Logic correctness
   - Test coverage
   - Documentation updates
   - Breaking changes
3. Check for:
   - Merge conflicts
   - CI/CD status
   - Required approvals
4. Provide constructive feedback with specific line references

## Example Triggers
- "Review this PR"
- "Check PR #123"
- "Is this PR ready to merge?"
```

#### documentation-writer
```yaml
---
name: documentation-writer
description: Writes clear documentation for code and APIs. Use when documenting functions, APIs, or writing README content.
---

# Documentation Writer

## Instructions
1. Understand the code/API being documented
2. Write documentation including:
   - Purpose and overview
   - Parameters/arguments
   - Return values
   - Usage examples
   - Edge cases and errors
3. Match the project's existing documentation style
4. Keep it concise but complete

## Example Triggers
- "Document this function"
- "Write API docs"
- "Add documentation for this module"
```

#### test-generator
```yaml
---
name: test-generator
description: Generates test cases for code. Use when writing tests, improving coverage, or asking "how should I test this?"
---

# Test Generator

## Instructions
1. Analyze the code to be tested
2. Identify test scenarios:
   - Happy path
   - Edge cases
   - Error conditions
   - Boundary values
3. Generate tests using the project's testing framework
4. Include setup/teardown if needed
5. Add descriptive test names

## Example Triggers
- "Write tests for this"
- "How should I test this function?"
- "Generate test cases"
```

---

## Best Practices Review (Before Creating)

After gathering all requirements and before generating the skill files, always ask:

"Based on best practices for skills like this, here are some features that could strengthen it:"

Then suggest relevant additions based on the skill type. Use WebSearch if needed to find current best practices for the domain. Common enhancements to consider:

**For workflow/process skills:**
- Iteration/feedback loops
- Progress checkpoints
- Output format options
- Error handling guidance

**For content generation skills:**
- Style guide / consistency rules
- Length/depth configuration
- Metadata generation (titles, descriptions, tags)
- Template variations

**For code-focused skills:**
- Integration with existing project patterns
- Linting/formatting preferences
- Test generation alongside main output
- Documentation generation

**For analysis skills:**
- Severity/priority classification
- Export formats
- Comparison modes
- Historical tracking suggestions

Present 3-5 relevant suggestions as a multi-select question using AskUserQuestion. Let the user pick which to include before generating.

---

## Generation Instructions

When creating a new skill:

1. **Create the directory**
   ```bash
   mkdir -p ~/.claude/skills/{skill-name}
   ```

2. **Write SKILL.md** with this structure:
   ```markdown
   ---
   name: {skill-name}
   description: {description with trigger keywords}
   ---

   # {Skill Title}

   ## Instructions
   {Step-by-step instructions}

   ## Example Triggers
   - "{trigger phrase 1}"
   - "{trigger phrase 2}"
   - "{trigger phrase 3}"
   ```

3. **Inform the user** to restart Claude Code to load the skill

---

## Validation

After creating a skill, validate it works:

1. Tell the user: "Restart Claude Code, then ask 'What skills are available?'"
2. The new skill should appear in the list
3. Test with one of the example trigger phrases
4. If the skill doesn't appear:
   - Check the file path is correct
   - Verify YAML frontmatter syntax (no tabs, proper indentation)
   - Ensure `name` field matches directory name

---

## Example Usage

**Guided mode:**
> "Help me create a skill"
> "I want to make a new skill"
> "Create a skill for me"

**Quick mode:**
> "Create a skill that formats my Python code according to PEP8"
> "Make a skill for generating API documentation from docstrings"
> "I need a skill that checks my code for security vulnerabilities"

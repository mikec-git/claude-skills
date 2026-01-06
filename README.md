# Claude Skills

A collection of custom skills for [Claude Code](https://claude.com/claude-code).

## Installation

Clone this repository and symlink it to your Claude Code skills directory:

```bash
git clone https://github.com/mikec-git/claude-skills.git
ln -s /path/to/claude-skills ~/.claude/skills
```

## Available Skills

### skill-creator

A meta-skill for creating well-structured Claude Code skills. Supports guided and quick modes.

**Triggers:** "create a skill", "make a new skill", "how do I make a skill"

### blog-writer

A conversational blog writing assistant that gathers context before drafting, produces outlines for approval, and writes section by section.

**Triggers:** "help me write about...", "review my blog", "make this better", "revise my post"

### smart-commit

Intelligently analyzes Git changes, groups them by separation of concerns, commits in logical order, and pushes automatically.

**Triggers:** "commit", "push", "commit my changes", "smart commit", "/smart-commit"

## Creating New Skills

Use the `skill-creator` skill to create new skills:

```
/skill-creator
```

## License

MIT

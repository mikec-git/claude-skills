# Skill Quality Checklist

Validate skills before sharing. Copy and check off each item.

## Contents

- [Quick Checklist](#quick-checklist)
- [Extended Checklist](#extended-checklist)
- [Syntax Validation](#syntax-validation)
- [Conciseness Test](#conciseness-test)
- [Testing by Model](#testing-by-model)
- [Quick Fixes](#quick-fixes)
- [Validation Flow](#validation-flow)

---

## Quick Checklist

````
Skill Validation:

Syntax (NEW)
- [ ] Valid YAML frontmatter (--- delimiters)
- [ ] name and description fields present
- [ ] Heading hierarchy (no skipped levels)
- [ ] Code blocks properly closed (``` pairs)
- [ ] Links have valid syntax [text](url)
- [ ] Lists consistently formatted
- [ ] Tables have matching column counts

Metadata
- [ ] name: lowercase, hyphens only, max 64 chars
- [ ] name: no reserved words (anthropic, claude)
- [ ] description: non-empty, max 1024 chars
- [ ] description: what it does + when to use it
- [ ] description: third person, specific trigger terms

Structure
- [ ] SKILL.md body under 500 lines
- [ ] Reference files one level deep only
- [ ] Files >100 lines have table of contents
- [ ] Forward slashes in all paths

Content
- [ ] No explanations of common knowledge
- [ ] Consistent terminology throughout
- [ ] Concrete examples included
- [ ] No time-sensitive information (or uses <details>)
- [ ] One default tool per task (with escape hatch)

Workflows
- [ ] Clear sequential steps
- [ ] Copyable checklist for complex tasks
- [ ] Feedback loops for quality-critical output
- [ ] Validation before destructive operations

Code (if applicable)
- [ ] Scripts handle errors explicitly
- [ ] No magic numbers (values documented)
- [ ] Dependencies listed with install commands
- [ ] Clear: execute script vs read as reference
````

---

## Extended Checklist

For thorough validation before production use.

```
Pre-Validation
- [ ] Requirements confirmed with user
- [ ] Scope clearly defined
- [ ] Success criteria documented

Syntax Deep Check (NEW)
- [ ] No skipped heading levels (## to #### without ###)
- [ ] All code blocks have language specifiers
- [ ] No unmatched emphasis markers (** or __)
- [ ] No unmatched inline code backticks
- [ ] Tables have separator row after header
- [ ] Links don't contain unencoded spaces
- [ ] Main heading (H1) present after frontmatter

Metadata Deep Check
- [ ] Description mentions all primary use cases
- [ ] Trigger words match user vocabulary
- [ ] No competing skills with overlapping triggers
- [ ] Description distinguishes from similar skills

Structure Deep Check
- [ ] Most common operations in SKILL.md
- [ ] Reference files contain truly optional content
- [ ] Navigation between files is clear
- [ ] No orphaned files (unreferenced)

Content Deep Check
- [ ] Every instruction has clear action
- [ ] Ambiguous terms defined or avoided
- [ ] Edge cases addressed or acknowledged
- [ ] Failure modes have recovery guidance

Robustness Check
- [ ] Works with varied phrasings of same request
- [ ] Handles missing optional context gracefully
- [ ] Provides useful partial results when stuck
- [ ] Clear about scope limitations

Cross-Model Compatibility
- [ ] Haiku: Sufficient explicit guidance
- [ ] Sonnet: Balanced instruction density
- [ ] Opus: Not over-prescriptive

Behavioral Patterns
- [ ] Constraints use positive framing ("do X" not "don't Y")
```

---

## Syntax Validation

Run the syntax validator to catch common Markdown errors before they cause issues.

### Running the Validator

```bash
# Validate a single file
python scripts/validate_syntax.py ./my-skill/SKILL.md

# Validate all markdown files in a directory
python scripts/validate_syntax.py ./my-skill/
```

### What It Checks

| Category        | Checks Performed                                     |
| --------------- | ---------------------------------------------------- |
| Frontmatter     | Opening/closing ---, name field, description field   |
| Headings        | Level hierarchy, space after #                       |
| Code Blocks     | Matched ``` delimiters, unclosed blocks              |
| Links           | Valid [text](url) syntax, empty text/url, URL spaces |
| Lists           | Space after marker, consistent indentation           |
| Tables          | Column count consistency across rows                 |
| Emphasis        | Matched \*\* and \_\_ markers                        |
| Inline Code     | Matched backticks                                    |
| Skill Structure | H1 after frontmatter, content order                  |

### Common Syntax Errors

| Error                      | Example                       | Fix                              |
| -------------------------- | ----------------------------- | -------------------------------- |
| Missing frontmatter closer | `---` at start, none at end   | Add closing `---`                |
| Skipped heading level      | `## Intro` then `#### Detail` | Use `### Detail` instead         |
| Unclosed code block        | ` ``` ` without closing       | Add closing ` ``` `              |
| Link with spaces in URL    | `[text](my file.md)`          | `[text](my%20file.md)` or rename |
| List without space         | `-item` instead of `- item`   | Add space after marker           |
| Unmatched bold             | `**bold text` without closing | Add closing `**`                 |

### Severity Levels

- **Error**: Must be fixed - will cause parsing issues
- **Warning**: Should be fixed - may cause display or compatibility issues

---

## Conciseness Test

For each paragraph ask:

1. Does Claude need this explanation?
2. Can I assume Claude already knows this?
3. Does this justify its token cost?

If any answer is "no," remove or condense.

**Token cost awareness:**

| Content Type        | Justification Needed      |
| ------------------- | ------------------------- |
| Domain terminology  | Yes - define once         |
| Standard libraries  | No - Claude knows these   |
| Common patterns     | No - Claude knows these   |
| Project conventions | Yes - specific to context |
| Edge case handling  | Yes - prevents errors     |
| Safety guardrails   | Yes - prevents harm       |

---

## Testing by Model

| Model  | Check                            |
| ------ | -------------------------------- |
| Haiku  | Does it provide enough guidance? |
| Sonnet | Is it clear and efficient?       |
| Opus   | Does it avoid over-explaining?   |

---

## Quick Fixes

| Issue                       | Fix                                                     |
| --------------------------- | ------------------------------------------------------- |
| Description too vague       | Add specific trigger keywords and use cases             |
| SKILL.md too long           | Move details to reference files                         |
| Claude ignores instructions | Make instructions more prominent, use stronger language |
| Claude over-reads files     | Improve file structure, add clear navigation            |
| Scripts fail silently       | Add explicit error handling with helpful messages       |
| Inconsistent behavior       | Reduce degrees of freedom for critical steps            |
| Fails on edge cases         | Add explicit handling or graceful fallbacks             |
| Works on Opus, fails Haiku  | Add more explicit guidance for critical steps           |
| Syntax validation fails     | Fix markdown issues reported by validate_syntax.py      |

---

## Validation Flow

```
Phase 1: Requirements Clear?
     |
     +---> No: Use AskUserQuestion tool
     |
     v
Phase 4: Static Validation Pass?
     |
     +---> No: Fix issues from scripts
     |
     v
Phase 5: Invocation Tests Pass?
     |
     +---> No: Update name/description
     |
     v
Ready for Use
```

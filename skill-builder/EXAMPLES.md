# Skill Examples

Complete examples demonstrating best practices at different complexity levels.

## Contents

- [Simple Skill: Commit Message Helper](#simple-skill-commit-message-helper)
- [Medium Skill: Code Review](#medium-skill-code-review)
- [Complex Skill: PDF Processing](#complex-skill-pdf-processing)
- [Anti-Pattern Examples](#anti-pattern-examples)

---

## Simple Skill: Commit Message Helper

Single-file skill using the examples pattern.

```markdown
---
name: commit-helper
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
---

# Commit Message Helper

Generate commit messages from staged changes.

## Format

type(scope): brief description

Detailed explanation if needed.

## Examples

**Input:** Added user authentication with JWT tokens
**Output:**
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware

**Input:** Fixed date display bug in reports
**Output:**
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation

**Input:** Updated deps and refactored error handling
**Output:**
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format
```

**Why this works:**

- Description includes triggers ("asks for help writing commit messages")
- Examples pattern teaches style more effectively than rules
- Under 50 lines - no reference files needed

---

## Medium Skill: Code Review

Skill with workflow and flexible guidance.

```markdown
---
name: code-review
description: Performs structured code reviews with actionable feedback. Use when asked to review code, check a PR, or analyze code quality.
---

# Code Review

Provide structured, actionable code reviews.

## Workflow

1. **Understand context**: What does this code do? What problem does it solve?
2. **Check correctness**: Are there bugs, edge cases, or logic errors?
3. **Evaluate design**: Is the structure clear? Are responsibilities well-separated?
4. **Assess maintainability**: Will this be easy to modify later?
5. **Review style**: Does it follow project conventions?

## Output Format

Structure feedback by severity:

### Critical

Issues that will cause bugs or security problems. Must fix.

### Important

Design issues or significant improvements. Should fix.

### Suggestions

Minor improvements or style preferences. Nice to have.

## Guidelines

- Be specific: reference line numbers and show corrected code
- Be constructive: explain why, not just what
- Prioritize: focus on what matters most
- Acknowledge good patterns you observe
```

**Why this works:**

- High degrees of freedom (code review is context-dependent)
- Clear workflow without being prescriptive
- Output template provides structure without rigidity

---

## Complex Skill: PDF Processing

Multi-file skill with scripts and progressive disclosure.

### Directory Structure

```
pdf-processing/
  SKILL.md
  FORMS.md
  scripts/
    analyze_form.py
    validate_fields.py
    fill_form.py
```

### SKILL.md

```markdown
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDFs or when the user mentions forms, document extraction, or PDF editing.
---

# PDF Processing

## Quick Start

Extract text with pdfplumber:

import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
text = pdf.pages[0].extract_text()

Install: pip install pdfplumber

## Form Filling

For form operations, see [FORMS.md](FORMS.md).

## Common Tasks

| Task           | Approach                    |
| -------------- | --------------------------- |
| Extract text   | pdfplumber (above)          |
| Extract tables | pdfplumber.extract_tables() |
| Merge PDFs     | pypdf PdfMerger             |
| Fill forms     | See FORMS.md workflow       |
```

### FORMS.md

```markdown
# Form Filling Guide

## Workflow

Copy and track progress:

- [ ] Step 1: Analyze form structure
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill form
- [ ] Step 5: Verify output

### Step 1: Analyze Form

Run: python scripts/analyze_form.py input.pdf

Output: fields.json with field names, types, and positions.

### Step 2: Create Field Mapping

Edit fields.json to add values for each field.

### Step 3: Validate Mapping

Run: python scripts/validate_fields.py fields.json

Fix any errors before continuing.

### Step 4: Fill Form

Run: python scripts/fill_form.py input.pdf fields.json output.pdf

### Step 5: Verify Output

Open output.pdf and confirm all fields are correctly filled.
If issues found, return to Step 2.
```

**Why this works:**

- Progressive disclosure: SKILL.md is quick reference, FORMS.md has details
- Explicit workflow with checklist
- Feedback loop (Step 5 returns to Step 2 on failure)
- Scripts referenced for execution, not reading
- One level of file references

---

## Anti-Pattern Examples

### Too Verbose

**Bad:**

```markdown
PDF (Portable Document Format) files are a common file format that
contains text, images, and other content. To extract text from a PDF,
you'll need to use a library. There are many libraries available...
```

**Good:**

```markdown
Extract text with pdfplumber:
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
text = pdf.pages[0].extract_text()
```

### Too Many Options

**Bad:**

```markdown
You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image...
```

**Good:**

```markdown
Use pdfplumber for text extraction.
For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Nested References

**Bad:**

```
SKILL.md -> advanced.md -> details.md -> actual info
```

**Good:**

```
SKILL.md -> advanced.md (contains actual info)
SKILL.md -> reference.md (contains actual info)
```

### Vague Description

**Bad:**

```yaml
description: Helps with documents
```

**Good:**

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDFs or when the user mentions forms, document extraction, or PDF editing.
```

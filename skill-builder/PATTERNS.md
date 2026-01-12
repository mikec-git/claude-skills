# Skill Patterns Reference

Detailed examples of common skill patterns. Load as needed.

## Contents

- [Degrees of Freedom](#degrees-of-freedom)
- [Positive Constraint Framing](#positive-constraint-framing)
- [Template Pattern](#template-pattern)
- [Examples Pattern](#examples-pattern)
- [Workflow Pattern](#workflow-pattern)
- [Feedback Loop Pattern](#feedback-loop-pattern)
- [Conditional Workflow Pattern](#conditional-workflow-pattern)
- [Progressive Disclosure Pattern](#progressive-disclosure-pattern)
- [Executable Scripts Pattern](#executable-scripts-pattern)
- [Command Language](#command-language)
- [Persuasion Principles](#persuasion-principles)

---

## Degrees of Freedom

Match specificity to task fragility.

### High Freedom (text-based)

Use when multiple approaches are valid:

```markdown
## Code review process

1. Analyze code structure and organization
2. Check for potential bugs or edge cases
3. Suggest readability improvements
4. Verify adherence to project conventions
```

### Medium Freedom (pseudocode/parameters)

Use when a preferred pattern exists:

````markdown
## Generate report

Use this template and customize as needed:

```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
```
````

### Low Freedom (specific scripts)

Use when operations are fragile:

````markdown
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
````

---

## Positive Constraint Framing

Negative instructions ("don't do X") force Claude to process the prohibited concept, increasing violation probability.

### Transform Negatives to Positives

| Negative (avoid)                      | Positive (use)                                   |
| ------------------------------------- | ------------------------------------------------ |
| Don't write code until you understand | Read and summarize the problem before writing    |
| Never skip validation                 | Always run validation first                      |
| Don't use emojis                      | Use only alphanumeric characters and punctuation |
| Avoid making assumptions              | Confirm understanding by restating requirements  |
| Don't modify production data          | Operate only on staging/test environments        |
| Never commit secrets                  | Commit only code and configuration               |

### Example Transformation

**Before (negative framing):**

```markdown
Do not proceed without user confirmation.
Never skip the backup step.
Don't use deprecated APIs.
```

**After (positive framing):**

```markdown
Wait for explicit user confirmation before proceeding.
Run backup before every destructive operation.
Use only APIs from the approved list: [X, Y, Z].
```

### When Negatives Are Unavoidable

Pair with a positive alternative:

```markdown
Do not hard-code credentials. Instead, read from environment variables.
```

---

## Template Pattern

### Strict Template

For exact format requirements:

````markdown
## Report structure

ALWAYS use this exact template:

```markdown
# [Analysis Title]

## Executive summary

[One-paragraph overview]

## Key findings

- Finding 1 with data
- Finding 2 with data

## Recommendations

1. Specific recommendation
2. Specific recommendation
```
````

### Flexible Template

For adaptable guidance:

````markdown
## Report structure

Sensible default format - adjust based on context:

```markdown
# [Analysis Title]

## Executive summary

[Overview]

## Key findings

[Adapt sections as needed]

## Recommendations

[Tailor to context]
```
````

---

## Examples Pattern

For quality-dependent output, provide input/output pairs:

````markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:

```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly
Output:

```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Follow this style: type(scope): brief description, then explanation.
````

---

## Workflow Pattern

For complex multi-step tasks:

````markdown
## Form processing workflow

Copy this checklist and track progress:

```
Progress:
- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output
```

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix any validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.
````

---

## Feedback Loop Pattern

For quality-critical tasks:

```markdown
## Content review process

1. Draft content following STYLE_GUIDE.md
2. Review against checklist:
   - Terminology consistency
   - Examples follow standard format
   - All required sections present
3. If issues found:
   - Note each issue with section reference
   - Revise content
   - Review checklist again
4. Only proceed when all requirements met
5. Finalize and save
```

For code-based validation:

```markdown
## Document editing process

1. Make edits to `word/document.xml`
2. **Validate immediately**: `python scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review error message
   - Fix issues in XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python scripts/pack.py unpacked_dir/ output.docx`
```

---

## Conditional Workflow Pattern

For branching logic:

```markdown
## Document modification workflow

1. Determine modification type:

   **Creating new content?** -> Follow "Creation workflow" below
   **Editing existing content?** -> Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

---

## Progressive Disclosure Pattern

### Pattern 1: High-level with References

````markdown
---
name: pdf-processing
description: Extract text and tables from PDFs, fill forms, merge documents. Use when working with PDF files.
---

# PDF Processing

## Quick start

```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md)
**API reference**: See [REFERENCE.md](REFERENCE.md)
**Examples**: See [EXAMPLES.md](EXAMPLES.md)
````

### Pattern 2: Domain-specific Organization

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing)
    ├── sales.md (opportunities, pipeline)
    └── product.md (API usage, features)
```

````markdown
# BigQuery Analysis

## Available datasets

**Finance**: Revenue, ARR, billing -> See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline -> See [reference/sales.md](reference/sales.md)
**Product**: API usage, features -> See [reference/product.md](reference/product.md)

## Quick search

```bash
grep -i "revenue" reference/finance.md
```
````

---

## Executable Scripts Pattern

### Error Handling

Scripts should solve problems, not punt to Claude:

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        print(f"Cannot access {path}, using default")
        return ''
```

### Self-Documenting Constants

```python
# HTTP requests typically complete within 30 seconds
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
MAX_RETRIES = 3
```

### Utility Script Documentation

````markdown
## Utility scripts

**analyze_form.py**: Extract form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

Output:

```json
{
  "field_name": { "type": "text", "x": 100, "y": 200 }
}
```

**validate_boxes.py**: Check for overlapping boxes

```bash
python scripts/validate_boxes.py fields.json
# Returns: "OK" or lists conflicts
```
````

### Package Dependencies

Always be explicit:

````markdown
Install required package: `pip install pypdf`

```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```
````

---

## Command Language

Direct commands increase instruction compliance. Soft language gets ignored.

| Soft (Avoid)             | Direct (Use)              |
| ------------------------ | ------------------------- |
| "You might want to..."   | "You must..."             |
| "Consider doing..."      | "Your task is to..."      |
| "It would be good to..." | "Always..."               |
| "Try to..."              | "Execute..."              |
| "You could..."           | "Return..." / "Output..." |

**When to use direct commands:**

- Critical constraints that cannot be violated
- Output format requirements
- Safety-critical operations
- Steps that must execute in exact order

**When softer language is acceptable:**

- Suggestions within high-freedom tasks
- Optional enhancements
- Style preferences (not requirements)

**Example transformation:**

```markdown
# Before (soft)

You might want to validate the input before processing.
Consider checking for null values.

# After (direct)

You must validate the input before processing.
Always check for null values. Reject invalid input immediately.
```

---

## Persuasion Principles

Research-backed influence principles that increase Claude's compliance with skill instructions. Based on Cialdini's work, adapted for AI agents.

| Principle        | How It Works                              | Application in Skills                                                   |
| ---------------- | ----------------------------------------- | ----------------------------------------------------------------------- |
| **Authority**    | Expertise signals increase compliance     | "Following industry best practices..." / "Per the API specification..." |
| **Social Proof** | "Everyone does this" changes behavior     | "Standard convention is..." / "Most implementations..."                 |
| **Consistency**  | Prior commitments increase follow-through | "As established in step 1..." / "Continuing the pattern..."             |
| **Specificity**  | Concrete details signal legitimacy        | Exact commands, specific values, named tools                            |

### Authority Pattern

```markdown
# Weak

Format the output nicely.

# Strong (authority)

Format output following the OpenAPI 3.0 specification.
Use ISO 8601 for all timestamps.
```

### Social Proof Pattern

```markdown
# Weak

You should add error handling.

# Strong (social proof)

Production systems universally implement error handling at API boundaries.
Add try/catch blocks around all external calls.
```

### Consistency Pattern

```markdown
# Weak

Now do the validation.

# Strong (consistency)

Having generated the schema in step 2, you must now validate against it.
This ensures the output matches your earlier commitment.
```

### Combining Principles

For critical instructions, combine multiple principles:

```markdown
# Maximum compliance (Authority + Social Proof + Direct Command)

Per security best practices used across the industry, you must sanitize
all user input before database insertion. Execute parameterized queries only.
```

### Anti-patterns

Avoid these - they reduce compliance or accuracy:

- Emotional appeals ("Please try your best") - reduces factual accuracy
- Urgency/scarcity ("Do this immediately") - unnecessary for AI
- Flattery ("You're great at this") - triggers sycophancy, not compliance

---
name: skill-builder
description: Creates effective Claude Code Skills following Anthropic best practices with integrated validation and evaluation. Use when asked to create a skill, build a new skill, make a custom skill, design agent capabilities, or help someone write skill instructions.
---

# Skill Builder

Build Skills that Claude can discover, load efficiently, and execute effectively - with integrated validation loops to ensure quality.

## Quick Reference

| Constraint      | Requirement                                                    |
| --------------- | -------------------------------------------------------------- |
| `name`          | Max 64 chars, lowercase, hyphens only, no "anthropic"/"claude" |
| `description`   | Max 1024 chars, third person, what + when to use               |
| SKILL.md body   | Under 500 lines; use progressive disclosure patterns if larger |
| File references | One level deep from SKILL.md only                              |
| Paths           | Unix-style forward slashes only                                |

## Workflow

Copy and track progress:

```
Skill Creation Progress:
- [ ] Phase 1: Define requirements
- [ ] Phase 2: Structure the skill
- [ ] Phase 3: Write content
- [ ] Phase 4: Validate quality
- [ ] Phase 5: Evaluate and iterate
```

### Phase 1: Define

Use the AskUserQuestion tool to gather requirements. Ask clarifying questions until you have clear answers for:

1. What task does this Skill enable? What repeated context does it eliminate?
2. What user requests should trigger this Skill?
3. Single domain or multiple domains?
4. How deterministic does the output need to be?

**Using AskUserQuestion effectively:**

- Ask one focused question at a time when topics are complex
- Provide concrete options when choices are constrained (e.g., determinism levels)
- Use follow-up questions to clarify ambiguous responses
- Continue asking until requirements are unambiguous

**Determinism levels:**

| Level  | When to use                          | Example                                      |
| ------ | ------------------------------------ | -------------------------------------------- |
| High   | Exact output required, fragile tasks | Database migrations, API calls, file formats |
| Medium | Preferred pattern, some flexibility  | Report generation, code templates            |
| Low    | Context-dependent, many valid paths  | Code review, content writing, analysis       |

**Validation checkpoint:** Confirm understanding with user before proceeding. Misaligned requirements are the most common cause of skill failure.

### Phase 2: Structure

**Simple skill** (under ~100 lines):

```
skill-name/
└── SKILL.md
```

**Complex skill** (approaching 500 lines):

```
skill-name/
├── SKILL.md          # Core instructions + common workflows (loaded when triggered)
├── REFERENCE.md      # Detailed API/schema info (loaded only when needed)
└── scripts/          # Utilities (executed, not loaded into context)
```

Keep frequently-used content in SKILL.md. Only split to reference files when:

- Content is rarely needed (e.g., advanced features, edge cases)
- Content is large and domain-specific (e.g., schema references)
- Content would push SKILL.md over 500 lines

**Validation checkpoint:** Review structure against complexity. Over-engineering simple skills reduces clarity.

See [EXAMPLES.md](EXAMPLES.md) for complete examples at different complexity levels.

### Phase 3: Write

**Frontmatter** (required):

```yaml
---
name: lowercase-with-hyphens
description: [What it does]. Use when [specific triggers].
---
```

**Body principles**:

- **Concise**: Only add context Claude lacks. Challenge each paragraph.
- **Specific**: Concrete examples, not abstract descriptions.
- **Consistent**: One term per concept throughout.
- **Progressive**: Core in SKILL.md, details in reference files.
- **Direct**: Use command language for critical instructions. See [Command Language](#command-language).
- **Persuasive**: Apply influence principles to increase compliance. See [Persuasion Principles](#persuasion-principles).

See [PATTERNS.md](PATTERNS.md) for common patterns.

**Validation checkpoint:** Apply conciseness test - for each paragraph ask: "Does Claude need this? Can I assume Claude knows this? Does this justify its token cost?"

### Phase 4: Validate

Spawn a validation agent to perform comprehensive quality checks. This isolates validation from the main conversation and enables thorough analysis without token pressure.

**Spawn validation agent:**

Use the Task tool with the following prompt:

<agent-prompt purpose="validation">
You are a skill validation agent. Analyze the skill at [SKILL_PATH] and perform:

1. SYNTAX VALIDATION
   python scripts/validate_syntax.py [SKILL_PATH]

   For each issue found, explain why it's a problem and how it should be fixed.

2. STRUCTURAL VALIDATION
   python scripts/validate_skill.py [SKILL_PATH]

   For each check, explain what you're validating and why it passed or failed.

3. TERMINOLOGY CONSISTENCY CHECK
   python scripts/check_terminology.py [SKILL_PATH]

   For each candidate pair flagged, provide justification:
   - COMBINE [preferred term]: Why these terms refer to the same concept
   - KEEP: The distinct meanings that justify separate terms

4. OUTPUT FORMAT
   Include justification for each validation result. Conclude with a VERDICT:

| Pass Rate | Verdict        | Action                                    |
| --------- | -------------- | ----------------------------------------- |
| 100%      | READY          | Proceed to Phase 5 for real-world testing |
| 70-99%    | NEEDS_REVISION | Address failed checks, re-run validation  |
| < 70%     | MAJOR_ISSUES   | Return to Phase 3, significant rewrite    |

</agent-prompt>

For extended validation checklists beyond static checks, see [CHECKLIST.md](CHECKLIST.md).

### Phase 5: Evaluate and Iterate

This phase tests whether the skill triggers correctly using blind evaluation. Subagents make invocation decisions without knowing the expected result, then you compare their decisions to ground truth.

**Important:** Skill detection uses only the `name` and `description` fields from frontmatter. The SKILL.md body is not used for detection. Any fixes in this phase should modify the name, description, or both - never the body content.

**Step 1: Generate test prompts with ground truth labels**

Create 40 test prompts across four categories. Keep the category labels private - agents will not see them.

| Category               | Count | Ground Truth | Description                                                   |
| ---------------------- | ----- | ------------ | ------------------------------------------------------------- |
| MUST_INVOKE            | 10    | YES          | Clear cases where skill should definitely trigger             |
| SHOULD_INVOKE_EDGE     | 10    | YES          | Edge cases that should still trigger despite indirect wording |
| SHOULD_NOT_INVOKE_EDGE | 10    | NO           | Ambiguous cases where clarification is needed before invoking |
| MUST_NOT_INVOKE        | 10    | NO           | Clear cases where skill should definitely NOT trigger         |

**Critical: Edge case categorization principles**

When categorizing edge cases, apply this test: **"If the user said this, should the skill auto-invoke, or should Claude ask clarifying questions first?"**

- If the prompt has **only one reasonable interpretation** that matches this skill → YES (SHOULD_INVOKE_EDGE)
- If the prompt is **ambiguous with multiple valid solutions** (this skill, other skills, settings, config files, etc.) → NO (SHOULD_NOT_INVOKE_EDGE)
- If the **correct behavior is to ask for clarification** → NO (SHOULD_NOT_INVOKE_EDGE)

Example categorization for a skill-builder skill:

| Prompt                                          | Category                    | Reasoning                                                      |
| ----------------------------------------------- | --------------------------- | -------------------------------------------------------------- |
| "I want to develop a skill for linting"         | SHOULD_INVOKE_EDGE (YES)    | "develop a skill" clearly maps to skill creation               |
| "Can you help me with my SKILL.md file?"        | SHOULD_NOT_INVOKE_EDGE (NO) | Could be editing, debugging, or creating - ask first           |
| "I need to improve how Claude handles my tasks" | SHOULD_NOT_INVOKE_EDGE (NO) | Could be skills, CLAUDE.md, settings, or prompting - ask first |
| "Help me configure Claude for my project"       | SHOULD_NOT_INVOKE_EDGE (NO) | Multiple valid solutions exist - ask first                     |

Generate prompts using these guidelines:

```
MUST_INVOKE (10 prompts, ground truth: YES):
- 5 direct, explicit requests using trigger terms from description
- 3 paraphrased requests using synonyms or related terms
- 2 requests with loose wording but unambiguous user intent

SHOULD_INVOKE_EDGE (10 prompts, ground truth: YES):
- Requests where the skill is clearly the right solution despite indirect phrasing
- Paraphrases that map to exactly one interpretation: this skill
- Wording that a reasonable person would only mean one thing by
- NOT prompts where "ask for clarification" would be the correct response

SHOULD_NOT_INVOKE_EDGE (10 prompts, ground truth: NO):
- Ambiguous requests where multiple tools/solutions could apply
- Prompts where the correct response is "ask for clarification first"
- Similar keywords used in a different but plausible context
- Requests that might relate to this skill but have other valid interpretations

MUST_NOT_INVOKE (10 prompts, ground truth: NO):
- 5 requests for clearly unrelated tasks
- 3 requests using completely different domains
- 2 requests that share no semantic overlap with the skill
```

**Step 2: Spawn 40 blind evaluation agents**

Launch 40 agents in parallel - one per prompt. Each agent evaluates a single prompt in complete isolation, ensuring no cross-prompt contamination or pattern-matching across the test set.

Each agent does NOT know:

- The category name
- The expected/ground truth result
- Whether the prompt "should" or "should not" invoke
- What other prompts are being tested

Use this template for each agent:

<agent-prompt purpose="blind-eval-single">
You are simulating Claude Code's skill matching system. Decide whether you would invoke the specified skill for this user prompt.

Skill name: [SKILL_NAME]
Skill description: [SKILL_DESCRIPTION]

User prompt: "[SINGLE_PROMPT]"

Provide:

1. Your decision: INVOKE or NO_INVOKE
2. Confidence level: HIGH / MEDIUM / LOW
3. Justification:
   - Exact trigger terms from description that match (or why none match)
   - Semantic similarity analysis
   - Edge case considerations (similar keywords in different contexts, paraphrased intent)
     </agent-prompt>

**Step 3: Compare decisions to ground truth**

After agents complete, compare each decision to the ground truth label you assigned in Step 1.

For each prompt:

- If agent said INVOKE and ground truth is YES: PASS
- If agent said NO_INVOKE and ground truth is NO: PASS
- Otherwise: FAIL

**Step 4: Aggregate results**

```
BLIND EVALUATION SUMMARY

Category                 | Correct | Total | Rate
-------------------------|---------|-------|------
MUST_INVOKE              | X       | 10    | Y%
SHOULD_INVOKE_EDGE       | X       | 10    | Y%
SHOULD_NOT_INVOKE_EDGE   | X       | 10    | Y%
MUST_NOT_INVOKE          | X       | 10    | Y%
-------------------------|---------|-------|------
OVERALL                  | X       | 40    | Y%

FAILURES:
[For each failed prompt, list:]
- Prompt: "[text]"
- Category: [category]
- Expected: [YES/NO]
- Agent said: [INVOKE/NO_INVOKE]
- Agent's justification: [quote their reasoning]
- Diagnosis: [Why the mismatch occurred - missing trigger term, over-broad description, etc.]

VERDICT: [See criteria below]
```

**Verdict criteria:**

| Overall Pass Rate  | Verdict      | Action                                  |
| ------------------ | ------------ | --------------------------------------- |
| 90-100% (36-40/40) | READY        | Skill triggers correctly, ready for use |
| 70-89% (28-35/40)  | NEEDS_TUNING | Adjust description triggers, re-test    |
| < 70% (< 28/40)    | MAJOR_ISSUES | Rewrite description and trigger terms   |

**Step 5: Iterate on failures (name/description changes only)**

<CRITICAL>
You MUST iterate automatically when verdict is NEEDS_TUNING or MAJOR_ISSUES.
Do NOT ask the user for permission to update and re-test.
Do NOT present intermediate results and wait for approval.
Silently fix the description, re-run evaluation, and repeat until READY.
Only present the final READY result to the user.
</CRITICAL>

Analyze each failure's diagnosis:

1. **False negatives in MUST_INVOKE:** Add missing trigger terms to description
2. **False negatives in SHOULD_INVOKE_EDGE:** Add synonyms or broaden trigger phrases
3. **False positives in SHOULD_NOT_INVOKE_EDGE:** Make description more specific, add disambiguating context
4. **False positives in MUST_NOT_INVOKE:** Narrow description scope or add exclusion language

After changes:

1. Re-run Phase 4 validation (name/description are validated there)
2. Re-run Phase 5 blind evaluation with the SAME test prompts
3. Repeat until verdict is READY

Do NOT modify the SKILL.md body in this phase - detection issues are always name/description issues.

---

## Essential Patterns

See [EXAMPLES.md](EXAMPLES.md) for complete skills demonstrating these patterns.

### Degrees of Freedom

Match specificity to task fragility:

**High freedom** - Multiple valid approaches:

```markdown
Review the code structure and suggest improvements for readability.
```

**Medium freedom** - Preferred pattern with flexibility:

```markdown
Use this template and customize as needed:
def process(data, format="markdown"): ...
```

**Low freedom** - Exact execution required:

```markdown
Run exactly: python scripts/migrate.py --verify --backup
Do not modify this command.
```

### Progressive Disclosure

SKILL.md is the overview; point to reference files for details:

```markdown
## Quick start

[Essential instructions here]

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md)
**API reference**: See [REFERENCE.md](REFERENCE.md)
```

Files never point deeper. Keep references one level from SKILL.md.

### Workflows with Checklists

For complex tasks, provide copyable checklists:

```markdown
Copy and track progress:

- [ ] Step 1: Analyze input
- [ ] Step 2: Validate structure
- [ ] Step 3: Generate output
- [ ] Step 4: Verify result
```

### Feedback Loops

For quality-critical output:

```markdown
1. Generate draft
2. Validate: run scripts/validator.py
3. If errors: fix and validate again
4. Only proceed when validation passes
```

### Command Language

Use direct commands for critical instructions. See [PATTERNS.md](PATTERNS.md#command-language) for examples.

| Soft (Avoid)           | Direct (Use)  |
| ---------------------- | ------------- |
| "You might want to..." | "You must..." |
| "Consider doing..."    | "Always..."   |
| "Try to..."            | "Execute..."  |

### Persuasion Principles

Use authority, social proof, and consistency to increase compliance. See [PATTERNS.md](PATTERNS.md#persuasion-principles) for detailed examples.

| Principle        | Example Application                                            |
| ---------------- | -------------------------------------------------------------- |
| **Authority**    | "Per the API specification..." / "Following standards..."      |
| **Social Proof** | "Production systems universally..." / "Standard convention..." |
| **Consistency**  | "As established in step 1..." / "Continuing the pattern..."    |

---

## Quick Checklist (Manual Review)

These items require human judgment and are not covered by static validation scripts:

```
Content Quality
- [ ] No explanations of common knowledge (assume Claude's competence)
- [ ] No time-sensitive information (or uses <details> for legacy patterns)
- [ ] One default tool per task (with escape hatch for alternatives)

Instruction Language
- [ ] Critical constraints use direct commands ("You must", "Always", "Execute")
- [ ] No soft language for required behaviors ("Consider", "Try to", "You might")
- [ ] Authority signals for compliance-critical instructions (specs, standards, best practices)
- [ ] Consistency references for multi-step workflows ("As established in step X...")

Workflow Quality
- [ ] Clear sequential steps
- [ ] Feedback loops for quality-critical output
- [ ] Validation before destructive operations

Code Quality (if scripts included)
- [ ] Scripts handle errors explicitly
- [ ] No magic numbers (values documented)
- [ ] Dependencies listed with install commands
- [ ] Clear distinction: execute script vs read as reference
```

---

## Runtime Troubleshooting

Issues that may occur after the skill passes validation and invocation testing:

| Issue                       | Fix                                                                    |
| --------------------------- | ---------------------------------------------------------------------- |
| Claude ignores instructions | Replace soft language with direct commands ("You must", "Always")      |
| Claude over-reads files     | Improve file structure, add clear navigation                           |
| Inconsistent behavior       | Reduce degrees of freedom for critical steps                           |
| Fails on edge cases         | Add explicit handling or graceful fallbacks                            |
| Works on Opus, fails Haiku  | Add more explicit guidance for critical steps                          |
| Skips validation steps      | Add authority signals ("Per specification...", "Industry standard...") |
| Breaks multi-step workflows | Add consistency anchors ("Having completed step X, you must now...")   |
| Outputs wrong format        | Use direct commands with specificity ("Output exactly: [format]")      |

---

## Reference Files

- [CHECKLIST.md](CHECKLIST.md) - Extended quality validation checklist
- [PATTERNS.md](PATTERNS.md) - Detailed pattern examples
- [EXAMPLES.md](EXAMPLES.md) - Complete skill examples

---

## Description Formula

```
[Action verbs]. Use when [triggers and contexts].
```

**Good examples:**

```yaml
# PDF Processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDFs or when the user mentions forms, document extraction, or PDF editing.

# Git Commit Helper
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.

# BigQuery Analysis
description: Query and analyze BigQuery datasets with proper filtering. Use when the user asks about data analysis, SQL queries, or mentions BigQuery or analytics.
```

**Bad examples:**

```yaml
description: Helps with documents  # Too vague
description: I can process files   # Wrong person
description: Useful for data       # No triggers
```

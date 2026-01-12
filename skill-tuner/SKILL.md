---
name: skill-tuner
description: Diagnose and fix skill trigger detection problems using blind validation testing. Use when a skill fails to invoke on expected prompts, isn't being detected, or the user asks to tune skill triggers, tune an existing description for better trigger matching, test trigger detection, or run blind validation. Not for creating new skills, writing new descriptions from scratch, evaluating description quality, general skill improvements, or runtime behavior.
---

# Skill Tuner

Diagnose why skills aren't triggering and iterate on name/description until they pass blind validation at 95%+ accuracy.

## Workflow

```
Skill Tuning Progress:
- [ ] Step 1: Identify the problem
- [ ] Step 2: Diagnose trigger gaps
- [ ] Step 3: Run blind validation (40 prompts)
- [ ] Step 4: Iterate until 95%+ pass rate
- [ ] Step 5: Apply changes
```

---

## Step 1: Identify the Problem

Gather information about the detection failure.

**Ask using AskUserQuestion:**

1. Which skill is failing to trigger?
2. What prompt should have triggered it but didn't?
3. Is this a false negative (should invoke but didn't) or false positive (invoked when it shouldn't)?

**Read the skill's frontmatter:**

```bash
head -10 /path/to/skill/SKILL.md
```

Extract and record:

- `name`: The skill name
- `description`: The full description text

**CRITICAL:** Skill detection uses ONLY the `name` and `description` fields. The SKILL.md body content is never used for detection. All fixes must modify name, description, or both.

---

## Step 2: Diagnose Trigger Gaps

Analyze why the prompt failed to match.

**Compare the failed prompt against the description:**

| Check       | Question                                                              |
| ----------- | --------------------------------------------------------------------- |
| Exact terms | Does the prompt contain any exact trigger words from the description? |
| Synonyms    | Does the prompt use synonyms that aren't in the description?          |
| Paraphrases | Is the intent clear but phrased differently than expected?            |
| Ambiguity   | Could the prompt reasonably match multiple skills?                    |

**Common failure patterns:**

| Pattern                 | Example                                           | Fix                         |
| ----------------------- | ------------------------------------------------- | --------------------------- |
| Missing synonym         | User said "glitch" but description only has "bug" | Add synonyms to description |
| Over-specific triggers  | Description requires "debug" but user said "fix"  | Broaden trigger phrases     |
| Under-specific triggers | Description too broad, matches unrelated prompts  | Add disambiguating context  |
| Missing use case        | User described symptom, description lists actions | Add symptom-based triggers  |

**Output diagnosis:**

```
DIAGNOSIS:
- Failed prompt: "[the prompt]"
- Trigger terms in description: [list them]
- Gap identified: [what's missing or wrong]
- Proposed fix: [specific change to description]
```

---

## Step 3: Run Blind Validation

Test whether the description correctly triggers across 40 diverse prompts.

### Step 3.1: Generate Test Prompts

Create 40 prompts across four categories. Keep category labels private - agents will not see them.

| Category               | Count | Ground Truth | Description                                                   |
| ---------------------- | ----- | ------------ | ------------------------------------------------------------- |
| MUST_INVOKE            | 10    | YES          | Clear cases where skill should definitely trigger             |
| SHOULD_INVOKE_EDGE     | 10    | YES          | Edge cases that should still trigger despite indirect wording |
| SHOULD_NOT_INVOKE_EDGE | 10    | NO           | Ambiguous cases needing clarification before invoking         |
| MUST_NOT_INVOKE        | 10    | NO           | Clear cases where skill should NOT trigger                    |

**Prompt generation guidelines:**

```
MUST_INVOKE (ground truth: YES):
- 5 direct requests using exact trigger terms from description
- 3 paraphrased requests using synonyms
- 2 requests with loose wording but unambiguous intent

SHOULD_INVOKE_EDGE (ground truth: YES):
- Requests where skill is clearly right despite indirect phrasing
- Paraphrases with exactly one interpretation: this skill
- Include the user's originally failed prompt if it belongs here

SHOULD_NOT_INVOKE_EDGE (ground truth: NO):
- Ambiguous requests where multiple tools could apply
- Prompts where correct response is "ask for clarification"
- Similar keywords in different contexts

MUST_NOT_INVOKE (ground truth: NO):
- 5 requests for clearly unrelated tasks
- 3 requests in completely different domains
- 2 requests with no semantic overlap
```

**Edge case categorization test:** "If the user said this, should the skill auto-invoke, or should Claude ask clarifying questions first?"

- Only one reasonable interpretation matching this skill → YES
- Ambiguous with multiple valid solutions → NO
- Correct behavior is to ask for clarification → NO

### Step 3.2: Spawn 40 Blind Evaluation Agents

Launch 40 agents in parallel using the Task tool with `model: haiku`. Each agent evaluates ONE prompt in complete isolation.

Each agent does NOT know:

- The category name
- The expected/ground truth result
- Whether the prompt "should" or "should not" invoke
- What other prompts are being tested

**Agent prompt template:**

```
You are simulating Claude Code's skill matching system. Decide whether you would invoke the specified skill for this user prompt.

Skill name: [SKILL_NAME]
Skill description: [SKILL_DESCRIPTION]

User prompt: "[SINGLE_PROMPT]"

Provide your response in this exact format:
DECISION: [INVOKE or NO_INVOKE]
CONFIDENCE: [HIGH/MEDIUM/LOW]
JUSTIFICATION: [Brief explanation of trigger term matches or why none match]
```

**CRITICAL:** You MUST spawn all 40 agents in a SINGLE message with 40 parallel Task tool calls. Do not spawn them sequentially.

### Step 3.3: Compare Results to Ground Truth

After all agents complete, compare each decision to the ground truth label.

| Agent Decision | Ground Truth | Result                |
| -------------- | ------------ | --------------------- |
| INVOKE         | YES          | PASS                  |
| NO_INVOKE      | NO           | PASS                  |
| INVOKE         | NO           | FAIL (false positive) |
| NO_INVOKE      | YES          | FAIL (false negative) |

### Step 3.4: Aggregate Results

```
BLIND VALIDATION RESULTS

Category                 | Correct | Total | Rate
-------------------------|---------|-------|------
MUST_INVOKE              | X       | 10    | Y%
SHOULD_INVOKE_EDGE       | X       | 10    | Y%
SHOULD_NOT_INVOKE_EDGE   | X       | 10    | Y%
MUST_NOT_INVOKE          | X       | 10    | Y%
-------------------------|---------|-------|------
OVERALL                  | X       | 40    | Y%

FAILURES:
[For each failure:]
- Prompt: "[text]"
- Category: [category]
- Expected: [YES/NO]
- Agent said: [INVOKE/NO_INVOKE]
- Justification: [agent's reasoning]
- Diagnosis: [why mismatch occurred]
```

**Verdict:**

| Pass Rate          | Verdict      | Action                      |
| ------------------ | ------------ | --------------------------- |
| 95-100% (38-40/40) | READY        | Skill triggers correctly    |
| 85-94% (34-37/40)  | NEEDS_TUNING | Adjust description, re-test |
| < 85% (< 34/40)    | MAJOR_ISSUES | Significant rewrite needed  |

---

## Step 4: Iterate Until 95%+

<CRITICAL>
You MUST iterate automatically when verdict is NEEDS_TUNING or MAJOR_ISSUES.
Do NOT ask the user for permission to update and re-test.
Do NOT present intermediate results and wait for approval.
Silently fix the description, re-run validation, and repeat until READY.
Only present the final READY result to the user.
</CRITICAL>

**Fix patterns by failure type:**

| Failure Type                             | Fix                            |
| ---------------------------------------- | ------------------------------ |
| False negative in MUST_INVOKE            | Add missing trigger terms      |
| False negative in SHOULD_INVOKE_EDGE     | Add synonyms, broaden phrases  |
| False positive in SHOULD_NOT_INVOKE_EDGE | Make description more specific |
| False positive in MUST_NOT_INVOKE        | Narrow scope, add exclusions   |

**After each change:**

1. Update the description
2. Re-run blind validation with the SAME 40 test prompts
3. Check if 95%+ achieved
4. If not, analyze new failures and iterate again

**Maximum iterations:** 5. If still failing after 5 iterations, present results to user and ask for guidance.

---

## Step 5: Apply Changes

Once 95%+ achieved:

1. Show the user the before/after descriptions
2. Show the validation results
3. Ask for confirmation before modifying the skill file
4. Update the skill's SKILL.md frontmatter

**Final output format:**

```
SKILL TUNING COMPLETE

Original description:
[old description]

Tuned description:
[new description]

Validation: [X]/40 ([Y]%)

Changes made:
- [list specific additions/modifications]

Ready to apply changes to [skill path]?
```

---

## Quick Reference

**Trigger terms for THIS skill:**

- "skill isn't triggering"
- "skill not detected" / "isn't being detected"
- "tune skill triggers"
- "tune my skill description"
- "test trigger detection"
- "skill not invoking" / "failed to invoke"
- "run blind validation"
- "skill keeps missing prompts"

**What this skill does NOT do:**

- Create new skills (use skill-builder)
- Write new descriptions from scratch (use skill-builder)
- Evaluate description quality generally
- Fix runtime behavior issues after successful invocation
- General skill improvements

---
name: debugger
description: Systematically diagnose and fix bugs using a structured methodology with council review. Use when the user reports a bug, error, crash, unexpected behavior, broken functionality, or asks to fix, debug, or troubleshoot issues in their code.
---

# Debugger

Systematically diagnose and fix bugs using a proven methodology with mandatory council review.

## Workflow

```
Debugging Progress:
- [ ] Step 1: Understand the Problem
- [ ] Step 2: Reproduce the Bug
- [ ] Step 3: Isolate & Diagnose
- [ ] Step 4: Council Review
- [ ] Step 5: Implement Fix
- [ ] Step 6: Verify Solution
```

**CRITICAL: Follow this workflow in order. Do NOT skip to fixing without reproducing first. Jumping to fixes without understanding causes incomplete solutions and new bugs.**

---

## Step 1: Understand the Problem

Before touching code, gather complete information.

**Ask using AskUserQuestion if not provided:**

1. **Expected behavior** - What should happen?
2. **Actual behavior** - What happens instead?
3. **Error messages** - Exact text and stack traces
4. **When it started** - Was it ever working? What changed?
5. **Frequency** - Every time, sometimes, or specific conditions?

**Document findings:**

```
Bug Summary:
- Expected: [What should happen]
- Actual: [What happens instead]
- Error: [Exact message if any]
- Frequency: [Always / Sometimes / Conditions]
- Recent changes: [What changed]
```

---

## Step 2: Reproduce the Bug

**You must reproduce the bug before attempting to fix it.** A bug you cannot reproduce is a bug you cannot verify as fixed.

### Reproduction Process

1. Get exact steps from user or determine from context
2. Execute the steps to confirm the bug
3. Document minimal reproduction:

```
Reproduction Steps:
1. [Action]
2. [Action]
3. [Action that triggers bug]
Result: [What happens]
```

### If Bug is Intermittent

Identify patterns:

- **Timing** - Race conditions, timeouts
- **Data** - Specific inputs, edge cases
- **State** - Only after certain actions
- **Environment** - Specific browser, config

### If Cannot Reproduce

**Do NOT proceed to fixing.** Instead:

1. Add logging to capture more data
2. Ask user for more specific steps
3. Check environment differences
4. Review recent commits

---

## Step 3: Isolate & Diagnose

Narrow down the cause using these techniques:

**Stack Trace Analysis:**

- Start from error location
- Trace backward through call stack
- Find first point where behavior diverges

**Binary Search:**

- Use git bisect for regression bugs
- Comment out code sections to isolate

**Component Isolation:**

- Test components independently
- Mock dependencies to rule them out

**Log Analysis:**

- Add strategic logging
- Trace data flow
- Identify where values become incorrect

**Document findings:**

```
Diagnosis:
- Location: [file:line]
- Trigger: [specific condition]
- Root cause: [why it happens]
- Category: [Runtime / Logic / State / Integration / Performance / UI]
```

### Common Bug Categories

| Category    | Common Causes                                         |
| ----------- | ----------------------------------------------------- |
| Runtime     | Null references, type errors, out of bounds           |
| Logic       | Off-by-one, wrong operator, missing edge case         |
| State       | Race conditions, stale data, incorrect initialization |
| Integration | API mismatch, missing error handling, timeouts        |
| Performance | N+1 queries, missing indexes, memory leaks            |
| UI          | Rendering issues, event handler bugs, CSS conflicts   |

---

## Step 4: Council Review

**MANDATORY: Before implementing the fix, invoke the council skill for root cause validation.**

```
Review this bug diagnosis:

Bug: [Brief description]
Location: [file:line]
Root Cause: [Technical explanation]
Category: [Bug category]

Proposed Fix:
[Description of intended solution]

Evaluate as debugging specialists:

1. ROOT CAUSE VALIDATION
   - Is the diagnosed root cause correct?
   - Could there be a deeper underlying issue?
   - Are there related bugs this might mask?

2. FIX ASSESSMENT
   - Will the proposed fix address the root cause?
   - Could it introduce new bugs?
   - Is it the simplest effective solution?

3. EDGE CASES
   - What edge cases should the fix handle?
   - Are there similar patterns elsewhere that need fixing?

4. PREVENTION
   - How could this bug have been prevented?
   - Should tests be added?

Provide specific recommendations.
```

**After council review:**

1. Incorporate feedback into fix approach
2. Note any additional edge cases to handle
3. Proceed to implementation

---

## Step 5: Implement Fix

**Fix the root cause, not just the symptom.**

### Before Writing Code

1. Consider multiple solutions
2. Choose the simplest effective fix
3. Plan minimal change - don't refactor while fixing

### Fix Checklist

```
- [ ] Fix addresses root cause
- [ ] Fix handles edge cases from council review
- [ ] Fix follows codebase patterns
- [ ] No debug code left behind
- [ ] Error handling is appropriate
```

### Common Fix Patterns

**Null Safety:**

```javascript
// Before
user.profile.name;
// After
user?.profile?.name ?? "Unknown";
```

**Race Condition:**

```javascript
// Before
fetchData();
processData();
// After
await fetchData();
processData();
```

**Missing Error Handling:**

```javascript
// Before
const data = await fetch(url);
// After
try {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
} catch (e) {
  handleError(e);
}
```

---

## Step 6: Verify Solution

**A fix is not complete until verified.**

### Verification Checklist

```
- [ ] Original bug no longer reproduces
- [ ] All reproduction steps now work
- [ ] No regression in related functionality
- [ ] Edge cases from council review handled
- [ ] No new console errors
```

### Write a Test (If Applicable)

If the codebase has tests, add one that catches this bug:

```
Test: [Name]
Covers: [What it tests]
Prevents: [This specific regression]
```

---

## Output Format

When debugging is complete, provide:

```
Debug Report
============

Bug: [Title]
Status: FIXED

Root Cause:
[Clear explanation]

Fix Applied:
[What was changed]

Files Modified:
- [file:line] - [change description]

Verification:
- [How verified]

Prevention:
- [Recommendations]
```

---

## Anti-Patterns

| Anti-Pattern          | Problem                   | Do Instead             |
| --------------------- | ------------------------- | ---------------------- |
| Guessing at fixes     | Wastes time, may add bugs | Follow methodology     |
| Fixing symptoms       | Bug recurs differently    | Fix root cause         |
| Multiple changes      | Can't tell what worked    | One change at a time   |
| Skipping reproduction | Can't verify fix          | Always reproduce first |
| Skipping council      | May miss deeper issues    | Always get review      |
| No verification       | Bug may persist           | Test thoroughly        |

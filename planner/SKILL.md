---
name: planner
description: Create comprehensive implementation plans with constraints, tradeoffs, and detailed steps before beginning work. Use when planning features, designing systems, decomposing complex tasks, or when other skills need a well-defined approach before execution. Triggers include "plan this", "help me plan", "create a plan", "before we start", "what's the approach", or requests that would benefit from upfront analysis.
---

# Planner

Create comprehensive plans that surface constraints, analyze tradeoffs, and define clear implementation steps before work begins.

## Invocation Patterns

**Direct user requests** - Run in main conversation (this skill):
- "Plan this feature for me"
- "Help me plan the authentication system"
- "What's the approach for implementing caching?"

Running in main context allows interactive Q&A with the user.

**Programmatic calls from other skills** - Use sub-agent (`subagent_type: planner`):
- frontend-designer invoking planner before building
- backend-expert invoking planner before coding
- Any skill that has already gathered requirements

Running as sub-agent keeps the parent skill's context clean.

## When to Use

- Before implementing features or changes
- When decomposing complex tasks
- When multiple approaches exist and tradeoffs matter
- When constraints need explicit identification
- When other skills invoke planning before execution

## Workflow

```
Planning Progress:
- [ ] Phase 1: Understand the Goal
- [ ] Phase 2: Explore the Space
- [ ] Phase 3: Identify Constraints
- [ ] Phase 4: Analyze Tradeoffs
- [ ] Phase 5: Define Implementation
- [ ] Phase 6: Risk Assessment
- [ ] Phase 7: Present Plan
```

**CRITICAL: Complete each phase before proceeding.**

## Phase 1: Understand the Goal

Establish clarity on what success looks like.

**Gather using AskUserQuestion if not provided:**
1. **Outcome** - What should exist when this is done?
2. **Context** - Why is this needed?
3. **Scope** - What's in/out of scope?
4. **Success criteria** - How will we know it worked?

## Phase 2: Explore the Space

Investigate before committing to an approach.

**For code/technical tasks:**
- Read existing code in relevant areas
- Identify patterns and conventions
- Check for similar implementations
- Understand dependencies

## Phase 3: Identify Constraints

Surface all limitations before designing solutions.

**Classify each:**
- **Hard constraint**: Cannot be violated
- **Soft constraint**: Preferred but negotiable
- **Assumption**: Believed true, should validate

## Phase 4: Analyze Tradeoffs

For each major decision:
1. Identify 2-3 viable approaches
2. Evaluate against constraints
3. Assess pros and cons
4. Recommend with reasoning

**For complex tradeoffs**, invoke council for multi-perspective analysis.

## Phase 5: Define Implementation

Break down into concrete steps.

**Requirements:**
- Each step produces verifiable output
- Steps ordered by dependencies
- Small enough to complete in one session
- Include validation criteria

## Phase 6: Risk Assessment

Identify what could go wrong and how to handle it.

## Phase 7: Present Plan

Compile findings into coherent plan.

**Before presenting:**
1. Review against original goal
2. Check hard constraints satisfied
3. Ensure steps are actionable

## Adapting Plan Depth

| Complexity  | Focus                              |
| ----------- | ---------------------------------- |
| Simple      | Goal, Steps - brief format         |
| Medium      | Goal, Constraints, Steps           |
| Complex     | All phases - full analysis         |
| Uncertain   | Explore, Tradeoffs, Risks          |

## Anti-Patterns

| Anti-Pattern               | Do Instead                      |
| -------------------------- | ------------------------------- |
| Skipping to implementation | Complete discovery first        |
| Over-planning simple tasks | Adapt depth to complexity       |
| Ignoring tradeoffs         | Make tradeoffs explicit         |
| Vague steps                | Define outputs and verification |
| No risk assessment         | Identify risks upfront          |
| Plan without approval      | Present plan before executing   |

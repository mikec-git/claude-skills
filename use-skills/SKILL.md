---
name: use-skills
description: Enforces proactive skill invocation discipline. Use when user asks about skill discipline, proactive tool usage, checking skills before responding, or ensuring capabilities are not missed. Trigger phrases include "use skills", "check skills", "invoke skills", "skill discipline", "don't skip skills", "be thorough with tools", "leverage all abilities", "don't miss capabilities".
---

<CRITICAL>
If there is even a 0.1% chance a skill might apply to what you're doing, you MUST invoke the skill.

When a skill applies to your task, you do not have a choice. You must use it.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</CRITICAL>

## The Rule

**Invoke relevant skills BEFORE any response or action.** Even a 0.1% chance a skill might apply means you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

## Workflow

1. User message received
2. Check: Might any skill apply? (even 0.1% chance)
3. If yes: Invoke the Skill tool
4. Announce: "Using [skill] to [purpose]"
5. If skill has checklist: Create TodoWrite todo per item
6. Follow skill instructions exactly
7. Then respond to user

## Red Flags

These thoughts mean STOP - you're rationalizing:

| Thought                             | Reality                                                        |
| ----------------------------------- | -------------------------------------------------------------- |
| "This is just a simple question"    | Questions are tasks. Check for skills.                         |
| "I need more context first"         | Skill check comes BEFORE clarifying questions.                 |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first.                   |
| "I can check files quickly"         | Files lack conversation context. Check for skills.             |
| "Let me gather information first"   | Skills tell you HOW to gather information.                     |
| "This doesn't need a formal skill"  | If a skill exists, use it.                                     |
| "I remember this skill"             | Skills evolve. Read current version.                           |
| "This doesn't count as a task"      | Action = task. Check for skills.                               |
| "The skill is overkill"             | Simple things become complex. Use it.                          |
| "I'll just do this one thing first" | Check BEFORE doing anything.                                   |
| "This feels productive"             | Undisciplined action wastes time. Skills prevent this.         |
| "I know what that means"            | Knowing the concept does not equal using the skill. Invoke it. |

## Skill Priority

When multiple skills could apply:

1. **Process skills first** (brainstorming, debugging, planning) - these determine HOW to approach the task
2. **Implementation skills second** (domain-specific tools) - these guide execution

Examples:

- "Build X" - brainstorming/planning first, then implementation skills
- "Fix this bug" - debugging first, then domain-specific skills

## Skill Types

**Rigid**: Follow exactly. Do not adapt away from discipline. Examples: TDD, debugging workflows.

**Flexible**: Adapt principles to context. Examples: code patterns, style guides.

The skill itself indicates which type it is.

## User Instructions

Instructions say WHAT, not HOW. "Add X" or "Fix Y" does not mean skip workflows.

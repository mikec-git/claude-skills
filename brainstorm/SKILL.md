---
name: brainstorm
description: Facilitate structured ideation sessions using proven frameworks like SCAMPER and Six Thinking Hats, producing detailed idea explorations with pros/cons and next steps. Use when the user asks to brainstorm, wants ideas for something, explores "what if" scenarios, or asks for help thinking through a problem.
---

# Brainstorm

Facilitate structured ideation sessions that produce high-quality, actionable ideas.

## Workflow

Copy and track progress:

```
Brainstorming Session:
- [ ] Step 1: Clarify the challenge
- [ ] Step 2: Select framework
- [ ] Step 3: Generate ideas
- [ ] Step 4: Deep dive on top ideas
- [ ] Step 5: Define next steps
```

### Step 1: Clarify the Challenge

Before generating ideas, understand the problem space. Ask clarifying questions using AskUserQuestion:

- What problem are you trying to solve?
- Who is this for? (audience, user, customer)
- What constraints exist? (time, budget, technical, etc.)
- What has already been tried or considered?
- What does success look like?

You must have clear answers before proceeding. Ambiguous challenges produce unfocused ideas.

### Step 2: Select Framework

Choose the framework best suited to the challenge type:

| Challenge Type         | Framework             | When to Use                                         |
| ---------------------- | --------------------- | --------------------------------------------------- |
| Improve existing thing | SCAMPER               | Enhancing products, processes, or solutions         |
| Complex decision       | Six Thinking Hats     | Multi-faceted problems needing diverse perspectives |
| Explore possibilities  | Mind Mapping          | Open-ended exploration, finding connections         |
| Overcome obstacles     | Reverse Brainstorming | Stuck situations, identifying hidden blockers       |
| Find opportunities     | SWOT + Ideation       | Strategic planning, market opportunities            |

Present the recommended framework to the user and explain why it fits their challenge.

### Step 3: Generate Ideas

Execute the selected framework systematically.

**SCAMPER Method:**

- **S**ubstitute: What can be replaced?
- **C**ombine: What can be merged or integrated?
- **A**dapt: What can be modified from elsewhere?
- **M**odify: What can be changed in form or quality?
- **P**ut to other uses: What else could this do?
- **E**liminate: What can be removed?
- **R**everse/Rearrange: What can be flipped or reordered?

**Six Thinking Hats:**

- White Hat: Facts and data - what do we know?
- Red Hat: Emotions and intuition - what feels right?
- Black Hat: Caution - what could go wrong?
- Yellow Hat: Optimism - what are the benefits?
- Green Hat: Creativity - what are new possibilities?
- Blue Hat: Process - what's the best approach?

**Mind Mapping:**

1. Place core challenge at center
2. Branch primary themes
3. Expand each theme with sub-ideas
4. Look for unexpected connections between branches

**Reverse Brainstorming:**

1. Invert the problem: "How could we make this worse?"
2. Generate ways to cause failure
3. Flip each failure mode into a solution

Generate at least 10-15 raw ideas before filtering. Quantity enables quality.

### Step 4: Deep Dive on Top Ideas

Select 3-5 most promising ideas for detailed exploration. For each idea, provide:

**Idea: [Name]**

| Aspect           | Analysis                                         |
| ---------------- | ------------------------------------------------ |
| **Description**  | Clear, specific explanation of the idea          |
| **Pros**         | Key benefits and strengths                       |
| **Cons**         | Risks, challenges, and weaknesses                |
| **Feasibility**  | Technical difficulty, resources needed, timeline |
| **Unique value** | What makes this different from alternatives      |

Rate each idea:

- **Impact potential:** High / Medium / Low
- **Implementation effort:** High / Medium / Low
- **Confidence level:** High / Medium / Low

### Step 5: Define Next Steps

For each explored idea, provide concrete next actions:

```
Idea: [Name]
Recommendation: Pursue / Explore further / Park for later / Discard

Next steps:
1. [Specific action with clear outcome]
2. [Specific action with clear outcome]
3. [Specific action with clear outcome]

Key question to answer: [Critical unknown that needs resolution]
```

## Output Format

Present the final output as:

```
## Brainstorming Summary

**Challenge:** [One-sentence problem statement]
**Framework used:** [Framework name]
**Ideas generated:** [Count]

## Top Ideas

### 1. [Idea Name] - [Recommendation]
[Detailed exploration from Step 4]
[Next steps from Step 5]

### 2. [Idea Name] - [Recommendation]
...

## Quick Reference

| Idea | Impact | Effort | Confidence | Recommendation |
|------|--------|--------|------------|----------------|
| ... | ... | ... | ... | ... |
```

## Guidelines

- Never dismiss ideas during generation phase - filter only after collecting many options
- Challenge assumptions explicitly - ask "why must it be this way?"
- Combine unrelated concepts - innovation often comes from unexpected connections
- Ground ideas in user constraints - creative but feasible beats brilliant but impossible
- When stuck, change perspective - ask "how would [different person/company] approach this?"

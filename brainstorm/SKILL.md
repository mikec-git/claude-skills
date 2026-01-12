---
name: brainstorm
description: Facilitate structured ideation sessions using proven frameworks like SCAMPER and Six Thinking Hats, producing detailed idea explorations with pros/cons and next steps. Use when the user asks to brainstorm, wants ideas for something, explores "what if" scenarios, or asks for help thinking through a problem.
---

# Brainstorm

Facilitate structured ideation sessions using the LLM Council to generate diverse, high-quality ideas from multiple expert perspectives.

## Workflow

Copy and track progress:

```
Brainstorming Session:
- [ ] Step 1: Clarify the challenge
- [ ] Step 2: Select framework
- [ ] Step 3: Convene the council
- [ ] Step 4: Synthesize and present results
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

### Step 3: Convene the Council

Delegate idea generation to the `council-chairman` agent using the Task tool. The council will spawn 5 domain experts tailored to the brainstorming challenge.

**Council prompt template:**

```
BRAINSTORMING SESSION

Challenge: [Clear problem statement from Step 1]
Context: [Audience, constraints, what's been tried, success criteria]
Framework: [Selected framework from Step 2]

TASK FOR THE COUNCIL:

Each expert should generate ideas using the [FRAMEWORK] methodology:

[Include framework details based on selection:]

SCAMPER:
- Substitute: What can be replaced?
- Combine: What can be merged or integrated?
- Adapt: What can be modified from elsewhere?
- Modify: What can be changed in form or quality?
- Put to other uses: What else could this do?
- Eliminate: What can be removed?
- Reverse/Rearrange: What can be flipped or reordered?

Six Thinking Hats:
- White Hat: Facts and data - what do we know?
- Red Hat: Emotions and intuition - what feels right?
- Black Hat: Caution - what could go wrong?
- Yellow Hat: Optimism - what are the benefits?
- Green Hat: Creativity - what are new possibilities?
- Blue Hat: Process - what's the best approach?

Mind Mapping:
- Start from core challenge, branch into themes, expand with sub-ideas
- Look for unexpected connections between branches

Reverse Brainstorming:
- How could we make this problem worse?
- Flip each failure mode into a potential solution

DELIVERABLES:

1. Each expert generates 3-5 ideas from their unique perspective
2. For each idea, provide:
   - Name and clear description
   - Pros and cons
   - Feasibility assessment (technical difficulty, resources, constraints)
   - Unique value proposition
3. Rate each idea: Impact (H/M/L), Effort (H/M/L), Confidence (H/M/L)
4. Final synthesis: Top 3-5 ideas with consensus ranking and recommended next steps
```

**Expert allocation:** The chairman will generate 5 experts relevant to the challenge domain. For example:

- Product brainstorm: Product Manager, UX Designer, Engineer, Marketer, End User Advocate
- Technical brainstorm: Architect, DevOps, Security, Performance Engineer, Skeptic
- Business brainstorm: Strategist, Finance, Operations, Customer Success, Competitor Analyst

### Step 4: Synthesize and Present Results

After the council completes deliberation, present the results in this format:

```
## Brainstorming Summary

**Challenge:** [One-sentence problem statement]
**Framework used:** [Framework name]
**Council experts:** [List the 5 experts convened]
**Ideas generated:** [Total count across all experts]

## Top Ideas (Council Consensus)

### 1. [Idea Name] - [Recommendation: Pursue / Explore / Park / Discard]

| Aspect           | Analysis                                    |
| ---------------- | ------------------------------------------- |
| **Description**  | Clear explanation of the idea               |
| **Pros**         | Key benefits (with expert attribution)      |
| **Cons**         | Risks and challenges (with expert concerns) |
| **Feasibility**  | Difficulty, resources, constraints          |
| **Unique value** | What makes this different                   |

**Ratings:** Impact: [H/M/L] | Effort: [H/M/L] | Confidence: [H/M/L]

**Next steps:**
1. [Specific action with clear outcome]
2. [Specific action with clear outcome]
3. [Specific action with clear outcome]

**Key question to answer:** [Critical unknown that needs resolution]

### 2. [Idea Name] - [Recommendation]
...

## Quick Reference

| Idea | Impact | Effort | Confidence | Recommendation |
|------|--------|--------|------------|----------------|
| ...  | ...    | ...    | ...        | ...            |

## Dissenting Views

[Notable disagreements or alternative perspectives from council members]
```

## Guidelines

- Never dismiss ideas during generation phase - filter only after collecting many options
- Challenge assumptions explicitly - ask "why must it be this way?"
- Combine unrelated concepts - innovation often comes from unexpected connections
- Ground ideas in user constraints - creative but feasible beats brilliant but impossible
- Capture dissenting views - minority opinions often contain valuable insights
- The council's diverse perspectives are the strength - let experts disagree

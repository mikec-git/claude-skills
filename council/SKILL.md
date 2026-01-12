---
name: council
description: Invokes an LLM Council with dynamically generated domain experts for complex questions. Use when facing difficult decisions, trade-off analysis, or when multiple perspectives would improve answer quality. Triggers include "council", "deliberate", "get expert opinions", "multi-perspective".
---

# LLM Council

Invoke the LLM Council to deliberate on complex questions using Andrej Karpathy's three-stage methodology with dynamically generated expert personas.

## When to Use

- Complex decisions with multiple valid approaches
- Questions where different stakeholders would disagree
- Trade-off analysis requiring diverse expertise
- Strategic or architectural decisions
- Any question where "it depends" is the likely answer

**Note:** For implementation planning tasks (breaking down work, identifying constraints, defining steps), use the **planner** skill or agent instead. The council is best for deliberation on complex decisions, not task decomposition.

## How It Works

Delegate to the `council-chairman` agent. The chairman will:

1. **Analyze** the question to identify relevant domains and tension points
2. **Design** 5 expert personas tailored to this specific question
3. **Stage 1** - Spawn experts in parallel for independent first opinions
4. **Stage 2** - Anonymous peer review where each expert ranks others
5. **Stage 3** - Chairman synthesizes final answer from all perspectives

## Expert Allocation

The chairman dynamically generates 5 Opus experts, each with a distinct perspective tailored to the question.

## Invocation

Delegate the full question and context to the council-chairman agent.

## Examples

**Question**: "Should we use microservices or monolith?"

Council might include:

- Distributed Systems Architect
- DevOps Engineer
- Startup CTO
- Junior Developer Advocate
- Skeptic/Complexity Critic

**Question**: "How should we handle user authentication?"

Council might include:

- Security Engineer
- UX Researcher
- Compliance Specialist
- Frontend Developer
- Attacker/Red Team

The experts are always tailored to maximize insight for the specific question.

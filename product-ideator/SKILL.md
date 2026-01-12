---
name: product-ideator
description: Generates and explores software product ideas with market research and expert deliberation. Use when the user wants product ideas, needs help with product research, asks about building a new product, or wants to validate a product concept.
---

# Product Ideator

Generate and deeply explore software product ideas through market research and multi-expert deliberation.

## Workflow

Execute these phases in order:

### Phase 1: Understand the Context

Gather information about the user's starting point:

- **Problem-driven**: What pain point or inefficiency exists?
- **Audience-driven**: Who do they want to build for?
- **Technology-driven**: What technology or trend interests them?
- **Open exploration**: No specific direction yet

Use AskUserQuestion if the input is ambiguous. You must have clarity before proceeding.

### Phase 2: Market Research

Use WebSearch to gather intelligence on:

1. **Existing solutions** - What products already solve this or adjacent problems?
2. **Market gaps** - Where do current solutions fall short?
3. **Target audience** - Who experiences this problem? How do they currently cope?
4. **Market trends** - Is this space growing, shrinking, or shifting?
5. **Monetization models** - How do similar products make money?

Perform at least 3-5 targeted searches. Synthesize findings into a brief market landscape summary.

### Phase 3: Council Deliberation

Invoke the council-chairman agent to deliberate on product direction.

Frame the council question to include:

- The problem/opportunity identified
- Market research findings
- Key tensions or trade-offs discovered

The council will generate domain-specific experts to evaluate the product opportunity from multiple perspectives.

### Phase 4: Idea Synthesis

Based on research and council deliberation, generate 2-3 product concepts. For each concept, provide:

```
## [Product Name]

**One-liner**: [Single sentence describing what it does]

**Problem**: [The specific pain point this addresses]

**Solution**: [How the product solves it]

**Target User**: [Primary persona with context]

**Differentiation**: [Why this beats existing alternatives]

**Key Features (MVP)**:
- [Feature 1]
- [Feature 2]
- [Feature 3]

**Monetization**: [How it makes money]

**Risks & Challenges**:
- [Risk 1]
- [Risk 2]

**Market Opportunity**: [Size and growth potential]
```

### Phase 5: Final Review

Conduct a critical review of the top idea. Evaluate:

| Dimension         | Assessment                                   |
| ----------------- | -------------------------------------------- |
| **Viability**     | Can this be built with reasonable resources? |
| **Desirability**  | Do users actually want this? Evidence?       |
| **Feasibility**   | Technical complexity and unknowns?           |
| **Defensibility** | What prevents competitors from copying?      |
| **Timing**        | Why now? What enables this today?            |

Provide an overall recommendation:

- **Strong opportunity**: Clear path forward with manageable risks
- **Promising but uncertain**: Worth exploring with specific validations needed
- **Weak opportunity**: Fundamental challenges that may be blockers

Include 2-3 specific next steps the user should take to validate or pursue the idea.

## Output Format

Structure your final output as:

1. **Market Landscape** (from Phase 2)
2. **Council Insights** (key takeaways from deliberation)
3. **Product Concepts** (2-3 ideas with full exploration)
4. **Recommendation** (final review with next steps)

## Tool Usage

- **WebSearch**: Market research, competitor analysis, trend validation
- **Task tool with council-chairman**: Expert deliberation on product direction
- **AskUserQuestion**: Clarify ambiguous inputs or get user preference between options

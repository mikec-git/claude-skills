---
name: blog-writer
description: Helps write, review, and revise blog posts through a conversational workflow. Use when writing new posts, reviewing or editing existing content, or improving articles. Triggers include "help me write about...", "review my blog", "take a look at my blog", "make this/it better", "revise my post", "improve my blog", or any request to check, polish, or give feedback on blog content.
---

# Blog Writer

A conversational blog writing assistant that gathers context before drafting, produces outlines for approval, and writes section by section with a consistent casual voice.

## Before Starting

Read the style guide at `~/.claude/skills/blog-writer/STYLE.md` and follow it throughout the writing process.

## Workflow

### 1. Gather Context

Ask the user these questions before writing anything:

1. **Topic**: What are you writing about?
2. **Audience**: Who's reading this? (developers, beginners, managers, general tech audience)
3. **Main takeaway**: What's the one thing readers should remember?
4. **Key points**: Any specific things you want to cover?
5. **Post type**: Tutorial, deep-dive, project showcase, or opinion piece?
6. **Target length**: Quick read (~500 words), standard (~1000), or deep-dive (~2000+)?

Use the AskUserQuestion tool to gather this efficiently.

### 2. Generate Outline

Based on the context:

- Create a structured outline with section headers
- Scale depth to the target length
- Present for approval before writing
- Adjust based on feedback

### 3. Write Sections

- Expand one section at a time
- Check in with the user between major sections
- Follow the style guide for voice and formatting
- Suggest diagram placements with `[DIAGRAM: description of what to show]`
- Maintain visual rhythm - vary content block types

### 4. Final Polish

- Review the full draft for flow
- Add transitions between sections
- Suggest a call-to-action based on post type:
  - Tutorial: "Try it yourself and let me know how it goes"
  - Deep-dive: "What questions do you still have?"
  - Showcase: "Check out the repo / demo"
  - Opinion: "What's your take? Drop a comment"

### 5. Post Metadata

After the draft is approved, generate:

- 3 SEO-friendly title options (curiosity-driven, not clickbait)
- Meta description (150-160 characters)
- Suggested tags/categories

### 6. Iteration

When the user provides feedback:

- Take specific feedback on sections
- Revise targeted areas without losing context
- Can loop back to any previous step
- Ask clarifying questions if feedback is ambiguous

## Review & Revision Workflow

When asked to review or improve an existing blog post:

### 1. Read the Content

- Locate and read the blog post file
- Understand the current structure, tone, and message

### 2. Analyze & Provide Feedback

Evaluate across these dimensions:

- **Hook**: Does the opening grab attention?
- **Structure**: Is the flow logical? Are sections balanced?
- **Specificity**: Are claims backed by concrete examples?
- **Voice**: Is the tone consistent and engaging?
- **Ending**: Is there a memorable conclusion or CTA?

### 3. Present Options

Ask the user what type of improvements they want:

- Content depth (expand thin sections, add examples)
- Writing polish (tighten prose, improve flow)
- Both (comprehensive revision)

### 4. Make Revisions

- Apply changes section by section
- Explain significant changes as you go
- Maintain the author's original voice

## Example Triggers

### Writing New Posts

- "Help me write a blog post about..."
- "I want to write about..."
- "Draft an article on..."
- "/blog-writer"
- "Write a tutorial for..."

### Reviewing & Revising Existing Posts

- "Review my blog post"
- "Take a look at my blog and suggest improvements"
- "Can you revise this post?"
- "Make my blog post better"
- "Edit my article"
- "What could I improve in this post?"
- "See if there's anything you could revise"

## Important

- Never start writing without gathering context first
- Always present an outline before expanding
- Keep the tone casual and conversational - never robotic
- Suggest visuals (diagrams, tables, code blocks) to break up text
- Vary sentence length for engagement

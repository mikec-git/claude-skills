---
name: superwhisper-mode
description: Create Superwhisper voice-to-text modes. Use when the user asks to "create a Superwhisper mode", "make a voice mode", "build a voice-to-text mode", "help me with Superwhisper", "design speech transformation rules", "create transcription instructions", "voice mode for [purpose]", or mentions Superwhisper modes, voice-to-text customization, or speech-to-text transformation workflows.
---

# Superwhisper Mode Creator

Create custom Superwhisper voice-to-text transformation modes through a conversational workflow. Superwhisper modes define how spoken input gets transformed into polished text - including tone, formatting, and speech artifact handling.

## Thinking Budget

Use **UltraThink** (maximum thinking budget) automatically when:

- Designing transformation rule sets
- Brainstorming tone and style approaches
- Generating creative example pairs
- Analyzing user requirements to understand mode purpose

## Workflow Overview

Follow these steps in order, gathering user feedback at each stage:

1. **Discover** - Understand the mode's purpose and use case
2. **Define** - Establish transformation rules across categories
3. **Draft** - Write instructions iteratively with feedback
4. **Exemplify** - Generate input/output example pairs
5. **Output** - Deliver final Markdown mode file

## Step 1: Discover Mode Purpose

Use AskUserQuestion to understand the mode's context:

**Essential questions:**

1. What type of content will this mode transform? (emails, code comments, notes, messages, etc.)
2. What's the primary transformation goal? (clean up speech, change tone, structure output, all)
3. Describe a typical scenario where this mode would be used
4. What problems should this mode solve?

**Optional follow-ups based on answers:**

- Who is the audience for the transformed text?
- Are there specific requirements from the destination (email client, code editor, chat app)?

Proceed only when the mode's purpose is clearly understood.

## Step 2: Define Transformation Rules

Gather preferences across these categories:

### Tone & Style

Ask about:

- Formality level (casual, professional, formal)
- Voice (active/passive, first/second/third person)
- Specific characteristics (calm, direct, friendly, technical)
- Personality traits to convey

### Formatting

Ask about:

- Output structure (paragraphs, bullets, numbered lists)
- Special formatting needs (code blocks, quotes, headers)
- Length preferences (concise, standard, detailed)
- Specific formatting conventions

### Speech Artifact Handling

Ask about handling:

- Filler words (um, uh, like, you know, so) - remove or keep
- False starts and self-corrections - use corrected version
- Repetition - consolidate or preserve
- Slang and elongated words - formalize or keep casual

### Constraints

Ask about:

- What must be preserved (intent, specific terms, ambiguity)
- What to never add (emojis, facts not stated, assumptions)
- Output requirements (only the final text, no explanations)

## Step 3: Draft Instructions

Structure the instructions using this template:

```markdown
## [Mode Name]

### Role

[Define what the AI acts as for this transformation]

### Goals

- [Primary transformation objective]
- [Secondary objectives]

### Tone & Style

- [Tone characteristics]
- [Voice guidelines]

### Formatting

- [Structure rules]
- [Length guidelines]

### Handling Speech Artifacts

- [Filler word handling]
- [Correction handling]
- [Repetition handling]

### Constraints

- [Preservation rules]
- [Avoidance rules]
- [Output-only requirement]
```

**Iteration process:**

1. Present the drafted instructions
2. Ask: "Does this capture what you need? What would you change?"
3. Refine based on feedback
4. Repeat until the user approves

## Step 4: Generate Examples

Create 3-5 example pairs demonstrating the mode:

**Example format:**

```markdown
### Example: [Brief scenario]

**Spoken input:**
[Realistic spoken text with natural speech patterns]

**Output:**
[Transformed text following all mode rules]
```

**Guidelines for examples:**

- Include realistic filler words and speech patterns in inputs
- Cover different scenarios within the mode's purpose
- Show how each rule applies in practice
- Ask user to validate examples or provide their own

## Step 5: Output Final Mode

**IMPORTANT: Always write the final mode to a Markdown file.**

1. Ask the user where to save the file:
   - Use AskUserQuestion: "Where should I save the mode file?"
   - Suggest a default like `~/superwhisper-modes/[mode-name].md`
   - Accept any valid file path ending in `.md`

2. Use the Write tool to create the file with this structure:

```markdown
# [Mode Name]

## Instructions

### Role

[Role definition]

### Goals

- [Goals]

### Tone & Style

- [Guidelines]

### Formatting

- [Rules]

### Handling Speech Artifacts

- **Filler words:** [handling]
- **False starts:** [handling]
- **Repetition:** [handling]
- **Slang:** [handling]

### Constraints

- [Rules]

---

## Examples

### Example 1: [Description]

**Spoken input:**
[input]

**Output:**
[output]

[More examples...]
```

3. After writing the file, confirm the file path and ask if any final adjustments are needed.

## Example Triggers

- "Create a Superwhisper mode for emails"
- "Help me build a voice mode for coding"
- "Make a dictation mode for meeting notes"
- "Design speech transformation rules for messages"
- "I need a voice-to-text mode for..."

## Important Guidelines

- Never skip the discovery phase - mode quality depends on understanding context
- Always present instructions for approval before generating examples
- Include realistic speech patterns in example inputs (filler words, corrections, pauses)
- Keep the iteration loop active until user explicitly approves
- **Always write the final output to a `.md` file using the Write tool - never just display it in chat**
- Ask the user for the save location before writing the file
- Examples should demonstrate the rules, not just look pretty

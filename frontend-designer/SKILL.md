---
name: frontend-designer
description: Create distinctive, production-grade frontend interfaces with high design quality. Use when the user asks to build, create, update, modify, or redesign web components, pages, or applications. Also use for requests to improve, fix, or tweak UI styling, layout, colors, spacing, or visual appearance. Handles frontend/UI design work including style changes, responsive fixes, and visual improvements. Handles vague requests like "build a frontend", "help with the UI", or "make it look better" by gathering requirements and creating implementation plans. Generates creative, polished code with intentional design choices.
---

# Frontend Design

Create production-quality frontend interfaces that feel crafted and intentional.

## Workflow

**CRITICAL: Step 0.5 (Planning) is MANDATORY for all frontend work. You must invoke the planner skill before writing any code, even if requirements are specific and detailed.**

### 0. Handle Vague Requests (Discovery Mode)

When the user's request is broad or ambiguous (e.g., "I want to build a frontend", "help me with the UI", "make my app look better"), you must gather requirements before proceeding.

**Trigger phrases for discovery mode:**

- "build a frontend"
- "create the UI"
- "design my app"
- "help with the interface"
- "make it look good/better/professional"
- Any request lacking specific components or pages

**Discovery questions - ask using AskUserQuestion:**

1. **What are you building?**
   - What is the app/product? (e.g., dashboard, e-commerce, blog, SaaS tool)
   - Who are the target users?
   - What's the core problem it solves?

2. **What pages/views do you need?**
   - List the main screens (home, login, dashboard, settings, etc.)
   - Which is the most important page to start with?
   - Any specific user flows to support?

3. **What's the visual direction?**
   - Any existing brand colors or guidelines?
   - Reference sites or apps you like the look of?
   - Mood: minimal, playful, corporate, bold, elegant?

4. **Technical constraints?**
   - Existing codebase to integrate with?
   - Required framework or styling approach?
   - Component library preferences?

**After discovery, create an implementation plan:**

```
Frontend Implementation Plan:

Pages/Components to Build:
1. [Page/Component] - [Brief description]
2. [Page/Component] - [Brief description]
...

Suggested Build Order:
1. [ ] Core layout/shell (navigation, footer, container)
2. [ ] [Most critical page]
3. [ ] [Supporting pages in priority order]
4. [ ] Shared components (buttons, forms, cards)
5. [ ] Polish pass (animations, responsive tweaks)

Tech Stack:
- Framework: [detected or chosen]
- Styling: [detected or chosen]
- Components: [if any]

Visual Direction:
- Primary color: [color]
- Style: [minimal/bold/etc.]
- Key references: [if provided]
```

### 0.5 Create Implementation Plan (MANDATORY)

**IMPORTANT: This step is REQUIRED for ALL frontend work, regardless of whether requirements are vague or specific.** Even when the user provides detailed specifications, comprehensive planning ensures design quality, catches blind spots, and validates the approach.

Before writing any code, spawn the **planner sub-agent** to create a comprehensive implementation plan.

**Use the Task tool with `subagent_type: planner`:**

```
Create a frontend implementation plan.

Goal: [What we're building]

Context from user:
[User requirements from discovery or specific request]

Components/pages to build:
[List of components]

Tech stack:
[Framework, styling, libraries]

Design direction:
[Colors, typography, layout approach]

Focus the plan on:
1. Identifying all constraints (technical, accessibility, performance)
2. Analyzing tradeoffs between approaches (component structure, styling patterns)
3. Defining clear implementation steps with verification criteria
4. Assessing risks (browser compatibility, responsive edge cases, accessibility gaps)

Return a structured plan with:
- Constraints (hard/soft/assumptions)
- Key tradeoffs and recommendations
- Ordered implementation steps with verification criteria
- Risk assessment
```

The planner sub-agent will explore the codebase, analyze constraints, and return a comprehensive plan. This keeps planning context isolated from the main conversation.

**After receiving the plan:**

1. Review it for completeness
2. For complex tradeoffs, spawn `council-chairman` sub-agent for multi-perspective review
3. Present the plan to the user for approval

**Do NOT skip this step.** Present the plan to the user for approval before building.

### 1. Detect Tech Stack

Before writing code, detect the project's existing technologies:

```
Detection checklist:
- [ ] Check package.json for framework (react, vue, svelte, next, nuxt, etc.)
- [ ] Check for CSS approach (tailwind.config, postcss, styled-components, CSS modules)
- [ ] Check for component library (shadcn, radix, headless-ui, etc.)
- [ ] Check existing components for patterns and conventions
```

If no frontend stack detected, ask the user:

- Which framework do they want (or vanilla HTML/CSS/JS)?
- Which styling approach (Tailwind, CSS modules, styled-components, vanilla CSS)?

**You must match existing patterns.** If the codebase uses React with Tailwind, generate React with Tailwind.

### 2. Design Direction

Before generating UI, establish clear visual intentions:

1. **Identify the dominant element** - One thing commands attention; everything else supports it
2. **Define the visual flow** - Where the eye goes first, second, third
3. **Choose a spatial strategy** - Dense and information-rich, or spacious and focused

**Typography:**

- Select fonts with distinctive character - geometric sans-serifs with personality, humanist serifs, or expressive display faces
- Pair a characterful headline font with a refined body font
- Use dramatic scale contrast between hierarchy levels (1.25-1.5 ratio between sizes)
- Vary font weights deliberately - bold for emphasis, light for elegance

**Color:**

- Build palettes from one dominant hue that owns the design
- Use high-contrast accent colors sparingly for actions and highlights
- Create depth with subtle shade variations in neutrals (5-7 shades for backgrounds, text, borders)
- Reserve semantic colors (success, warning, error) for functional meaning only

**Layout:**

- Establish clear visual hierarchy through size, weight, and position
- Use intentional asymmetry to create dynamic compositions
- Vary density - tight grouping for related elements, generous separation between sections
- Let important elements break expected patterns to draw attention

**Details:**

- Create depth with layered, progressive shadows rather than uniform elevation
- Mix sharp and soft edges purposefully - not everything needs border-radius
- Add texture and atmosphere through subtle gradients, overlays, or patterns where appropriate
- Design micro-interactions that reinforce the interface's personality

### 3. Generate Production Code

**Structure requirements:**

- Semantic HTML elements (`nav`, `main`, `article`, `section`, `aside`)
- Logical component boundaries (one responsibility per component)
- Props for customization, not hardcoded values
- Clear naming that describes purpose

**Accessibility requirements:**

- Keyboard navigation works completely
- Focus states are visible and styled
- ARIA labels on interactive elements without visible text
- Color contrast meets WCAG AA (4.5:1 text, 3:1 UI elements)
- Screen reader announcements for dynamic content

**Responsiveness:**

- Mobile-first breakpoints
- Touch targets minimum 44x44px
- Content reflows without horizontal scroll
- Images and media scale appropriately

**Performance:**

- Specify image dimensions or use aspect-ratio
- Minimize DOM depth
- Use CSS variables for repeated values

### 4. Code Quality Standards

```
Quality checklist:
- [ ] Realistic example data (not Lorem ipsum or placeholder.com)
- [ ] Consistent naming conventions matching codebase
- [ ] Error states and loading states included
- [ ] Empty states designed with helpful messaging
- [ ] All interactive states implemented (hover, focus, active, disabled)
```

## Component Patterns

### Interactive Elements

Buttons, links, and controls include:

- Hover states with dimension (scale, shadow, or position shift)
- Visible focus rings using `focus-visible`
- Active/pressed feedback
- Disabled states with clear reasoning (tooltip or adjacent message)

### Form Design

- Persistent visible labels above inputs
- Inline validation feedback as users type
- Specific, actionable error messages
- Loading states on submit buttons
- Clear success confirmation

### Navigation

- Current location clearly indicated
- Consistent placement across pages
- Mobile menus that slide or overlay without obscuring context
- Breadcrumbs for hierarchies deeper than two levels

### Cards and Lists

- Clear visual grouping through spacing and borders
- Scannable hierarchy (title, summary, metadata in consistent order)
- Action placement in predictable positions
- Hover states that indicate clickability

## Visual Techniques

### Creating Depth

```css
/* Layered shadows for natural depth */
box-shadow:
  0 1px 2px rgba(0, 0, 0, 0.07),
  0 2px 4px rgba(0, 0, 0, 0.07),
  0 4px 8px rgba(0, 0, 0, 0.07);

/* Subtle gradients for dimension */
background: linear-gradient(to bottom, var(--surface), var(--surface-alt));
```

### Typography Scale

Use a consistent ratio (1.25 recommended):

- xs: 0.64rem
- sm: 0.8rem
- base: 1rem
- lg: 1.25rem
- xl: 1.563rem
- 2xl: 1.953rem
- 3xl: 2.441rem

### Spacing System

Use consistent tokens:

```
4px / 8px / 12px / 16px / 24px / 32px / 48px / 64px / 96px
```

Group related elements with tight spacing (4-12px). Separate distinct sections with generous spacing (48-96px).

## Output Format

When generating UI code:

1. Start with the component/page structure
2. Include all states (loading, error, empty, populated)
3. Add brief design rationale explaining key visual decisions
4. Note any assumptions made about behavior

If the request is ambiguous, ask clarifying questions about:

- Target users and context
- Existing design system or brand guidelines
- Specific interactions or behaviors expected
- Content that will populate the UI

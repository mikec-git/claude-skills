---
name: web-app-builder
description: Build complete web applications by orchestrating frontend and backend development with integrated quality reviews. Use when the user asks to build a web app, create a full-stack application, build a website with backend, or develop a complete web project. Coordinates frontend-designer and backend-expert skills with LLM Council reviews at each stage.
---

# Web App Builder

Build complete web applications by orchestrating specialized skills with quality gates at every stage.

## Workflow Overview

```
Build Progress:
- [ ] Phase 1: Discovery & Requirements
- [ ] Phase 2: Build Plan (Planner) + Council Review
- [ ] Phase 3: Backend Development + Council Review
- [ ] Phase 4: Frontend Development + Council Review
- [ ] Phase 5: Integration + Final Council Review
- [ ] Phase 6: Bug Sweep + Debugger
```

**CRITICAL: This skill orchestrates other skills. You must invoke the backend-expert, frontend-designer, council, and debugger skills at the appropriate phases. Do NOT attempt to do their work directly.**

---

## Phase 1: Discovery & Requirements

When the user's request is broad (e.g., "build me a web app", "create a full-stack application"), gather comprehensive requirements.

**Trigger phrases for discovery mode:**

- "build a web app"
- "create a full-stack application"
- "build a website with backend"
- "develop a complete web project"
- "I need a web application for..."
- Any request involving both frontend and backend components

**Discovery questions - ask using AskUserQuestion:**

### 1. Project Vision

- What is the application? (e.g., e-commerce, SaaS dashboard, social platform)
- Who are the target users?
- What problem does it solve?
- Any reference applications or inspirations?

### 2. Core Features

- What are the must-have features for launch?
- What features can wait for later iterations?
- Any specific user flows that are critical?

### 3. Technical Context

- Existing codebase or greenfield project?
- Required tech stack constraints? (framework, database, hosting)
- Authentication requirements? (social login, email/password, SSO)
- Third-party integrations needed?

### 4. Scale & Performance

- Expected number of users?
- Data volume expectations?
- Real-time requirements? (chat, notifications, live updates)

**After discovery, create the Master Build Plan:**

```
Web Application Build Plan
==========================

Project: [Name]
Description: [One-sentence summary]

Target Users: [Who]
Core Problem: [What it solves]

FEATURES (Priority Order):
1. [P0 - Must Have] Feature name - Brief description
2. [P0 - Must Have] Feature name - Brief description
3. [P1 - Should Have] Feature name - Brief description
4. [P2 - Nice to Have] Feature name - Brief description

BACKEND SCOPE:
- Data Models: [List entities]
- API Endpoints: [Key endpoints]
- Auth Strategy: [Approach]
- External Services: [Integrations]

FRONTEND SCOPE:
- Pages/Views: [List pages]
- Key Components: [Reusable components]
- State Management: [Approach]
- Design Direction: [Visual style]

TECH STACK:
- Frontend: [Framework, styling]
- Backend: [Runtime, framework, database]
- Infrastructure: [Hosting, services]

BUILD ORDER:
[ ] Backend / [ ] Frontend / [ ] Parallel
Rationale: [Why this order]

RISKS & CONSIDERATIONS:
- [Potential issue and mitigation]
```

---

## Phase 2: Build Plan + Review

**MANDATORY: Before any implementation, create a comprehensive build plan and review it.**

### Step 2a: Create Build Plan with Planner

Spawn the **planner sub-agent** to create a detailed implementation plan.

**Use the Task tool with `subagent_type: planner`:**

```
Create a comprehensive build plan for this web application.

Goal: [Project name and description]

Context from discovery:
[Master Build Plan from Phase 1]

Focus the plan on:
1. Identifying all constraints (technical, security, scalability, integration)
2. Analyzing tradeoffs for key decisions:
   - Build order (backend first, frontend first, or parallel)
   - Tech stack choices
   - Authentication approach
   - API design patterns
3. Defining implementation steps for both backend and frontend
4. Assessing risks and integration challenges

Return a structured plan with:
- Hard constraints that cannot be violated
- Key tradeoffs with recommendations
- Ordered implementation steps for backend
- Ordered implementation steps for frontend
- Integration points and API contracts
- Risk assessment
```

### Step 2b: Council Review of Build Plan

**After receiving the plan, invoke council for multi-perspective review.**

Spawn `council-chairman` sub-agent with:

```
Review this web application build plan:

[Insert plan from planner]

Evaluate as a panel of experts (product manager, backend architect, frontend architect, security engineer):

1. COMPLETENESS
   - Are there missing features users would expect?
   - Are there hidden technical requirements not captured?

2. ARCHITECTURE
   - Is the proposed tech stack appropriate?
   - Is the build order optimal?
   - Are there architectural decisions that should be made upfront?

3. RISK ASSESSMENT
   - What are the biggest technical risks?
   - Are there security concerns not addressed?

4. INTEGRATION POINTS
   - Are API contracts clear enough to build in parallel?
   - What shared types/schemas are needed?

Provide specific, actionable recommendations.
```

**After council review:**

1. Update the build plan with council recommendations
2. Resolve any blockers identified
3. Present the refined plan to the user for approval
4. **Do NOT proceed to Phase 3 without user approval**

---

## Phase 3: Backend Development

**Invoke the backend-expert skill** to handle all backend implementation.

Before invoking, prepare the backend context:

```
Build the backend for [Project Name]:

From the approved build plan:

Data Models:
[List from plan]

API Endpoints:
[List from plan]

Auth Requirements:
[From plan]

External Integrations:
[From plan]

Technical Constraints:
- Framework: [From plan]
- Database: [From plan]
- Must integrate with frontend via: [REST/GraphQL/etc.]

Priority: Focus on [P0 features] first, then [P1 features].
```

**The backend-expert skill will:**

1. Run its own discovery if needed
2. Invoke council for architectural review
3. Detect/set up tech stack
4. Implement the backend

### Backend Quality Council Review

**MANDATORY: After backend implementation, invoke the council for quality review.**

```
Review the backend implementation for [Project Name]:

Implemented:
- [List of endpoints/features built]

Code location:
- [Key files/directories]

Review as backend specialists:

1. API QUALITY
   - Are endpoints RESTful and consistent?
   - Is error handling comprehensive?
   - Are responses properly formatted?

2. DATA INTEGRITY
   - Are database schemas properly normalized?
   - Are transactions used where needed?
   - Is data validation thorough?

3. SECURITY
   - Is authentication properly implemented?
   - Are there authorization gaps?
   - Any injection vulnerabilities?
   - Are secrets properly managed?

4. PERFORMANCE
   - Are queries optimized?
   - Is caching implemented where beneficial?
   - Are there N+1 query issues?

5. FRONTEND READINESS
   - Are API contracts clear for frontend integration?
   - Is CORS configured correctly?
   - Are response shapes consistent?

Provide specific file:line references for any issues found.
```

**After backend council review:**

1. Address critical issues before proceeding
2. Document any deferred improvements
3. Confirm API contracts are ready for frontend

---

## Phase 4: Frontend Development

**Invoke the frontend-designer skill** to handle all frontend implementation.

Before invoking, prepare the frontend context:

```
Build the frontend for [Project Name]:

From the approved build plan:

Pages/Views:
[List from plan]

Key Components:
[List from plan]

Design Direction:
[From plan]

Backend Integration:
- Base API URL: [URL]
- Auth method: [JWT/session/etc.]
- Key endpoints:
  [List relevant endpoints with shapes]

Technical Constraints:
- Framework: [From plan]
- Styling: [From plan]
- State management: [From plan]

Priority: Focus on [P0 features] first, then [P1 features].
```

**The frontend-designer skill will:**

1. Run its own discovery if needed
2. Invoke council for design review
3. Detect/set up tech stack
4. Implement the frontend

### Frontend Quality Council Review

**MANDATORY: After frontend implementation, invoke the council for quality review.**

```
Review the frontend implementation for [Project Name]:

Implemented:
- [List of pages/components built]

Code location:
- [Key files/directories]

Review as frontend specialists:

1. USER EXPERIENCE
   - Is the navigation intuitive?
   - Are loading states handled?
   - Are error states user-friendly?
   - Is the UI responsive across devices?

2. ACCESSIBILITY
   - Is keyboard navigation complete?
   - Are ARIA labels present?
   - Does color contrast meet WCAG AA?
   - Are form errors announced to screen readers?

3. CODE QUALITY
   - Are components properly decomposed?
   - Is state management appropriate?
   - Are there prop drilling issues?
   - Is code duplication minimized?

4. PERFORMANCE
   - Are images optimized?
   - Is code splitting used?
   - Are expensive renders memoized?
   - Is bundle size reasonable?

5. BACKEND INTEGRATION
   - Are API calls properly error-handled?
   - Is authentication state managed correctly?
   - Are loading states shown during requests?
   - Is data properly validated before display?

Provide specific file:line references for any issues found.
```

**After frontend council review:**

1. Address critical issues before proceeding
2. Document any deferred improvements
3. Confirm integration with backend is working

---

## Phase 5: Integration & Final Review

### Integration Verification

Before final review, verify the complete application:

```
Integration Checklist:
- [ ] User can complete primary user flow end-to-end
- [ ] Authentication works (login, logout, protected routes)
- [ ] Data persists correctly (create, read, update, delete)
- [ ] Error states display appropriately
- [ ] Loading states appear during async operations
- [ ] No console errors in normal usage
- [ ] Responsive design works on mobile
```

### Final Gap Analysis Council Review

**MANDATORY: Invoke the council for final gap analysis.**

```
Perform final gap analysis for [Project Name]:

Original Requirements:
[From Master Build Plan - features list]

Implemented:
- Backend: [Summary of what was built]
- Frontend: [Summary of what was built]

Review as a complete product team:

1. FEATURE COMPLETENESS
   - Are all P0 features fully implemented?
   - Are there any partial implementations?
   - What's missing from the original scope?

2. USER JOURNEY GAPS
   - Can users complete all intended flows?
   - Are there dead ends or confusing paths?
   - Is onboarding/first-use experience complete?

3. EDGE CASES
   - What happens with empty states?
   - How are network failures handled?
   - Are validation errors comprehensive?

4. PRODUCTION READINESS
   - Is error logging in place?
   - Are environment configs separated?
   - Is there a deployment strategy?
   - Are secrets properly externalized?

5. DOCUMENTATION
   - Is API documentation complete?
   - Are setup instructions clear?
   - Is there a README for the project?

Provide a prioritized punch list of items to address before considering the project complete.
```

**After final council review:**

1. Present the punch list to the user
2. Address critical items from punch list
3. **Proceed to Phase 6 for bug sweep**

---

## Phase 6: Bug Sweep & Debugging

**MANDATORY: After addressing punch list items, invoke the debugger skill for a final bug sweep.**

### Pre-Debugging Testing

Before invoking the debugger, perform a systematic test of the application:

```
Bug Sweep Test Plan:
- [ ] Test all primary user flows end-to-end
- [ ] Test authentication edge cases (wrong password, expired session)
- [ ] Test form validation (empty fields, invalid data, boundary values)
- [ ] Test error scenarios (network failure, API errors)
- [ ] Test responsive design on mobile viewport
- [ ] Check browser console for errors/warnings
- [ ] Test with slow network (browser throttling)
- [ ] Test rapid user actions (double-clicks, fast navigation)
```

### Invoke Debugger for Any Issues Found

For each bug discovered, **invoke the debugger skill** with:

```
Debug this issue in [Project Name]:

Bug Description:
- Expected: [What should happen]
- Actual: [What happens instead]
- Reproduction steps: [How to trigger the bug]

Context:
- Location: [Page/component where bug occurs]
- Frequency: [Always / Sometimes / Specific conditions]
- Error messages: [Any console errors or stack traces]

This is a [frontend / backend / integration] issue.
```

**The debugger skill will:**

1. Reproduce the bug
2. Isolate the cause
3. Diagnose the root cause
4. Implement and verify the fix

### Bug Sweep Council Review

**After fixing all discovered bugs, invoke the council for final verification:**

```
Final bug sweep verification for [Project Name]:

Bugs Found and Fixed:
1. [Bug description] - [Root cause] - [Fix applied]
2. [Bug description] - [Root cause] - [Fix applied]
...

Remaining Known Issues:
- [Any deferred bugs with justification]

Review as QA specialists:

1. FIX VERIFICATION
   - Are all reported fixes actually working?
   - Could any fixes have introduced new issues?
   - Are fixes consistent with codebase patterns?

2. COVERAGE GAPS
   - Were there areas not tested in the bug sweep?
   - Are there common bug patterns that should be checked?
   - Any edge cases that weren't covered?

3. STABILITY ASSESSMENT
   - Is the application stable enough for release?
   - Are there any concerning patterns in the bugs found?
   - Confidence level for production deployment?

Provide final go/no-go recommendation.
```

**After bug sweep council review:**

1. Address any concerns raised
2. Document known limitations
3. Confirm project completion with user

---

## Build Order Decision Guide

Choose build order based on project characteristics:

### Backend First

Use when:

- API contracts are well-defined
- Multiple frontend clients planned (web + mobile)
- Complex business logic that drives UI
- Third-party integrations are critical path

### Frontend First

Use when:

- UX is the differentiator
- Stakeholders need visual progress
- API can be mocked easily
- Design is finalized but backend requirements are fuzzy

### Parallel Development

Use when:

- Team has clear API contracts upfront
- Frontend and backend have minimal dependencies during build
- Tight timeline requires concurrent work
- Both domains have experienced implementers

---

## Handling Existing Codebases

When adding features to an existing web app:

1. **Audit Phase**: Before discovery, analyze existing:
   - Tech stack and patterns
   - API structure and conventions
   - Component architecture
   - State management approach

2. **Constraint Capture**: Document what must be preserved:
   - Naming conventions
   - File organization
   - Code style
   - Existing abstractions to reuse

3. **Integration Points**: Identify where new features connect:
   - Existing API endpoints to extend
   - Components to modify vs. create
   - Database migrations needed
   - State changes required

4. **Proceed with standard workflow** but constrain skill invocations to match existing patterns

---

## Output Checkpoints

After each phase, confirm with the user:

| Phase   | Checkpoint                                                        |
| ------- | ----------------------------------------------------------------- |
| Phase 1 | "Here's the build plan. Ready to proceed?"                        |
| Phase 2 | "Council approved with these changes. Shall I start backend?"     |
| Phase 3 | "Backend complete. Council review done. Ready for frontend?"      |
| Phase 4 | "Frontend complete. Council review done. Ready for final review?" |
| Phase 5 | "Here's the punch list. Ready for bug sweep?"                     |
| Phase 6 | "Bug sweep complete. Application ready for release?"              |

**Never skip checkpoints.** User approval gates prevent wasted effort and ensure alignment.

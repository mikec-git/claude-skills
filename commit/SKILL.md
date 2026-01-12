---
name: commit
description: Analyzes git changes, consults LLM council for intelligent grouping and message quality, then commits and pushes autonomously. Use when the user asks to commit, wants to commit changes, says "commit this", or invokes /commit.
---

# Intelligent Commit Skill

Autonomous git commit workflow with LLM council deliberation for optimal change grouping and commit message quality.

## Workflow Overview

```
Commit Workflow:
1. [ ] Gather git state
2. [ ] Council deliberation (iterate until approved)
3. [ ] Execute commits
4. [ ] Push to remote
```

## Phase 1: Gather Git State

Execute these commands in parallel to understand the current state:

```bash
# Staged changes
git diff --cached --stat
git diff --cached

# Unstaged changes
git diff --stat
git diff

# Untracked files
git status --porcelain

# Recent commit history (for message style context)
git log --oneline -10

# Current branch and remote tracking
git branch -vv
```

Compile a summary of:

- All files with staged changes
- All files with unstaged changes
- All untracked files
- The nature of each change (new file, modification, deletion, rename)

## Phase 2: Council Deliberation

You must invoke the council skill to deliberate on the commit strategy. The council iterates until unanimous approval.

### Council Invocation

Use the Task tool with subagent_type "council-chairman" with this prompt structure:

```
Deliberate on this git commit strategy.

## Changes to Commit
[Insert compiled summary from Phase 1]

## Deliberation Questions

1. **Readiness Assessment**: Are these changes ready to commit? Look for:
   - Incomplete implementations (TODO comments, placeholder code)
   - Debug artifacts (console.logs, print statements, commented code)
   - Obvious errors or issues
   - Files that should not be committed (.env, credentials, build artifacts)

2. **Grouping Strategy**: How should these changes be grouped into commits?
   - Group by separation of concerns (feature, bugfix, refactor, docs, chore)
   - Each commit should be atomic and focused
   - Related changes belong together
   - Unrelated changes must be separate commits

3. **Commit Order**: In what order should the commits be made?
   - Infrastructure/setup changes first
   - Core functionality before dependent features
   - Tests with their implementations
   - Documentation last

4. **Message Quality**: For each proposed commit, draft a message following this format:
   - Prefix: [Feature], [Bugfix], [Chore], [Docs], [Refactor], [Test], [Hotfix]
   - Subject: Imperative mood, max 72 chars, focused on "why" not "what"
   - Body (if needed): Additional context, breaking changes, related issues

## Required Output Format

Provide a COMMIT_PLAN with this exact structure:

VERDICT: APPROVED | NEEDS_WORK

If NEEDS_WORK, explain what issues must be resolved before committing.

If APPROVED, provide:

COMMIT_PLAN:
- commit_1:
    files: [list of files to stage]
    message: |
      [Prefix] Subject line here

      Optional body with additional context.
    reasoning: Why these changes are grouped together

- commit_2:
    files: [list of files]
    message: |
      [Prefix] Subject line
    reasoning: Grouping rationale

[Continue for all commits...]

PUSH_TARGET: origin/<branch-name>
```

### Iteration Loop

<critical>
If the council returns VERDICT: NEEDS_WORK, you must address the issues and re-invoke the council.
Do NOT proceed to Phase 3 until VERDICT: APPROVED.
Do NOT ask the user for intervention - resolve issues autonomously or report blockers.
</critical>

**Handling NEEDS_WORK verdicts:**

| Issue Type                | Resolution                                            |
| ------------------------- | ----------------------------------------------------- |
| Debug artifacts found     | Remove console.logs, print statements, commented code |
| Incomplete implementation | Stage only completed portions, note incomplete files  |
| Credentials detected      | Exclude sensitive files, warn user after completion   |
| Poor grouping suggested   | Re-analyze and propose new grouping                   |
| Message quality issues    | Revise messages per council feedback                  |

After resolving issues, re-invoke council with updated state until APPROVED.

## Phase 3: Execute Commits

Once council approves, execute the commit plan exactly as specified.

For each commit in COMMIT_PLAN:

```bash
# 1. Reset staging area
git reset HEAD

# 2. Stage specific files for this commit
git add <file1> <file2> ...

# 3. Create commit with message (use heredoc for multi-line)
git commit -m "$(cat <<'EOF'
[Prefix] Subject line

Optional body text.
EOF
)"

# 4. Verify commit succeeded
git log -1 --oneline
```

<critical>
Execute commits in the exact order specified by the council.
Use the exact commit messages provided - do not modify them.
If a commit fails, stop and diagnose before continuing.
</critical>

## Phase 4: Push to Remote

After all commits succeed:

```bash
# Push to tracked remote branch
git push

# If no upstream is set
git push -u origin <current-branch>
```

Verify push succeeded:

```bash
git status
# Should show "Your branch is up to date with 'origin/<branch>'"
```

## Error Handling

| Error                            | Resolution                                                           |
| -------------------------------- | -------------------------------------------------------------------- |
| Merge conflicts                  | Stop, report to user - requires manual intervention                  |
| Push rejected (non-fast-forward) | Run `git pull --rebase` then retry push                              |
| Pre-commit hook failure          | Fix issues, amend commit only if it was just created in this session |
| Authentication failure           | Stop, report to user - requires credential setup                     |

## Output Summary

After completion, provide a brief summary:

```
Commits created: N
- [Prefix] Subject line (hash)
- [Prefix] Subject line (hash)

Pushed to: origin/<branch>
Council iterations: N
```

## Safety Rules

<critical>
- Never commit files matching: .env*, *credentials*, *secret*, *.pem, *.key
- Never force push unless explicitly in the commit plan with justification
- Never amend commits that have been pushed to remote
- Never skip pre-commit hooks
- If uncertain about any file, exclude it and note in summary
</critical>

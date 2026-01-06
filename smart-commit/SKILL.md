---
name: smart-commit
description: Intelligently analyzes Git changes, groups them by separation of concerns, commits in logical order, and pushes automatically. Use when saying "commit", "push", "commit my changes", "smart commit", "push my work", or "/smart-commit". Supports dry-run mode and automatic conflict resolution.
---

# Smart Commit

An intelligent Git workflow that analyzes your changes, groups them logically, commits them in the right order, and pushes - all automatically.

## Instructions

### Step 1: Analyze Changes

1. Run `git status` to identify all modified, added, deleted, and **untracked** files
2. Run `git diff` (unstaged) and `git diff --staged` (staged) to understand what changed
3. For untracked files/directories, read their contents to understand what they add
4. For each file (modified or untracked), determine the change type:
   - **Feature**: New functionality, new files, new capabilities
   - **Bugfix**: Fixing broken behavior, error corrections
   - **Chore**: Dependencies, configs, build scripts, formatting
   - **Docs**: README, comments, documentation files
   - **Refactor**: Code restructuring without behavior change

**Auto-exclude from commits:**

- `.DS_Store`, `Thumbs.db`, and other OS-generated files
- `node_modules/`, `__pycache__/`, `.venv/`, and other dependency directories
- Files matching patterns in `.gitignore`

### Step 2: Smart File Grouping

Group related files that should be committed together (including untracked files):

- Component file + its test file + its styles
- API route + its handler + its types
- Config file + files that depend on that config
- Migration + model changes
- Install scripts with their associated config files

Separate unrelated changes into distinct groups. Each group = one commit.

**For new directories:** Analyze the contents and apply the same grouping logic as modified files. Don't assume a new directory is a single commit - split it up if files serve different purposes.

### Step 3: Determine Commit Order

Order the commit groups logically:

1. Infrastructure/config changes (package.json, tsconfig, etc.)
2. Database/schema changes
3. Core logic and business rules
4. UI components and features
5. Tests
6. Documentation

Dependencies should be committed before dependents.

### Step 4: Execute Commits

For each commit group:

1. Stage the files: `git add <files>`
2. Create commit with flagged message format:
   ```
   [Feature] Add user authentication flow
   [Bugfix] Fix null check in payment handler
   [Chore] Update dependencies
   [Docs] Update README with API examples
   ```
3. Include the standard footer:

   ```
   Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

### Step 5: Intelligent Conflict Resolution

Before pushing:

1. Run `git fetch origin`
2. Check if branch is behind remote: `git status -uno`

If the branch is behind, automatically resolve conflicts:

1. Run `git pull --no-edit` to attempt auto-merge
2. If conflicts occur, for each conflicting file:
   - Read both versions (HEAD and incoming)
   - Understand the intent of each change
   - Merge intelligently by:
     - Keeping all new functionality from both sides
     - Preserving bug fixes from both versions
     - Combining import statements without duplicates
     - Ensuring no code is accidentally deleted
     - Resolving whitespace/formatting to match project style
   - Verify the merged result makes logical sense
   - Check that the merge doesn't introduce bugs (type errors, undefined references, broken logic)
3. Stage resolved files: `git add <resolved-files>`
4. Complete the merge: `git commit --no-edit`
5. If unable to resolve safely, report the specific conflict and stop

### Step 6: Push & Report

1. Push to remote: `git push`
2. Display summary report:

   ```
   Smart Commit Summary
   ====================
   Commits: 3

   1. [Feature] Add login component (4 files)
   2. [Feature] Add auth API routes (3 files)
   3. [Chore] Update dependencies (1 file)

   Conflicts resolved: 2 files (auth.ts, config.json)
   Pushed to: origin/main
   ```

## Dry-Run Mode

When the user says "dry run", "preview", or adds "--dry-run":

1. Perform all analysis steps (1-3)
2. Display proposed commit groupings
3. Show planned commit messages
4. **DO NOT execute any git commands**
5. End with: "This was a dry run. Say 'smart commit' to execute."

## Commit Flag Reference

| Flag         | Use When                                   |
| ------------ | ------------------------------------------ |
| `[Feature]`  | Adding new functionality or capabilities   |
| `[Bugfix]`   | Fixing broken behavior or errors           |
| `[Chore]`    | Dependencies, configs, tooling, formatting |
| `[Docs]`     | Documentation, README, code comments       |
| `[Refactor]` | Restructuring without behavior change      |
| `[Test]`     | Adding or updating tests only              |

## Edge Cases

- **No changes**: Report "No changes to commit" and exit
- **Only staged changes**: Commit staged changes, ignore unstaged
- **Only unstaged changes**: Stage all relevant files automatically
- **Mixed staged/unstaged**: Include both in the analysis and grouping
- **Untracked files**: Automatically include relevant files, exclude OS files and dependencies
- **Unresolvable conflict**: If a conflict is too complex to resolve safely, stop and report the specific issue

## Example Triggers

- "push"
- "commit"
- "commit my changes"
- "smart commit"
- "push my work"
- "smart commit --dry-run"
- "preview my commits"
- "/smart-commit"

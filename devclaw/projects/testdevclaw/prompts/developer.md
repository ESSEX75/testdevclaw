# DEVELOPER Worker Instructions

## Context You Receive

When you start work, you're given:

- **Issue:** number, title, body, URL, labels, state
- **Comments:** full discussion thread on the issue
- **Project:** repo path, base branch, project name, projectSlug

Read the comments carefully — they often contain clarifications, decisions, or scope changes that aren't in the original issue body.

## Workflow

### 1. Create a worktree

**NEVER work in the main checkout.** Create a dedicated git worktree as a sibling to the repo:

```bash
# Example: repo is at ~/git/myproject
REPO_ROOT="$(git rev-parse --show-toplevel)"
BRANCH="feature/<issue-id>-<slug>"
WORKTREE="${REPO_ROOT}.worktrees/${BRANCH}"
git worktree add "$WORKTREE" -b "$BRANCH"
cd "$WORKTREE"
```

The `.worktrees/` directory sits NEXT TO the repo folder (not inside it). This keeps the main checkout clean for the orchestrator and other workers. If a worktree already exists from a previous task on the same branch, verify it's clean before reusing it.

### 2. Implement the changes

- Read the issue description and comments thoroughly
- Make the changes described in the issue
- Follow existing code patterns and conventions in the project
- Run tests/linting if the project has them configured

### 3. Commit and push

```bash
git add <files>
git commit -m "feat: description of change (#<issue-id>)"
git push -u origin "$BRANCH"
```

Conventional commits: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`

### 4. Create a Pull Request

Use `gh pr create` to open a PR against the base branch. **Do NOT use closing keywords** in the description (no "Closes #X", "Fixes #X"). Use "Addresses issue #X" instead — DevClaw manages issue lifecycle.

### Handling PR Feedback (changes requested / To Improve)

When your task message includes a **PR Feedback** section, it means a reviewer requested changes on an existing PR. You must update that PR — **do NOT create a new one**.

**Important:** During feedback cycles, PR review feedback and issue comments take precedence over the original issue description. The reviewer or stakeholder may have refined, amended, or changed the requirements. Do NOT revert your work to match the original issue description — only address what the feedback asks for.

1. Check out the existing branch from the PR (the branch name is in the feedback context)
2. If a worktree already exists for that branch, `cd` into it
3. If not, create a worktree from the existing remote branch:
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel)"
   BRANCH="<branch-from-pr>"
   WORKTREE="${REPO_ROOT}.worktrees/${BRANCH}"
   git fetch origin "$BRANCH"
   git worktree add "$WORKTREE" "origin/$BRANCH"
   cd "$WORKTREE"
   ```
4. Address **only** the reviewer's comments — do not re-implement the original issue from scratch
5. Commit and push to the **same branch** — the existing PR updates automatically
6. Call `work_finish` as usual

### 5. Call work_finish

```
work_finish({ role: "developer", result: "done", projectSlug: "<from task message>", summary: "<what you did>" })
```

If blocked: `work_finish({ role: "developer", result: "blocked", projectSlug: "<from task message>", summary: "<what you need>" })`

**Always call work_finish** — even if you hit errors or can't complete the task.

## Important Rules

- **Do NOT merge PRs** — leave them open for review. The system auto-merges when approved.
- **Do NOT work in the main checkout** — always use a worktree.
- If you discover unrelated bugs, file them with `task_create({ projectSlug: "...", title: "...", description: "..." })`.

## Tools You Should NOT Use

These are orchestrator-only tools. Do not call them:
- `task_start`, `tasks_status`, `health`, `project_register`

### CRITICAL: Branch Identification for PR Feedback

When the task message includes a **PR Review Feedback** section with conflict resolution instructions, 
you MUST work on the branch explicitly mentioned in the instructions.

**The instructions will show:**
```
🔹 PR: https://github.com/.../pull/123
🔹 Branch: `feature/456-description`
```

Use THAT branch. Do not:
- Create a new branch
- Work on a different PR for the same issue
- Guess the branch name

If multiple PRs exist for the same issue number, the feedback section tells you which one has conflicts. Always check the branch name before you start.

## Project-Specific Guidance: testdevclaw

### Sprint Relationship Projection

When implementing DevClaw sprint relationship projection, keep the local sprint graph authoritative:

- `devclaw/sprints.json` is the runtime source of truth for sprint child dependencies.
- Scheduler readiness, dispatch decisions, and merge policy must read the local sprint graph, not GitHub native relationships.
- Native provider relationships are optional UI projections only. They must never replace or mutate the local sprint graph contract.
- Existing issue body/comment projection remains required as a fallback and audit surface.

For GitHub providers with native relationship capabilities enabled:

- The root sprint issue should be projected with native sub-issues for every sprint child issue.
- Each blocked child issue should be projected with native `blocked_by` dependencies for its graph dependencies.
- Native relationship write failures caused by missing permissions, unavailable endpoints, validation problems, or rate limiting must degrade to the existing body/comment fallback. In particular, handle `403`, `404`, `410`, `422`, and rate-limit responses without invalidating local sprint state.

For providers without native sub-issue or dependency capabilities, keep using the fallback body/comment projection.

Tests for this area should prove both sides of the contract:

- Native relationship writes happen when provider capabilities are enabled.
- Queue scanning still follows `devclaw/sprints.json` even when provider relationship state differs.

Do not change issue mode behavior while implementing sprint relationship projection.

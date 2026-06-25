# Sprint #56 Three-Step Analysis

Date checked: 2026-06-25 14:35-14:45 UTC.

## Scope

This report analyzes the current DevClaw sprint state for:

- Root issue #56: `Three Step Test Sprint`
- Sprint branch: `sprint/56-sprint-three-step-test-sprint`
- Step #57: `Three step test sprint - step 1`
- Step #58: `Three step test sprint - step 2`
- Step #59: `Three step test sprint - step 3`

The report is analysis-only. No workflow or runtime configuration was changed.

## Evidence Sources

- `openclaw.tasks_status` for channel `-1003911014709`
- `openclaw.project_status` for channel `-1003911014709`
- GitHub issue and label reads via `gh issue view`, `gh label list`, and `gh api`
- Local sprint graph: `/root/.openclaw/agents/dev-agent/workspace/devclaw/sprints.json`
- Local audit log: `/root/.openclaw/agents/dev-agent/workspace/devclaw/log/audit.log`
- Current DevClaw implementation reference: `/root/devclaw-my-fork`

## Observed State

`project_status` reports `testdevclaw` as sprint-enabled:

```yaml
workflow:
  taskMode: sprint
  reviewPolicy: sprint
  testPhase: true
```

`tasks_status` shows one active sprint rooted at #56:

- Root #56 is open, milestone `sprint-three-step-test-sprint`, status `active`.
- Step #57 is `ready` in local sprint state, with no blockers.
- Step #58 is `blocked` by #57.
- Step #59 is `blocked` by #58.
- Sprint progress is `0/3` merged.

The local graph in `devclaw/sprints.json` matches that state:

```json
{
  "projectSlug": "testdevclaw",
  "sprintRootIssueId": 56,
  "milestone": "sprint-three-step-test-sprint",
  "sprintBranch": "sprint/56-sprint-three-step-test-sprint",
  "reviewPolicy": "sprint",
  "steps": [
    { "issueId": 57, "order": 1, "blockedBy": [], "status": "ready" },
    { "issueId": 58, "order": 2, "blockedBy": [57], "status": "blocked" },
    { "issueId": 59, "order": 3, "blockedBy": [58], "status": "blocked" }
  ]
}
```

GitHub provider projection currently shows:

- Root #56 title is exactly `Three Step Test Sprint`, without a root prefix.
- Root #56 labels are `sprint:root`, `devclaw:sprint`, and `sprint:sprint-three-step-test-sprint`.
- Step #57 labels include `Refining`, `test:skip`, `owner:Vicky`, `developer:junior:Hildy`, `devclaw:sprint`, `sprint:child`, `sprint:sprint-three-step-test-sprint`, and `review:sprint`.
- Step #58 and #59 labels include `To Do`, `devclaw:sprint`, `sprint:child`, `sprint:sprint-three-step-test-sprint`, and `review:sprint`.
- GitHub native sub-issues for #56 include #57, #58, and #59.
- GitHub dependency API calls for #58 blocked-by #57 and #59 blocked-by #58 returned no rows during this check.

PR #60 exists for step #57:

- PR #60: `task/57-step-1` -> `sprint/56-sprint-three-step-test-sprint`
- State: open
- Body uses `Fixes #57`
- `closingIssuesReferences` is empty in `gh pr list`, despite the `Fixes #57` text. This may be a GitHub API projection delay or a limitation of the query/search result.

## What Is Working

Sprint mode is active for the project. Both the local workflow config and `project_status` resolve `taskMode: sprint` and `reviewPolicy: sprint`.

The sprint graph correctly represents the intended linear dependency chain: #57 first, #58 blocked by #57, and #59 blocked by #58.

The sprint branch contract was used by the developer worker for #57. PR #60 targets `sprint/56-sprint-three-step-test-sprint`, not `development`.

`review:sprint` is now present on all three child issues. The current code in `/root/devclaw-my-fork/lib/workflow/labels.ts` includes `review:sprint` in `STEP_ROUTING_LABELS`, and `resolveReviewRouting()` maps `ReviewPolicy.SPRINT` to `review:sprint`.

GitHub native parent/sub-issue projection exists for the root: `#56/sub_issues` returned #57, #58, and #59.

## Failures And Gaps

### 1. `review:sprint` Exists, But Is Not Fully Honored

The user-noticed `review:sprint` problem is no longer simple absence. The label is present on #57, #58, and #59, and the current code maps sprint review policy to that label.

The failure is now in completion/merge handling. The audit log records that #57 opened PR #60 to the sprint branch, but `work_finish(done)` was blocked:

```text
work_finish(done) is blocked by DevClaw validation: it expects target branch development
even though sprint metadata for issue #57 says prTargetBranch sprint/56-sprint-three-step-test-sprint.
```

That means the sprint routing label and the child PR branch contract are being applied, but the worker completion validation still follows the issue-mode expectation in at least this path. As a result, the sprint child cannot proceed to sprint auto-merge even though it used the right target branch.

Likely root cause: the work-finish PR validation path is still validating against the project base branch for this sprint child instead of resolving the expected target branch from the sprint graph or managed metadata.

Next fix:

- In `work_finish(done)`, detect sprint child issues before PR target validation.
- Use the graph step `prTargetBranch` as the expected PR base.
- Keep project base branch validation for standalone issues and final sprint PRs only.
- Add a regression test using issue #57's shape: child PR base `sprint/56-sprint-three-step-test-sprint`, project base `development`.

### 2. Root Issue Title Is Missing A Root Prefix

Root #56 is titled:

```text
Three Step Test Sprint
```

It has `sprint:root`, so machines can identify it, but the title itself does not include a user-visible root prefix such as `Root: Three Step Test Sprint` or `Sprint root: Three Step Test Sprint`.

Likely root cause: `createSprintStructure()` creates the root issue with `title: args.input.title`. It does not decorate the title before provider creation.

Next fix:

- Decide the exact desired prefix format.
- Apply it only to the provider root issue title in `sprint_create`.
- Keep the milestone and branch slug stable unless the product decision explicitly wants title prefix to affect those too.
- Add a test asserting the root title prefix and child titles remain unchanged.

### 3. Label Colors Are Partly Configured, But Sprint Projection Labels Stay Gray

Current provider label colors include:

- State labels: configured, for example `To Do` is `428bca`, `Refining` is `f39c12`.
- Role labels: configured, for example developer labels are green `0e8a16`.
- Routing labels: configured, for example `review:sprint` is red `d93f0b`.
- Sprint projection labels: gray `ededed`, including `devclaw:sprint`, `sprint:root`, `sprint:child`, and `sprint:sprint-three-step-test-sprint`.

The dynamic labels `step:1`, `step:2`, `step:3`, and `blocked:step` are also not visible on the current step issues, even though current code expects ordered `step:<order>` labels and blocked children should receive `blocked:step`.

Likely root causes:

- Project registration and `sync_labels` create state, role, and step-routing labels from `getStateLabels()` and `getRoleLabels()`. They do not define colors for dynamic sprint projection labels.
- `sprint_create` adds sprint labels directly through `provider.addLabel()` after issue creation. If a dynamic label does not already exist, provider behavior can create or apply it with default gray, depending on provider implementation.
- The audit log says `sprint_repair` failed because label `step:1` was not found. That suggests repair/add-label can assume labels already exist, while ordered step labels are not being ensured before use.

Next fix:

- Add a central sprint label color map, for example:
  - `devclaw:sprint`: neutral blue or gray
  - `sprint:root`: distinct root color
  - `sprint:child`: distinct child color
  - `sprint:<milestone>`: neutral sprint color
  - `step:<order>`: green or blue
  - `blocked:step`: red/orange
- Ensure dynamic sprint labels are created with colors before adding them to issues.
- Update sprint repair to `ensureLabel()` for expected dynamic labels before `addLabel()`.
- Add tests for `step:1`, `step:2`, `blocked:step`, and sprint labels existing with intended colors.

### 4. #58 And #59 Appear In `To Do` While Blocked

`tasks_status` shows #58 and #59 under the general `To Do` queue:

```text
To Do: #59, #58
```

The same response also shows the sprint tree state:

```text
#58 state: blocked, blockedBy: [57]
#59 state: blocked, blockedBy: [58]
```

This is confusing, but it is not by itself proof that the scheduler will dispatch blocked children. The current queue scan implementation in `/root/devclaw-my-fork/lib/services/queue-scan.ts` calls `resolveStepReadiness()` before dispatch. That function returns `step_blocked` while dependencies are unresolved, so the scanner should skip #58 and #59 even though they carry the provider queue label.

The audit log supports that interpretation: heartbeat ticks after #57 was blocked report no new pickups and repeated skipped counts.

Likely root cause: provider queue labels are used so existing queue scans can discover sprint children, while local sprint graph readiness remains authoritative. `tasks_status` reports raw queue labels in its queue section, so blocked sprint children look queued even though the sprint tree says they are blocked.

Next fix:

- Keep the queue label if the scheduler depends on it for discovery.
- Change `tasks_status` and `task_list` presentation in sprint mode to separate "provider queue label" from "dispatchable now".
- For blocked sprint children, either omit them from the dispatchable `To Do` list or annotate them with `blockedBy` and `reason: step_blocked`.
- Add a test that #58/#59 remain undispatched while #57 is unresolved, and a separate status test that blocked children are not presented as ready work.

### 5. GitHub Dependency Projection Is Incomplete For The Three-Step Sprint

GitHub native parent/sub-issue projection exists for #56. However, dependency API checks for:

- #58 blocked by #57
- #59 blocked by #58

returned no dependency rows during this check.

The local graph has the blockers, so the runtime source of truth is correct. The provider dependency projection is missing or not observable for this sprint.

Likely root cause: `createSprintStructure()` calls `linkIssueDependency()` after graph creation, but provider dependency creation may be failing silently, may require different GitHub capabilities, or may not surface through the checked endpoint. This class of issue was also seen in earlier sprint validation work.

Next fix:

- Make `linkIssueDependency()` failures visible in `sprint_create` output and audit logs.
- After writing dependencies, read back the provider projection and report warnings if blocked-by relationships are missing.
- Keep local `devclaw/sprints.json` as authoritative for scheduling.

## Summary Of Likely Root Causes

1. `review:sprint` label creation and mapping are fixed, but `work_finish(done)` still validates sprint child PRs against `development` in the observed path.
2. Root issue title creation uses the raw sprint title without a root prefix.
3. Dynamic sprint projection labels are not centrally ensured with colors before use; repair also appears to assume `step:1` already exists.
4. `tasks_status` mixes provider queue labels with dispatch readiness, making blocked sprint children appear queued.
5. GitHub dependency projection for blockers is absent for #58/#59 even though the local graph is correct.

## Recommended Fix Order

1. Fix `work_finish(done)` sprint child PR target validation. This is blocking #57 despite a correctly targeted PR.
2. Ensure dynamic sprint labels and colors before applying/repairing sprint projection.
3. Update `tasks_status` sprint presentation so blocked children are not shown as ready queue work.
4. Add root title prefix handling in `sprint_create`.
5. Make dependency projection write/readback failures observable.


# Анализ sprint-mode issues и ветки `feat/sprint-mode-config-validation`

Дата проверки: 2026-06-20 09:30-09:40 UTC.

## Источники

- GitHub issues: <https://github.com/ESSEX75/testdevclaw/issues>
- Локальная ветка: `/root/devclaw-my-fork`, `feat/sprint-mode-config-validation`
- Конфиг проекта: `/root/.openclaw/agents/dev-agent/workspace/devclaw/projects/testdevclaw/workflow.yaml`
- Локальный sprint graph: `/root/.openclaw/agents/dev-agent/workspace/devclaw/sprints.json`

## Текущее состояние

Project override для `testdevclaw` действительно включён:

```yaml
workflow:
  taskMode: sprint
  reviewPolicy: sprint
```

`tasks_status` для `-1003911014709:topic:5` тоже резолвит проект как sprint mode:

- `taskMode: "sprint"`
- root sprint issues: `#26`, `#30`, `#34`
- ready/refining child issues: `#27`, `#31`, `#35`, `#36`
- blocked child issues: `#28`, `#32`

Свежие PR:

- PR `#29` -> issue `#27`, target `sprint/sprint-test-sprint-smoke`
- PR `#33` -> issue `#31`, target `sprint/sprint-minimal-pr-smoke-2`
- PR `#37` -> issue `#35`, target `sprint/sprint-minimal-pr-parallel-smoke`
- PR `#38` -> issue `#36`, target `sprint/sprint-minimal-pr-parallel-smoke`

## 1. Почему нет `review:sprint`, и выглядит как `review:human`

В текущей модели нет label `review:sprint`. В коде есть только step routing labels:

- `review:human`
- `review:agent`
- `review:skip`
- `test:skip`

Ключевая причина: `resolveReviewRouting()` в `/root/devclaw-my-fork/lib/workflow/labels.ts:100` явно мапит `ReviewPolicy.SPRINT` в `review:human`:

```ts
if (policy === RP.SPRINT) return "review:human";
```

Этот label ставится при dispatch developer task в `/root/devclaw-my-fork/lib/dispatch/index.ts`, когда роль производит reviewable work. Поэтому child issue в sprint mode получают `review:human`, хотя проектный policy равен `sprint`.

Дополнительно: `reviewPolicy: sprint` сейчас реализован не как routing label, а как отдельная merge policy. Она находится в `/root/devclaw-my-fork/lib/sprints/merge-policy.ts:30`: для `ReviewPolicy.SPRINT` включается `childAutoMerge: true`, а final PR остаётся на human review.

Вывод: отсутствие `review:sprint` сейчас не случайность, а прямое следствие дизайна/кода. Если нужен label для UI, его надо добавить отдельно в routing labels и убрать маппинг sprint -> human. Если label не нужен, надо хотя бы не ставить `review:human` на sprint child issues, потому что он вводит в заблуждение.

### Ожидаемая и фактическая семантика `reviewPolicy: sprint`

Ожидаемая модель для project override:

- root/workspace `workflow.yaml` может оставаться в обычном issue mode: `taskMode: issue` или отсутствует, `reviewPolicy: human`;
- project-level override для `testdevclaw` задаёт `workflow.taskMode: sprint` и `workflow.reviewPolicy: sprint`;
- все child task PR идут из task branch в `sprint/<название-спринта>`;
- child PR не требуют ручного human review по одному;
- DevClaw автоматически вливает child PR в sprint branch, когда PR mergeable и проверки прошли;
- человек ревьюит только финальный PR из `sprint/<название-спринта>` в `development`.

Фактически сейчас:

- project override работает: `tasks_status` для `testdevclaw` показывает `taskMode: "sprint"`;
- worker получает правильный target branch: `PR TARGET BRANCH: sprint/...`;
- но child issue всё равно получают label `review:human`, потому что `ReviewPolicy.SPRINT` мапится в `review:human`;
- обычное workflow transition после `developer done` всё равно переводит issue из `Doing` в `To Review`;
- sprint merge policy запускается отдельно после transition, и auto-merge child PR происходит только если `provider.getPrStatus()` вернул `mergeable === true` и `checksPassed === true`;
- если PR не найден, GitHub вернул `mergeable: UNKNOWN`, checks не определены, нет корректной issue/PR linkage, или runtime работает не на актуальном коде, child issue остаётся выглядеть как обычный human-review flow.

По смыслу это баг текущей реализации: `reviewPolicy: sprint` не должен выглядеть и исполняться как `reviewPolicy: human` для каждого child PR. Нужен отдельный sprint-child path:

- sprint child после `developer done` должен идти в auto-merge в sprint branch;
- на child issue нужен `review:sprint` или отсутствие misleading `review:human`;
- если auto-merge невозможен, issue должен получать понятный технический статус/причину, например `sprint:merge-blocked`, `To Improve` или `Refining`, а не обычное ожидание human review;
- human review должен оставаться только на final PR `sprint/... -> development`.

## 2. Почему labels `step:31`, `step:32`, а не `step:1`, `step:2`

Сейчас `step:*` считается от GitHub issue id, а не от порядкового номера шага внутри sprint.

Код: `/root/devclaw-my-fork/lib/sprints/projection-guard.ts:62`

```ts
const labels = ["devclaw:sprint", "sprint:child", sprintLabel, `step:${issueId}`];
```

То есть:

- sprint root `#30`
- child `#31` получает `step:31`
- child `#32` получает `step:32`

Root issue не получает `step:*`: это уже правильно реализовано в `/root/devclaw-my-fork/lib/sprints/projection-guard.ts:55`, где root получает только `devclaw:sprint`, `sprint:root`, `sprint:<milestone>`.

Вывод: root issue не считается, но label использует provider issue id, поэтому визуально кажется, что счётчик идёт глобально. Если ожидаемое поведение `step:1`, `step:2` внутри sprint, надо менять `expectedManagedLabelsForIssue()` на `step:${step.order}` или ввести отдельный label, например `step-order:1`, сохранив issue id в metadata.

## 3. Почему в Development / sprint status не подставляется PR из issue

Здесь две разные проблемы.

Во-первых, GitHub PR bodies используют текст вида `Addresses issue #31`. По `gh pr list` поле `closingIssuesReferences` пустое у PR `#33`, `#37`, `#38`. Это значит, что GitHub не считает эти PR формально closing/linked references для Development sidebar. Для нативной связки лучше использовать `Fixes #31`, `Closes #31` или GraphQL/REST linked issue API, если нужна именно связь без auto-close.

Во-вторых, DevClaw sprint status не подтягивает PR из provider tree. В `/root/devclaw-my-fork/lib/providers/github.ts` метод `readSprintTree()` возвращает:

```ts
pullRequests: [],
```

А `/root/devclaw-my-fork/lib/tools/tasks/sprint-status.ts:62` берёт PR URL только из `step.prUrl` или из `tree.pullRequests`. Поэтому `tasks_status` показывает `prUrl: null`, хотя PR физически существуют.

Ещё один важный момент: `step.prUrl` в `sprints.json` заполняется в `processSprintMergePolicy()` только после успешного child auto-merge (`markStepMerged`). Пока PR открыт и не merged, graph остаётся без `prUrl`.

Вывод: PR создаются на правильные sprint branches, но не попадают ни в GitHub formal Development linkage, ни в DevClaw sprint status. Нужно либо сохранять `prUrl` при `work_finish(done)` до auto-merge, либо сделать `readSprintTree()`/status поиск PR по issue/timeline/source branch.

## 4. Почему нет blocked steps в Relationship

В локальном graph зависимости есть:

- sprint `#26`: `#28` blocked by `#27`
- sprint `#30`: `#32` blocked by `#31`

Labels тоже есть: `#28` и `#32` имеют `blocked:step`.

Но GitHub Relationship projection пустой:

- `GET /repos/ESSEX75/testdevclaw/issues/30/sub_issues` вернул `[]`
- `GET /repos/ESSEX75/testdevclaw/issues/32/dependencies/blocked_by` вернул `[]`

В локальной ветке после commit `d30451d feat(sprints): project native GitHub relationships` код должен вызывать:

- `linkChildIssue()` для root -> child
- `linkIssueDependency()` для blocked child -> blocking child

См. `/root/devclaw-my-fork/lib/tools/sprints/sprint-create.ts:246` и `:282`.

Но у реально созданных issue есть только fallback comments `parent sprint issue #...`; comments `blocked by #...` отсутствуют. Это сильный признак, что sprint issues были созданы runtime-версией, где dependency projection ещё не выполнялась, либо runtime не был перезапущен/перезагружен после последних commits.

Есть ещё риск в самом коде: `tryCreateNativeSubIssue()` и `tryCreateNativeBlockedByDependency()` ловят ошибки и пишут только `console.warn`, без audit log и без surfaced warning в tool result. Если GitHub API endpoint недоступен, требует preview/другой payload или silently fails, пользователь видит успешный `sprint_create`, но Relationship не появляется.

Вывод: локальный graph и labels знают про blockers, но GitHub Relationship projection фактически не записан. Нужно перезапустить runtime на актуальной ветке и добавить audit/tool warnings для failures в native relationship projection.

## Анализ последних commits ветки

Последние commits в `feat/sprint-mode-config-validation`:

- `735cc19 test(sprints): cover managed projection label repair`
- `d30451d feat(sprints): project native GitHub relationships`
- `14508a6 fix(sprints): project child steps into queue`
- `81bea8b feat(tasks): show sprint status trees`
- `91acbb5 feat(sprints): add merge policy pipeline`
- `6e47a4a feat(worker): validate sprint pr targets`
- `0b6ab08 feat(dispatch): add branch contract`
- `5014a3a feat(sprints): gate queue dispatch by graph`
- `d362c62 feat(sprints): guard managed projection`
- `a49058f feat(tools): add sprint create`

Ветка закрывает существенные части sprint MVP: graph, sprint_create, queue projection, branch contract, status tree, merge policy, projection guard. Но наблюдаемые bugs лежат на стыке provider projection и routing/status:

1. `reviewPolicy: sprint` не имеет собственного label и в UI превращается в `review:human`.
2. `step:*` labels используют issue id, а не order.
3. PR URL не сохраняется в graph/status при создании/open PR.
4. GitHub native relationships не подтверждаются и failures не видны в audit/tool output.

## Рекомендации

1. Решить продуктово, нужен ли label `review:sprint`.
   - Если нужен: добавить `review:sprint` в `STEP_ROUTING_LABELS`, schema/tests/docs и маппить `ReviewPolicy.SPRINT` в него.
   - Если не нужен: не ставить `review:human` на sprint child issues, чтобы UI не говорил неправду.

2. Изменить `step:*` semantics.
   - Для пользовательского UI лучше `step:1`, `step:2`.
   - Если нужен стабильный issue id, хранить его в metadata/body или добавить отдельный `step-issue:<id>`.

3. Фиксировать PR URL раньше.
   - На `work_finish(done)` после `DETECT_PR` записывать `step.prUrl`, даже если auto-merge ещё не произошёл.
   - Дополнительно научить `readSprintTree()` возвращать pullRequests через issue timeline/source branch.

4. Сделать relationship projection наблюдаемой.
   - Не ограничиваться `console.warn`; писать `auditLog`.
   - Вернуть warnings из `sprint_create`.
   - Добавить проверку после записи `sub_issues`/`dependencies`.

5. Проверить runtime deployment.
   - Текущая локальная ветка содержит код dependency projection, но созданные issues не имеют ни native relationships, ни fallback blocked comments.
   - Перед следующей smoke-проверкой нужно убедиться, что OpenClaw/DevClaw runtime реально работает с `/root/devclaw-my-fork` на commit `735cc19` или новее.

## 2026-06-21 / 2026-06-25 two-step sprint smoke run

Дата первичной проверки: 2026-06-21 16:22-16:40 UTC.
Повторная проверка provider/local state: 2026-06-25 14:15-14:35 UTC.

### Evidence

- Sprint root: issue `#47` `Two Step Test Sprint`, <https://github.com/ESSEX75/testdevclaw/issues/47>
- Step 1: issue `#48` `Test sprint step 1`, <https://github.com/ESSEX75/testdevclaw/issues/48>
- Step 2: issue `#49` `Test sprint step 2`, <https://github.com/ESSEX75/testdevclaw/issues/49>
- Child PR `#50`: <https://github.com/ESSEX75/testdevclaw/pull/50>, `step/48-test-step-one` -> `sprint/sprint-two-step-test-sprint`, merged at `2026-06-21T16:22:49Z`
- Child PR `#51`: <https://github.com/ESSEX75/testdevclaw/pull/51>, `step/49-test-step-two` -> `sprint/sprint-two-step-test-sprint`, merged at `2026-06-21T16:28:08Z`
- Final sprint PR `#52`: <https://github.com/ESSEX75/testdevclaw/pull/52>, `sprint/sprint-two-step-test-sprint` -> `development`, merged at `2026-06-21T16:33:30Z`.
- GitHub issue `#47` remains open on 2026-06-25 even after child PRs `#50`/`#51` and final PR `#52` are merged.
- GitHub issue `#47` sub-issue summary is complete: `completed: 2`, `total: 2`, `percent_completed: 100`.
- GitHub milestone `sprint-two-step-test-sprint` remains open because it still has one open issue: root issue `#47`; child issues `#48` and `#49` are closed.
- Local `devclaw/sprints.json` still records `testdevclaw:47` as `status: "active"` with both steps `status: "merged"` and no `finalPr` field.
- Local `devclaw/sprints.json` records the dependency: step `#49` has `blockedBy: [48]`.
- GitHub native relationship API records parent linkage: `#47/sub_issues` returns child issues `#48` and `#49`.
- GitHub native dependency API records blocker linkage: `#49/dependencies/blocked_by` returns `#48`, and `#48/dependencies/blocking` returns `#49`.
- GitHub issue summaries also expose the dependency counts: `#49` has `total_blocked_by: 1`; `#48` has `total_blocking: 1`.
- Provider UI caveat: in child issue views such as `#49`, the visible relationship projection emphasizes the parent issue and may not show the `#48` blocker in the same place, even though the dependency exists in the native API.
- PR `#50`, `#51`, and `#52` all have empty `closingIssuesReferences`; the PR bodies use `Addresses issue #...`, not GitHub closing keywords.

### What worked

- `sprint_create` created the sprint root issue, both child issues, and the sprint branch.
- The local sprint graph recorded the expected dependency: step `#49` had `blockedBy: [48]` in `devclaw/sprints.json` and related metadata.
- Developer workers created child PRs against the sprint branch, not directly against `development`.
- The child PR code changes were valid. PR `#50` and PR `#51` were mergeable and were merged into `sprint/sprint-two-step-test-sprint`.
- A final sprint PR was eventually created and merged: PR `#52`, `sprint/sprint-two-step-test-sprint` -> `development`.
- After graph repair, status rendering could represent the completed child state: progress `2/2`, both child steps `merged`, and both `prUrl` fields populated.
- GitHub native parent/sub-issue projection is present for root `#47` and children `#48`/`#49`.
- GitHub native blocker/dependency projection is present in the API: `#49` is blocked by `#48`.

### What failed

1. Developer `work_finish(done)` rejected sprint-target child PRs.
   - Evidence: issue `#48` includes a worker completion comment saying implementation was complete and PR `#50` was opened.
   - The completion path rejected the PR because it expected target branch `development`, even though the child issue specified `PR target branch: sprint/sprint-two-step-test-sprint`.
   - Result: issue `#48` stayed stuck, and the sprint did not advance automatically.

2. Child auto-merge and finalization did not complete end-to-end.
   - PR `#50` and PR `#51` had to be manually merged.
   - The local sprint graph had to be manually repaired to mark both steps merged.
   - The system did not independently move from child PR merge to durable final sprint completion.

3. Root sprint task does not close automatically.
   - This is one of the two user-observed known issues.
   - Even after progress reached `2/2`, both child issues were closed/done, and final PR `#52` was merged to `development`, root issue `#47` remained open.
   - Local graph `testdevclaw:47` stayed `status: "active"` and did not record `finalPr`.
   - GitHub milestone `sprint-two-step-test-sprint` also stayed open with `open_issues: 1`, because root issue `#47` is still open.
   - Likely cause / next debug point: the reconciliation path handles merged child steps but does not persist final PR metadata or transition the root sprint issue after the final sprint PR merge. The finalizer should reconcile by sprint branch (`sprint/sprint-two-step-test-sprint`) and base branch (`development`) so it can detect already-merged final PRs such as `#52`.

4. GitHub Relationships are present in the API but incomplete/misleading in visible projection.
   - This is the second user-observed known issue.
   - Child issue `#49` body contains `Depends on: test-step-one`, and the local graph has `blockedBy: [48]`.
   - On 2026-06-25, GitHub API confirms the native dependency exists: `#49/dependencies/blocked_by` returns `#48`, and `#48/dependencies/blocking` returns `#49`.
   - GitHub issue summaries also show `#49 total_blocked_by: 1` and `#48 total_blocking: 1`.
   - However, the child issue UI/projection still makes the parent relationship much more visible than the blocker relationship. If the requester is inspecting the child issue relationship panel, this can still look like "parent is present, blocker is missing."
   - Next debug point: distinguish provider write failure from provider UI/discoverability. The native API says the blocker was written; DevClaw status/reporting should surface it directly so users do not have to inspect provider API endpoints.

5. PR bodies still use non-closing issue text.
   - PR `#50` and PR `#51` use `Addresses issue #48/#49`; PR `#52` has an empty body.
   - As noted in the earlier analysis, this does not create formal GitHub closing linkage in the Development/sidebar model.
   - `gh pr view` shows `closingIssuesReferences: []` for all three PRs.
   - If formal provider linkage is required, DevClaw needs either closing keywords such as `Fixes #...` / `Closes #...` or explicit provider API linkage. If auto-close must remain under DevClaw control, do not rely on PR body text; persist explicit sprint finalization state instead.

6. Labels and state can become inconsistent after failed completion.
   - During manual recovery, issue `#49` temporarily had both `To Do` and `Doing`.
   - It later fell back to `Planning` before `task_start` moved it back to `To Do`.
   - This points to fragile state reconciliation after a failed worker finish path.

### Recommendations

1. Fix sprint child PR target validation in `work_finish(done)`.
   - For sprint child issues, validate the PR base against the child issue branch contract or sprint graph target branch, not only the project base branch.
   - Include the expected and actual target branch in the error message when validation fails.

2. Persist child PR metadata before merge.
   - Save `step.prUrl` when `work_finish(done)` detects the child PR.
   - Do not wait until successful auto-merge to make the PR visible in `tasks_status`.

3. Make child auto-merge idempotent and status-driven.
   - Poll or reconcile open/merged child PRs by issue id, source branch, and sprint target branch.
   - If a child PR is already merged, mark the graph step merged without requiring manual repair.

4. Add final sprint completion logic.
   - When all child steps are merged, create or update the final PR from `sprint/sprint-two-step-test-sprint` to `development`.
   - Set `finalPr` in the sprint graph.
   - Reconcile already-existing final PRs by head/base branch, because PR `#52` was created and merged but the graph still lacks `finalPr`.
   - Close or complete root issue `#47` only after the final sprint PR satisfies the configured review/merge policy.
   - Close or complete the milestone when all sprint issues are closed, or document that milestone closure is manual.

5. Surface native GitHub blocker relationships explicitly in DevClaw status.
   - Keep parent/root linkage visible, but also read/display native blocked-by relationships from provider APIs where available.
   - Treat local graph `blockedBy` as the source of truth and provider dependency API as the projection check.
   - Surface provider failures as tool warnings or audit entries instead of only logging them.
   - Add a status/report field that shows `#49 blocked by #48` without requiring the user to inspect GitHub's API.

6. Harden label/state reconciliation.
   - Make state transitions remove mutually exclusive workflow labels atomically.
   - After a failed completion, reconcile the issue from the graph and PR state instead of falling back to stale labels.

7. Add a root-finalization regression test.
   - Fixture: root `#47` with two merged child steps and final PR `#52` already merged.
   - Expected: graph records final PR, root issue transitions to terminal/done state, and the provider root issue is closed.
   - Also assert that parent/sub-issue and blocked-by projections are reported separately, because GitHub may display them differently in the UI.

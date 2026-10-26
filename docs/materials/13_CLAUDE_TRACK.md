# CLAUDE CODE TRACK

Claude works only in `xiangqi-claude` / `claude-full`.

## Start prompt
You are the implementation engineer for the CLAUDE branch of a Vietnamese-first AI-assisted Xiangqi learning platform.

Read all docs first. Do not code immediately.

PHASE 0:
1 inspect repo
2 identify stack
3 run app
4 run tests/lint/build
5 list current features
6 list broken/incomplete parts
7 map repo to spec
8 identify technical risks
9 security/privacy issues
10 licensing issues
11 propose M0 plan

Explain for a beginner:
- folder roles
- commands and why
- outputs

Constraints:
- spec is source of truth
- engine/rules = chess truth
- LLM = grounded explanation
- no fake ML
- no unlicensed data
- no secrets
- tests for critical logic
- no unrelated refactor

STOP after audit.

## Milestone prompt
Proceed with Milestone [Mx] ONLY.

Before coding:
- reread spec
- inspect code
- explain goal
- acceptance criteria
- files expected to change
- risks/edge cases

Implement minimum complete solution.
Run tests/lint/build.
Review diff.
Update IMPLEMENTATION_REPORT.md:
goal, changed files, decisions, commands, tests, bugs, limitations, deviations, 5 concepts owner should understand.

STOP.

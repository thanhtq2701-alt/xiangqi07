# LEARNING MODEL + SPACED REPETITION

## Principle
Repeat skill/error pattern, not exact answer.

## Skill taxonomy v0
Strategic:
- position evaluation
- attack planning
- defense planning
- control/constraint
- coordination
- general safety
- weak-point identification
- conversion

Tactical/process:
- threat awareness
- candidate moves
- calculation
- forcing moves
- pin/constraint
- discovered attack
- material tactic
- mate pattern
- defensive resource
- rushed decision
- failure to reassess
- time management

## User-skill state
mastery_score
stability
last_review_at
next_review_at
lapse_count
evidence_count
transfer_success_count

## Heuristic score example
Fail + bad reasoning: -6
Fail + partly right: -3
Correct Hint2: 0
Correct Hint1: +1
Correct slow: +2
Correct no hint: +3
Unseen transfer + good reasoning: +5
Same error recurs in real game: -6
Avoids error correctly in game: +4

## Scheduler v0
Fail: 1 day
Heavy help: 1–2 days
Weak reasoning: 3 days
Correct no hint: 7 days
Unseen transfer success: 14 days
Second transfer success: 30 days
Later: 60/90

This is heuristic, not a scientific claim.

## Daily due cap
Beginner 5–8
Intermediate 8–10
Advanced configurable

## Priority
due + weakness + recurrence + low evidence - recent exposure

## Mastery
Require:
- multiple verified attempts
- good reasoning
- at least 2 unseen transfer successes
- reduced recent recurrence

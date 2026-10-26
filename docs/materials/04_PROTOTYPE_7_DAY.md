# 7-DAY PROTOTYPE

## Goal
Một flow demo hoàn chỉnh:
Play/import game → critical mistake → reflection → engine-grounded explanation → retry → related puzzle → spaced review → dashboard update.

## Day 0
- clean repo
- docs copied
- environment verified
- baseline commit
- claude-full + codex-full branches/worktrees

## Day 1 — Board + Rules
- 9x10 board
- select/move
- legal rules
- turn
- move history
- reset
- unit tests each piece/flying general

Exit: full local game possible.

## Day 2 — Engine/Bot
- engine adapter
- top move
- bot
- timeout
- cache

Exit: 20 test positions no crash, bot always legal.

## Day 3 — Post-game Review
- save game
- analyze moves
- eval timeline
- top 1–3 critical moments
- retry

## Day 4 — Reflection + AI explanation
- adaptive questions
- structured engine facts
- JSON explanation
- fallback
- feedback/report

## Day 5 — Puzzle follow-up
- 20–50 curated puzzles
- tags
- level
- recommend related unseen puzzle
- attempt logging

## Day 6 — Spaced repetition + profile
- user_skill state
- next_review
- due queue
- skill dashboard
- recent mistakes

## Day 7 — QA + Deploy
- smoke tests
- README
- demo 30–60 sec
- screenshots/GIF
- release tag v0.1.0-prototype
- known limitations
- AI usage log

## Stretch only
- online PvP
- richer login
- heatmaps
- 3D

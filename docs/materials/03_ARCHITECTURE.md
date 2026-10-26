# ARCHITECTURE V0.1

## Stack đề xuất
Frontend: Next.js + React + TypeScript + Tailwind  
Backend: Python 3.12 + FastAPI  
DB/Auth: Supabase/PostgreSQL  
Engine: Xiangqi engine adapter, candidate Pikafish  
AI: LLM API backend-only  
Realtime later: Supabase Realtime/WebSocket

> Bạn đang có Python 3.14; nên cân nhắc thêm 3.12 nếu dependency chưa support 3.14 tốt.

## Diagram
Browser
→ Board / Review / Puzzle / Dashboard
→ FastAPI
→ Game Service
→ Rules Adapter
→ Engine Adapter → Xiangqi Engine
→ Review/Diagnostic Service
→ Puzzle/Spaced-Repetition Service
→ AI Explanation Service → LLM
→ PostgreSQL

## Engine output
- eval
- top moves
- PV
- depth
- engine version

## Diagnostic output example
{
  "primary_skill": "threat_awareness",
  "secondary_skill": "candidate_move_generation",
  "severity": "major",
  "confidence": 0.72
}

## AI explanation input
- player level
- position
- engine top moves
- played move
- eval before/after
- diagnosis
- user reflection
- curated lesson context

## Data tables
users
games
moves
engine_analyses
reviews
skills
user_skills
puzzles
puzzle_tags
attempts
feedback

## API candidate
POST /games
POST /games/{id}/moves
POST /games/{id}/analyze
GET /reviews/{game_id}
POST /reviews/{id}/reflection
POST /reviews/{id}/retry
GET /practice/next
POST /puzzles/{id}/attempt
GET /profile
GET /reviews/due

## Guardrails
- backend validation
- secrets backend only
- engine cache by position hash
- schema validation for LLM output
- fallback when LLM fails
- prompt/version logging
- no autonomous production patching

# AI / ML PLAN

## L0 Deterministic
Rules + engine + heuristics + DB.

## L1 LLM-assisted teaching
LLM explains verified facts.
This means using an existing ML model, not training your own.

## L2 Adaptive heuristic
Next practice based on:
skill weakness + due date + level + recent errors + unseen filter.

## L3 Real ML
Only after labels/data/baseline/test split.

### Candidate task A: mistake classification
Metrics: macro F1, class precision/recall, confusion matrix.
Baseline: owner-authored rules.

### Candidate B: retention prediction
Predict P(success on unseen related position at time t).
Models: logistic regression first, tree model later.
Metrics: log loss, AUC, calibration.

### Candidate C: puzzle ranking
Metrics: Recall@K, NDCG@K.
Baseline: heuristic scheduler.

## Gold set
Start 20–50 owner-verified positions.
Then 100+.
Store engine version, line, tags, level, explanation rubric.

## RAG
Useful later for curated lessons/opening notes.
RAG is retrieval at runtime, not training.

## CV gates
Safe now:
“Building an AI-assisted Xiangqi learning platform…”

After adaptive rules:
“Built adaptive puzzle recommendation based on user mistakes…”

Only after real model:
“Trained/evaluated a machine-learning model to …”

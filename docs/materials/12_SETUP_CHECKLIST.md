# WINDOWS SETUP

## Verify
PowerShell:

git --version
python --version
py --list
node -v
npm -v
code --version

## Git identity
git config --global user.name
git config --global user.email
git config --global --list

## Repo
git status
git branch
git log --oneline -10

Freeze when clean:
git add .
git commit -m "chore: freeze parallel baseline"

## Branches
git branch claude-full
git branch codex-full

## Worktrees
git worktree add ..\xiangqi-claude claude-full
git worktree add ..\xiangqi-codex codex-full

## Python venv
Prefer 3.12 if required:
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

## Secrets
.env or .env.local
Never commit.
Create .env.example.

## Commit flow
git status
git diff
run tests/lint/build
git add .
git commit -m "feat: ..."
git push

## You must understand
1. what feature solves
2. changed files
3. input→output
4. tests
5. limitation

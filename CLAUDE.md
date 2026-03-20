# iBuyArtifacts — Project Context for Claude

## Owner
Donovan Duncan (CEO, indie.io) — CST timezone, morning person, short bursts.

## Communication Rules
- **Act autonomously** — do NOT ask "should I proceed?" or "is this okay?"
- Keep responses short and direct, no fluff
- If 70%+ confident, just do it. Donovan prefers fixing mistakes over constant interruptions
- After EVERY code edit: run `git diff` to verify changes landed
- Before complex multi-step work: write state to `tasks/todo.md`

## What is this
iBuyArtifacts project

## Tech Stack
python

## Key Files
- `.gitignore`
- `CLAUDE.md`
- `README.md`
- `appraisal.html`
- `artifacts_data.json`
- `css`
- `fetch_artifacts.py`
- `gallery.html`
- `index.html`
- `js`
- `news.html`
- `sell.html`


## Architecture
- **Front-end**: Multi-page site (index, gallery, appraisal form, sell, news) with HTML/CSS/JS for UI and interaction
- **Data layer**: JSON artifact database (artifacts_data.json) + Python fetch script for content sourcing and updates
- **Appraisal service**: HTML form feeding to Gemini AI (Harold persona) generating expert appraisals with historical/market context
- **Hosting**: Static site served from Amsterdam nginx + transactional mailer for appraisal delivery
- **Revenue**: Gumroad integration ($49 appraisals) + Ko-fi tips; Harold profile photos on IG/X/Bluesky drive traffic

## Task Tracking
- **Tasks**: `tasks/todo.md` — check on startup, mark items as you go
- **Lessons**: `tasks/lessons.md` — update after corrections, check on startup

## Session Recovery
1. Read `tasks/todo.md` for where we left off
2. Read `tasks/lessons.md` for project-specific gotchas
3. `git log --oneline -10` and `git status` to see what's been done
4. Resume from last incomplete checkbox

# ForgeOS

> **One English sentence → a built, tested, secured, and deployed full-stack SaaS.**

ForgeOS is a fully autonomous, multi-agent product factory that runs locally on consumer hardware. Type an idea; five specialised AI agents collaborate to produce a complete codebase with architecture docs, security audit, GitHub repo, and cloud deployment.

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%7C%20Claude-brightgreen.svg)](https://ollama.ai)
[![Version](https://img.shields.io/badge/version-0.1-violet.svg)](CHANGELOG.md)

---

## What it does

```
"Build a habit tracker SaaS with daily streaks and a dashboard"
                          ↓  ~25 minutes
  ✅ SPEC.md + ARCH.md + TASKS.json
  ✅ Full Next.js 14 + FastAPI + Supabase scaffold
  ✅ All endpoints, pages, and tests implemented
  ✅ OWASP security audit + RLS policies
  ✅ GitHub repo created + Railway + Vercel deployed
```

---

## Architecture

Five specialised agents run in a fixed pipeline. Each writes its output to
`builds/<id>/` and updates `context.json` before the next agent starts.

```
Idea ──▶ ArchitectAgent ──▶ ScaffoldAgent ──▶ CoderAgent
                                                   │
              ForgeBrain ◀── DeployAgent ◀── SecurityAgent
```

| # | Agent | What it produces |
|---|-------|-----------------|
| 1 | **ArchitectAgent** | `SPEC.md`, `ARCH.md`, `STACK.json`, `TASKS.json` |
| 2 | **ScaffoldAgent** | Full project tree — Next.js 14 + FastAPI + Supabase |
| 3 | **CoderAgent** | All tasks implemented with tests; self-reviews every file |
| 4 | **SecurityAgent** | `SECURITY.md`, OWASP audit, Supabase RLS policies |
| 5 | **DeployAgent** | GitHub repo, Railway (backend), Vercel (frontend) |

After each build, **ForgeBrain** distils patterns into your Obsidian vault.
**Healer** runs as a daemon watching Sentry + Uptime Robot for auto-PR fixes.

---

## Hardware & LLM

Designed to run on a single consumer GPU — no cloud LLM required for
development.

| Provider | Role | Cost |
|----------|------|------|
| **Ollama** `qwen2.5-coder:7b` | Primary — all tasks | Free, local |
| **Claude** `claude-haiku-4-5` | Fallback if Ollama is unreachable | ~$0.01/build |

The LLM router tries Ollama first; if the service is not running on port
11434 it automatically falls back to Claude. Both providers are optional —
if neither responds, agents use deterministic scaffold templates to guarantee
forward progress.

---

## Quick start

### Prerequisites

- WSL2 (Ubuntu 22.04) + Python 3.11+
- Node 20+ for the UI
- [Ollama](https://ollama.ai) with `qwen2.5-coder:7b` pulled (optional but recommended)
- `ANTHROPIC_API_KEY` in `.env` (free-tier fallback)

### Install

```bash
# Clone
git clone https://github.com/<your-username>/forgeos
cd forgeos

# Python engine (WSL2)
pip install -e ".[all]"
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY at minimum

# UI
cd forgeos-ui && npm install
```

### Run

```bash
# Terminal 1 — start Ollama (skip if using Claude only)
ollama serve

# Terminal 2 — ForgeOS API (WSL2, inside forgeos/)
PYTHONPATH=. python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 \
  --reload-dir agents --reload-dir llm --reload-dir tools

# Terminal 3 — ForgeOS UI
cd forgeos-ui && npm run dev
```

Open [http://localhost:3000](http://localhost:3000), type your idea, click **Forge**.

### Or run headless

```bash
PYTHONPATH=. python3 orchestrator.py --idea "Build a SaaS that turns voice notes into tasks"
```

---

## UI

The Next.js 14 dashboard streams agent progress in real-time via SSE:

- **3D hero scene** — React Three Fiber, five orbiting agent nodes, mouse tracking
- **Live build log** — agent cards update as each phase completes
- **Build history** — sidebar lists all past builds with status
- **One-click resume** — pick up a failed build exactly where it stopped

---

## File layout

```
forgeos/
├── orchestrator.py        # entry point, runs the agent pipeline
├── api.py                 # FastAPI server + SSE streaming (/builds/{id}/stream)
├── models.py              # LLMClient, ProjectContext, Task (canonical types)
├── config.py              # LLM routing, stack, deploy config
├── forge_brain.py         # Obsidian knowledge accumulation
├── healer.py              # self-healing daemon (Sentry + Uptime Robot)
├── agents/
│   ├── base.py            # BaseAgent ABC
│   ├── architect.py       # spec + task decomposition
│   ├── scaffold.py        # full project tree + config files
│   ├── coder.py           # implements every task + self-review pass
│   ├── game.py            # Three.js / Phaser / Godot (auto-skipped for non-games)
│   ├── security.py        # OWASP audit, RLS policies
│   └── deploy.py          # GitHub + Railway + Vercel
├── llm/
│   ├── router.py          # Ollama → Claude fallback chain
│   ├── ollama.py          # OllamaClient
│   └── claude.py          # ClaudeClient (haiku-4-5 default)
├── tools/
│   ├── github.py          # repo creation via GitHub API
│   ├── railway.py         # Railway deploy
│   ├── vercel.py          # Vercel deploy
│   └── supabase_admin.py  # service-role Supabase client
├── forgeos-ui/            # Next.js 14 App Router dashboard
│   ├── app/page.tsx       # main page — 3D hero + build view
│   ├── components/3d/     # React Three Fiber hero scene
│   └── hooks/useStream.ts # SSE client with reconnection
└── builds/                # runtime output — one folder per build
    └── <id>/
        ├── context.json   # full pipeline state
        ├── SPEC.md
        ├── ARCH.md
        ├── TASKS.json
        ├── STACK.json
        ├── SECURITY.md
        └── project/       # the generated codebase
```

---

## Generated stack

Every ForgeOS build produces a project using this default stack:

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 App Router + TypeScript + Tailwind CSS |
| Backend | FastAPI + Pydantic v2 + SQLAlchemy |
| Database | Supabase (Postgres + Auth + Storage + RLS) |
| Deploy | GitHub → Railway (API) + Vercel (UI) |
| Tests | pytest (backend) + Vitest (frontend) |
| CI/CD | GitHub Actions |
| Monitoring | Sentry + Uptime Robot |

---

## Environment variables

```bash
# Minimum to run (one of these must be set)
ANTHROPIC_API_KEY=sk-ant-...      # Claude haiku-4-5 fallback

# Optional LLM
OLLAMA_MODEL=qwen2.5-coder:7b    # default model for Ollama

# Deploy (agents degrade gracefully without these)
GITHUB_TOKEN=ghp_...
RAILWAY_TOKEN=...
VERCEL_TOKEN=...

# Supabase (for generated projects)
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# Monitoring (optional)
SENTRY_DSN=...
UPTIMEROBOT_API_KEY=...
```

---

## Tests

```bash
pip install -e ".[dev]"
PYTHONPATH=. python3 -m pytest tests/ -v
```

Unit tests mock all LLM calls. Agents fall back to deterministic scaffold
templates when no LLM is configured, so the suite passes without API keys.

---

## Build resumption

If a build is interrupted, resume from exactly where it stopped:

```bash
# Find the build ID
ls builds/

# Resume (completed agents are auto-skipped)
PYTHONPATH=. python3 orchestrator.py \
  --idea "Build a habit tracker with daily streaks" \
  --workdir builds/<id>
```

---

## Roadmap

- [ ] Multi-tenancy (per-user build isolation)
- [ ] Plugin system for custom agent steps
- [ ] Mobile scaffold (React Native + Expo)
- [ ] Streaming diff view (see files being written live)
- [ ] DeepSeek / Gemini LLM provider support
- [ ] Obsidian ForgeBrain auto-publish

---

## License

MIT — see [LICENSE](LICENSE).

---

*Built with ForgeOS v0.1 · Runs locally on an ASUS TUF + RTX 4050*

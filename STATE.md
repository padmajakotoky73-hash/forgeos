# ForgeOS — Build State

## [2026-05-24T16:38:49Z] Phase 1 complete

**What was built:**
- FIX 1: `/` and `/healthz` routes embedded directly in `_BE_MAIN` scaffold template; CoderAgent SYSTEM_PROMPT updated with guard rule.
- FIX 2: GitHub repos now created `private=False` (required for Vercel). `VercelClient.trigger_deployment` now accepts `root_directory` param. `DeployAgent._step_vercel` passes `root_directory="frontend"`. `vercel.json` template added to scaffold frontend.
- FIX 3: `SecurityReport`, `FailureRecord`, `SandboxResult`, `BrowserResult`, `PipelineBlockedError` dataclasses added to `models.py`. `SecurityAgent` fully rewritten with 5 real checks (hardcoded secrets, unauth routes, SQL injection, env hygiene, frontend key leak). Gate raises `PipelineBlockedError` if critical findings.
- FIX 4: `_CI_YAML` template fixed (PYTHONPATH, backend/tests/ target, healthz smoke test, -v flag). `_DEPLOY_YAML` updated from Railway to Render. ForgeOS own `.github/workflows/ci.yml` created.

**Files created/modified:**
- `agents/security.py` — fully rewritten
- `agents/scaffold.py` — _BE_MAIN, _CI_YAML, _DEPLOY_YAML, vercel.json template
- `agents/coder.py` — SYSTEM_PROMPT guard for healthz
- `agents/deploy.py` — repos public, root_directory passed
- `tools/vercel.py` — trigger_deployment root_directory param
- `models.py` — 5 new dataclasses
- `.github/workflows/ci.yml` — ForgeOS CI

**Verified:**
- `PYTHONPATH=. python3 -c 'from agents.security import SecurityAgent...'` → OK
- SecurityAgent end-to-end: 5 passed, 1 warning, 0 critical → success

**Blockers hit:** None

**Next:** Phase 2 — Dependency install (e2b, browser-use, composio-claude, redis, rq)


---

## [2026-05-24] Phase 14 — ContractForge live build errors

### Error 1 — ceo_review ran before ArchitectAgent (FIXED)
**Stage**: ceo_review gate
**Cause**: Gate evaluated empty SPEC.md — LLM penalised missing spec, scored 4/10.
**Fix**: Moved ceo_review to run AFTER architect in hermes.py `_build_pipeline()`.

### Error 2 — _parse_verdict regex failed on markdown bold (FIXED)
**Stage**: all gates
**Cause**: `SCORE: N/10` regex did not match `**Score:** 4/10` (markdown `**...**` wrapper).
**Fix**: Regex changed from `SCORE\s*[:\-]\s*` to `SCORE[^0-9]*?` to skip any non-digit chars.

### Error 3 — Text "FAIL" verdict overrides numeric score (FIXED)
**Stage**: office_hours gate
**Cause**: LLM wrote score 6/10 but included "FAIL (High Risk)" in prose. Text detection
  in `_parse_verdict` treated "FAIL" as authoritative and overrode the numeric score.
  Result: gate blocked at score=6.0 even though min_score=6.0 (should be PASS).
**Fix**: `_parse_verdict` now uses numeric score as primary signal when score > 0.
  Text detection ("PASS"/"FAIL") is fallback only when score=0.0 (no number found).

### Error 4 — Shared workdir between builds (FIXED)
**Cause**: HermesOrchestrator used `RUNTIME.workdir_root` for all builds — artifacts overwrote.
**Fix**: Per-build subdir created automatically under `builds/<slug>-<timestamp>/`.

---

## Next Sprint

### COMPUTER USE INTEGRATION (Phase 2)
- Replace browser-use in tools/browser_agent.py with Claude Computer Use API
- Requires: Docker + VNC sandbox, anthropic beta header "computer-use-2024-10-22"
- Model: claude-sonnet-4-5 (computer use enabled)
- Agents that can: open apps, fill forms, navigate any website, operate like a human at a computer
- Every product ForgeOS builds gets an embedded ComputerUseAgent at scaffold time
- This is the "runs a company autonomously" layer

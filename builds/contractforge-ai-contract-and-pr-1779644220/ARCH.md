# ContractForge Architecture

## Stack Justification

### Frontend: Next.js 14 (App Router) + Tailwind + Shadcn/ui
**Why**: Next.js 14 provides server-side rendering, API routes, and incremental static regeneration—critical for SEO and fast contract preview rendering. App Router enables nested layouts for multi-step contract generation flows. Tailwind + Shadcn/ui deliver production-grade UI components (forms, modals, tables) without bloat, essential for a document-heavy SaaS. Vercel deployment ensures zero-config CI/CD.

### Backend: FastAPI
**Why**: FastAPI's async-first design handles concurrent PDF generation and LLM inference calls efficiently. Built-in OpenAPI docs reduce onboarding friction. Pydantic validation ensures type-safe contract data. Modal.com integration for GPU-accelerated LLM inference is seamless via FastAPI endpoints. APScheduler for cron jobs (subscription reminders) runs natively.

### Database: Supabase (Postgres)
**Why**: Postgres's JSONB columns store state-specific GST rules and contract metadata without schema bloat. Row-level security (RLS) enforces multi-tenant isolation. Supabase Storage (S3-compatible) eliminates separate file storage infrastructure. Realtime subscriptions (unused in MVP but available for future collaboration). Native UUID support for contract IDs.

### Cache: Upstash Redis
**Why**: Serverless Redis (no infrastructure management). Sliding-window rate limiting prevents abuse (e.g., 100 contract generations/hour per user). Session caching for LLM inference results (avoid re-generating identical contracts). Upstash's REST API works in edge functions (Vercel).

### Queue: Upstash Redis Streams
**Why**: Lightweight alternative to Kafka for this scale. Handles async tasks: PDF generation, e-signature webhooks, email notifications. Streams provide ordering guarantees for audit trails. No separate infrastructure.

### Auth: Supabase Auth
**Why**: Built-in JWT support integrates seamlessly with FastAPI (Bearer token validation). Email verification out-of-the-box. Row-level security policies tied to `auth.uid()`. No third-party auth service overhead.

### Payments: Lemon Squeezy
**Why**: Handles INR pricing natively (avoids currency conversion fees). Recurring billing for subscriptions. Webhook support for subscription status changes (new_subscription, subscription_updated, subscription_cancelled). Lower fees than Stripe for India-focused SaaS.

### Email: Resend
**Why**: Transactional email for contract delivery, signature reminders, subscription confirmations. High deliverability in India. Simple API, no SMTP configuration. Supports email templates (Markdown-to-HTML).

### Monitoring: Sentry + Uptime Robot
**Why**: Sentry captures FastAPI exceptions, LLM inference failures, PDF generation errors. Uptime Robot monitors endpoint health (Railway backend, Vercel frontend). Alerts via Slack for critical failures.

### CI/CD: GitHub Actions
**Why**: Native GitHub integration. Workflows for: linting (Ruff), type checking (mypy), testing (pytest + Jest), building Docker images for Railway, deploying to Vercel. No external CI/CD cost.

### Deployment: Railway (backend) + Vercel (frontend)
**Why**: Railway provides managed PostgreSQL, Redis, and FastAPI hosting in one dashboard. Vercel optimizes Next.js builds and edge functions. Both support GitHub auto-deploy on push. Railway's pricing is transparent for Indian startups.

### ML Service: FastAPI Inference + MLflow + Great Expectations
**Why**: FastAPI endpoint (`POST /api/contracts/generate`) calls modal.com GPU for LLM inference. MLflow tracks model versions and inference metrics. Great Expectations validates contract JSON schema before storage (e.g., all required fields present, GST number format valid). Prevents garbage-in-garbage-out.

### GPU: modal.com
**Why**: Serverless GPU for LLM inference (Claude via Anthropic API or open-source Llama via Replicate). No GPU infrastructure to manage. Pay-per-inference. Scales to zero when idle.

### GST Compliance DB: Hardcoded Rules + Supabase JSON Columns
**Why**: GST rates are static (5%, 12%, 18%, 28% for most services). Store as JSON in `contracts.gst_config` column: `{"state": "Karnataka", "rate": 18, "effective_date": "2024-01-01"}`. Hardcoded rules in FastAPI (e.g., "Software services → 18%"). Avoids external API calls. Updates via schema migration (quarterly).

### Document Storage: Supabase Storage
**Why**: S3-compatible, no separate AWS account. Signed URLs for secure PDF downloads. Audit logs built-in. Integrates with Postgres (foreign keys to `contracts.pdf_path`).

### Rate Limiting: Upstash Redis (Sliding Window)
**Why**: Prevent abuse: 100 contract generations/hour per user, 1000/day per IP. Sliding window (not fixed) ensures fairness. Upstash REST API works in FastAPI middleware.

### Analytics: PostHog
**Why**: Event tracking for: contract generation, PDF export, e-signature completion, subscription upgrade. Cohort analysis (free → paid conversion). Session replay for UX debugging. Self-hostable if needed.

### Cron Jobs: APScheduler (FastAPI)
**Why**: Subscription renewal reminders (7 days before expiry). Runs in FastAPI background tasks. Triggers Resend email. No external cron service.

---

## System Diagram
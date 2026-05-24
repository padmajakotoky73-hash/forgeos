# ContractForge Specification

## Problem
Freelancers in India face significant friction when creating professional, legally compliant contracts. Manual drafting is time-consuming, error-prone, and often results in non-compliant agreements that expose both parties to legal risk. GST compliance adds another layer of complexity that most freelancers lack expertise in. Existing solutions are either too generic (missing Indian-specific requirements) or too expensive (legal consultation fees).

## Target Users
1. **Freelancers in India** (primary): Solo practitioners, consultants, and small agencies needing to generate contracts for client engagements.
2. **Small business owners**: Entrepreneurs hiring freelancers and needing standardized, compliant agreements.
3. **Agencies**: Teams managing multiple freelancer relationships and requiring consistent contract templates.

## Core Features

1. **AI-Powered Contract Generation**
   - Generate GST-compliant contracts using LLM inference (Claude/GPT via modal.com).
   - Input: project scope, duration, rate, client details, deliverables.
   - Output: production-ready contract in Markdown, stored in Supabase.
   - State-specific GST rate injection (JSON columns in Postgres).

2. **NDA Template Library**
   - Pre-built, India-compliant NDA templates (unilateral and mutual).
   - Customizable fields: party names, confidentiality period, jurisdiction.
   - One-click generation with auto-fill from user profile.

3. **Statement of Work (SOW) Generation**
   - AI-assisted SOW creation with sections: scope, deliverables, timeline, payment terms, acceptance criteria.
   - Linked to contract for consistency.
   - Milestone-based breakdown for phased projects.

4. **PDF Export with E-Signature Flow**
   - Convert generated contracts to PDF (via Puppeteer or WeasyPrint).
   - Store PDFs in Supabase Storage (S3-compatible).
   - E-signature integration (placeholder for DocuSign/Signzy API).
   - Audit trail: track signature status, timestamps, IP addresses.

5. **Subscription & Payment Management**
   - Monthly subscription at Rs2499 via Lemon Squeezy.
   - Usage tracking: contracts generated per month (PostHog analytics).
   - Soft limits: free tier (3 contracts/month), paid tier (unlimited).

6. **User Authentication & Profile**
   - Supabase Auth (email/password, optional Google OAuth).
   - User profile: name, GST number, business address, bank details (for invoicing).
   - Subscription status and billing history.

## Non-Features (Out of Scope)

- **Real-time collaborative editing** on contracts.
- **Custom contract templates** beyond AI-generated and pre-built NDAs/SOWs.
- **Advanced legal consultation services** or lawyer-on-demand.
- **Multi-language support** (English only, with Hindi UI labels optional).
- **Blockchain-based contract verification** or smart contracts.
- **Integration with accounting software** (Tally, QuickBooks) in MVP.
- **Mobile app** (web-responsive only for MVP).

## Success Metrics

1. **Adoption**: 500+ active users within 3 months of launch.
2. **Engagement**: Average 5+ contracts generated per paying user per month.
3. **Conversion**: 15%+ free-to-paid conversion rate.
4. **Retention**: 70%+ monthly retention for paid users.
5. **Satisfaction**: NPS ≥ 40 from user surveys.
6. **Revenue**: Rs50,000+ MRR by month 6.
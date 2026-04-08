---
name: Auth Middleware Rewrite
description: Auth rewrite is compliance-driven (legal), not tech debt — favor compliance over ergonomics
type: project
---

Auth middleware rewrite is driven by legal/compliance requirements around session token storage.
**Why:** Legal flagged the current implementation for storing session tokens in a way that doesn't meet new compliance requirements. This is NOT a tech-debt cleanup.
**How to apply:** When making scope decisions about the auth rewrite, favor compliance and security over developer ergonomics. Don't cut corners on token handling to save time.

Timeline: Must be completed by 2026-05-01 (compliance deadline).
Owner: Backend team (Sarah leading).

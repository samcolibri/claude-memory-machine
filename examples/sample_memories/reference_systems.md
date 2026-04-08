---
name: External Systems
description: Where to find bugs (Linear), metrics (Grafana), docs (Notion)
type: reference
---

- **Bug tracking:** Linear, project "BACKEND" for API issues, "FRONTEND" for UI bugs
- **Metrics dashboard:** grafana.internal/d/api-latency — oncall watches this, check when editing request-path code
- **Documentation:** Notion workspace "Engineering" — architecture decisions and RFCs live here
- **CI/CD:** GitHub Actions, workflows in `.github/workflows/`
- **Staging:** staging.techco.dev (auto-deploys from `develop` branch)

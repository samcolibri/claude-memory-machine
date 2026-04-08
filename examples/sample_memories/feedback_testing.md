---
name: Testing Preferences
description: Use real databases in tests, prefer integration over unit, vitest not jest
type: feedback
---

Always use real databases in integration tests, never mocks for DB operations.
**Why:** Had an incident where mocked tests passed but a production migration failed — mock/prod divergence masked the bug.
**How to apply:** Use testcontainers or a real test database. For unit tests of pure logic, mocks are fine. For anything touching the database, use the real thing.

Use vitest, not jest.
**Why:** Project standardized on vitest for speed and native ESM support.
**How to apply:** All new test files use `import { describe, it, expect } from 'vitest'`.

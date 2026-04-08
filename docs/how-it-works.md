# How It Works

## The 30-Second Version

1. A global config file (`~/.claude/CLAUDE.md`) loads in every Claude Code session
2. It tells Claude to read your memory files before responding
3. Claude remembers who you are, what you've been working on, and how you like to work
4. At the end of each session, Claude writes a summary for next time

That's it. No servers, no databases, no API keys.

## The 5-Minute Version

### Why Claude Code Forgets You

Claude Code uses a new context window for each session. When you close a terminal and open a new one, Claude has no idea:
- Who you are
- What project you were working on
- What decisions you made yesterday
- How you prefer to receive help

### How Memory Machine Fixes This

**The trick:** Claude Code automatically loads `~/.claude/CLAUDE.md` into every session's system prompt. This file tells Claude to read your memory files before it responds to anything.

**The memory files** are plain markdown stored in `~/.claude/projects/{your-project}/memory/`. They contain:

- **Who you are** (`user_*.md`) — your role, expertise, preferences
- **How you work** (`feedback_*.md`) — corrections and confirmed approaches
- **What's happening** (`project_*.md`) — active work, deadlines, decisions
- **Where things are** (`reference_*.md`) — external systems, dashboards, docs
- **What happened last** (`episodic_last_session.md`) — bridge between sessions
- **History** (`episodic_sessions.md`) — rolling log of past sessions

### The Session Lifecycle

```
┌─ SESSION START ──────────────────────────┐
│                                          │
│  CLAUDE.md loads automatically           │
│  Claude reads MEMORY.md index            │
│  Claude reads last session summary       │
│  Claude reads relevant memory files      │
│                                          │
│  Result: Claude knows who you are        │
│  and what you've been doing              │
│                                          │
├─ DURING SESSION ─────────────────────────┤
│                                          │
│  You work normally with Claude           │
│  Claude learns new things about you      │
│  Claude saves important learnings        │
│  (Optional: hook pushes to Mem0 cloud)   │
│                                          │
├─ SESSION END ────────────────────────────┤
│                                          │
│  Claude writes session summary           │
│  Claude updates memory index             │
│  Claude appends to session log           │
│                                          │
│  Result: Next session starts with        │
│  full context                            │
│                                          │
└──────────────────────────────────────────┘
```

### What Makes This Different

Most AI memory systems use RAG — they compress your conversations into summaries, embed them, and search. The problem: **summaries are lossy**.

Claude Memory Machine follows the MemMachine paper's approach:
- **Store raw details** (episodic memory), not just AI-generated summaries
- **Preserve context** (what was happening around a decision), not just the decision
- **Layer memory types** (STM + episodic + profile), like human cognition

## Customization

### Adding Memories Manually

Create any `.md` file in your memory directory:

```markdown
---
name: My Coding Style
description: Prefers functional programming, minimal dependencies
type: feedback
---

Use functional patterns over OOP when possible.
**Why:** User finds FP more readable and testable.
**How to apply:** Default to map/filter/reduce, pure functions, immutable data.
```

Then add it to MEMORY.md:
```
- [Coding Style](feedback_coding_style.md) — Functional > OOP, minimal deps
```

### Per-Project Memories

Each project directory can have its own memory:
```
~/my-project/.claude/memory/MEMORY.md
```

These load in addition to the global memory when working in that directory.

### Mem0 Cloud Integration

For ground truth preservation (the raw, uncompressed record of everything):

```bash
./install.sh --with-mem0 --mem0-key YOUR_KEY
```

This adds a hook that pushes every Write/Edit/Bash action to Mem0's cloud. Your local memory files handle profile and episodic summaries; Mem0 stores the raw ground truth.

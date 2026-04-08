# Claude Memory Machine

**Give Claude Code a real memory. Every session. Every directory. Forever.**

Inspired by the [MemMachine paper](docs/paper-summary.md) (Wang et al., 2026) — a ground-truth-preserving memory system that achieves 93% accuracy on complex memory benchmarks while using 80% fewer tokens than existing solutions.

Claude Memory Machine brings MemMachine's three-tier cognitive architecture to Claude Code CLI, so your AI assistant remembers you across every session, every project, every terminal window.

```
              Before                              After
    ┌─────────────────────┐            ┌─────────────────────┐
    │  "Who are you?"     │            │  "Welcome back.     │
    │  "What project?"    │            │   Last time we      │
    │  "Remind me what    │    ──>     │   fixed the auth    │
    │   we did last time" │            │   bug. Ready to     │
    │  "Start over..."    │            │   continue?"        │
    └─────────────────────┘            └─────────────────────┘
         Stateless AI                    AI with Memory
```

---

## Quick Start (< 2 minutes)

```bash
git clone https://github.com/YOUR_USERNAME/claude-memory-machine.git
cd claude-memory-machine
chmod +x install.sh
./install.sh
```

That's it. Open any new Claude Code session — it remembers.

---

## What It Does

| Layer | Cognitive Model | Implementation | Speed | Purpose |
|-------|----------------|----------------|-------|---------|
| **Layer 1** | Structured Memory | memorymesh MCP (SQLite + FTS5) | <10ms | Project details, architecture, credentials |
| **Layer 2** | Episodic Memory | Mem0 Cloud (semantic vectors) | ~500ms | Deep history, cross-project patterns (1000+ memories) |
| **Layer 3** | Profile Memory | Local markdown files with frontmatter | ~50ms | Who you are, how you work, behavioral preferences |

### The Key Insight (from MemMachine paper)

> "How data is recalled matters more than how it is stored, provided storage preserves ground truth."

Most AI memory systems compress your conversations into lossy summaries. Claude Memory Machine stores **raw episodic records** alongside distilled profiles, then uses **contextualized retrieval** — pulling not just matching facts, but the surrounding conversational context that makes those facts meaningful.

### v2: Three-Layer Architecture

The v2 system uses **three complementary memory layers**, each optimized for different speed/depth tradeoffs:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: memorymesh MCP    ← FAST (local FTS5, <10ms) │
│           Structured, importance-scored, tagged          │
│           Project details, architecture, credentials     │
│                                                          │
│  Layer 2: Mem0 Cloud        ← DEEP (semantic vectors)   │
│           1000+ raw memories, auto-captured              │
│           Semantic search across months of history        │
│                                                          │
│  Layer 3: Local Markdown    ← CURATED (human-readable)  │
│           Profile, feedback, project context              │
│           Editable, version-controlled                   │
│                                                          │
│  Orchestrator: CLAUDE.md    ← BRAIN (queries all 3)     │
└─────────────────────────────────────────────────────────┘
```

On every session start, Claude queries **all three layers simultaneously**, synthesizes the context, and greets you naturally — like a colleague who remembers every conversation you've ever had.

---

## Architecture

```
~/.claude/
├── CLAUDE.md                          # Global brain — loaded EVERY session
├── settings.json                      # Hooks for automatic memory capture
└── projects/
    └── {your-project}/
        └── memory/
            ├── MEMORY.md              # Index — the "table of contents" of your mind
            ├── episodic_last_session.md    # Tier 1: STM bridge
            ├── episodic_sessions.md        # Tier 2: Rolling session log
            ├── user_*.md                   # Tier 3: Profile memories
            ├── feedback_*.md              # Tier 3: Behavioral preferences
            ├── project_*.md               # Tier 3: Active project context
            └── reference_*.md             # Tier 3: External system pointers
```

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     SESSION START                             │
│                                                              │
│  1. CLAUDE.md loads (global, every directory)                │
│  2. Read MEMORY.md index                                     │
│  3. Read episodic_last_session.md (STM bridge)              │
│  4. Read relevant memory files based on user's first msg    │
│  5. Silently integrate — respond with full context           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                     DURING SESSION                           │
│                                                              │
│  - Claude learns new facts → writes to memory/ files        │
│  - PostToolUse hook → captures actions to Mem0 (optional)   │
│  - Profile memory updated when user shares preferences      │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                     SESSION END                              │
│                                                              │
│  1. Write session summary → episodic_last_session.md        │
│  2. Append to rolling log → episodic_sessions.md            │
│  3. Update MEMORY.md index if new memories created          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Memory Types

### User Memories (`user_*.md`)
Who you are. Your role, expertise, preferences.
```markdown
---
name: User Role
description: Software engineer, 5 years Python, new to Rust
type: user
---
Senior Python developer at Acme Corp, transitioning to Rust for the new microservices platform.
Prefers concise explanations with code examples over theory.
```

### Feedback Memories (`feedback_*.md`)
How you want Claude to behave. Corrections AND confirmations.
```markdown
---
name: Testing Approach
description: Always use real databases in integration tests, never mocks
type: feedback
---
Integration tests must hit a real database, not mocks.
**Why:** Prior incident where mock/prod divergence masked a broken migration.
**How to apply:** When writing or reviewing test code, ensure DB tests use testcontainers or a real test database.
```

### Project Memories (`project_*.md`)
What's happening in your work right now.
```markdown
---
name: Auth Rewrite
description: Auth middleware rewrite driven by compliance, not tech debt
type: project
---
Auth middleware rewrite is driven by legal/compliance requirements around session token storage.
**Why:** Legal flagged current implementation for non-compliant session storage.
**How to apply:** Scope decisions should favor compliance over ergonomics.
```

### Reference Memories (`reference_*.md`)
Where to find things in external systems.
```markdown
---
name: Bug Tracker
description: Pipeline bugs tracked in Linear project INGEST
type: reference
---
Pipeline bugs are tracked in Linear project "INGEST".
API latency dashboard: grafana.internal/d/api-latency (oncall watches this).
```

---

## Configuration

### Basic (No Cloud — 100% Local)

The default install uses only local files. No API keys, no cloud services, no data leaves your machine.

```bash
./install.sh
```

### Advanced (With Mem0 Cloud — Ground Truth Preservation)

For full MemMachine-style episodic ground truth storage, add Mem0 integration:

```bash
./install.sh --with-mem0
# You'll be prompted for your Mem0 API key
```

This adds a PostToolUse hook that pushes raw session actions to Mem0's cloud, giving you a searchable archive of every interaction.

### Custom Memory Directory

```bash
./install.sh --memory-dir /path/to/your/memory
```

---

## How It Compares

Based on benchmarks from the MemMachine paper (Wang et al., 2026):

| System | LoCoMo Score | Token Usage | Ground Truth | Open Source |
|--------|-------------|-------------|--------------|-------------|
| **MemMachine** | **91.69%** | **~4.2M** | **Preserved** | **Yes** |
| Mem0 | 66.88% | ~19.2M | Partial | Partial |
| Zep | 75.14% | N/A | Partial | Partial |
| Memobase | 75.78% | N/A | Partial | Yes |
| OpenAI Memory | 52.90% | N/A | No | No |
| LangMem | 58.10% | N/A | No | Yes |

### Key Results from the Paper

- **93.0%** accuracy on LongMemEval (ICLR 2025 benchmark)
- **93.2%** on HotpotQA hard set with Retrieval Agent
- **~80%** fewer input tokens than Mem0
- **Retrieval-stage optimizations dominate**: retrieval depth (+4.2%), context formatting (+2.0%), search prompt design (+1.8%) each outweigh ingestion-stage chunking (+0.8%)

---

## The Science Behind It

### Three Memory Tiers (Cognitive Science Foundation)

Based on Tulving's (1972) episodic-semantic distinction and the Atkinson-Shiffrin multi-store model:

```
┌─────────────────────────────────────────────────┐
│           TIER 1: SHORT-TERM MEMORY             │
│                                                 │
│  Current conversation context window            │
│  + Last session summary (STM bridge)            │
│  Capacity: Limited (context window)             │
│  Duration: Current session                      │
│                                                 │
├─────────────────────────────────────────────────┤
│          TIER 2: EPISODIC MEMORY                │
│                                                 │
│  Raw conversation records (ground truth)        │
│  Rolling session summaries                      │
│  What happened, when, in what context           │
│  Capacity: Unlimited (file-based)               │
│  Duration: Persistent                           │
│                                                 │
├─────────────────────────────────────────────────┤
│          TIER 3: PROFILE MEMORY                 │
│                                                 │
│  User preferences, facts, patterns              │
│  Behavioral feedback & corrections              │
│  Project context & references                   │
│  Capacity: Curated (quality > quantity)          │
│  Duration: Persistent, evolving                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Contextualized Retrieval

Traditional RAG grabs isolated matching chunks. MemMachine's contextualized retrieval expands matches to include surrounding conversational turns:

```
Query: "What did we decide about the database?"

Traditional RAG:
  → "We'll use PostgreSQL" (isolated fact, no context)

Contextualized Retrieval:
  → User asked about scaling requirements          (context)
  → Team discussed MySQL vs PostgreSQL tradeoffs   (context)  
  → Decision: PostgreSQL for JSONB support         (nucleus match)
  → Action item: Set up read replicas by Friday    (context)
```

### Ground Truth Preservation

```
┌────────────────────────────────┐
│     LLM-Extracted Memory       │
│                                │
│  "User likes Italian food"     │  ← Lossy summary
│  (Original context lost)       │     What if they said
│                                │     "I liked that Italian
│                                │     place, but only for
│                                │     lunch meetings"?
└────────────────────────────────┘

┌────────────────────────────────┐
│   Ground Truth + Profile       │
│                                │
│  Episode: "I liked that        │  ← Raw record preserved
│  Italian place on 5th, but     │
│  only for lunch meetings.      │
│  For dinner I prefer Thai."    │
│                                │
│  Profile: Italian (lunch),     │  ← Distilled on top,
│  Thai (dinner)                 │     not instead of
└────────────────────────────────┘
```

---

## Uninstall

```bash
./uninstall.sh
```

This removes only the Claude Memory Machine configuration. Your memory files are preserved (you choose whether to delete them).

---

## FAQ

**Q: Does my data leave my machine?**
A: With the default install, no. Everything is local markdown files. The optional Mem0 integration sends action summaries to Mem0's cloud.

**Q: Does this work with Claude Code in VS Code / JetBrains?**
A: Yes. The global `CLAUDE.md` is loaded by Claude Code regardless of interface — CLI, VS Code extension, JetBrains plugin, desktop app, or web.

**Q: What about different projects in different directories?**
A: The global `~/.claude/CLAUDE.md` loads in every directory. Project-specific memories can also be added to each project's own `.claude/` directory.

**Q: How much storage does this use?**
A: Minimal. Memory files are small markdown files. Even after months of heavy use, expect < 1MB total.

**Q: Can I use this with other AI coding tools?**
A: The architecture is Claude Code-specific (uses `CLAUDE.md` and Claude Code hooks), but the memory file format is plain markdown — portable to any system.

**Q: Will Claude actually read these files?**
A: Yes. `~/.claude/CLAUDE.md` is automatically loaded into every Claude Code session's system prompt. It's a first-class feature of Claude Code.

---

## Contributing

PRs welcome. Key areas:

- **Memory retrieval strategies** — smarter ways to select which memories to load
- **Session summarization** — better episodic compression
- **Multi-agent memory sharing** — shared memory across team members
- **Benchmarking** — test memory recall accuracy with synthetic conversations
- **Integration with other memory backends** — Chroma, Pinecone, Weaviate

---

## Credits

- **MemMachine Paper**: Wang, S., Yu, E., Love, O., Zhang, T., Wong, T., Scargall, S., & Fan, C. (2026). *MemMachine: A Ground-Truth-Preserving Memory System for Personalized AI Agents.* arXiv:2604.04853v1.
- **Cognitive Science Foundations**: Tulving (1972) episodic-semantic distinction, Atkinson-Shiffrin (1968) multi-store model.
- **Claude Code**: Anthropic's CLI for Claude — the runtime that makes this possible.

---

## License

Apache 2.0 — same as the original MemMachine.

---

*Your AI assistant just got a real memory.*

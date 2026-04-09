# Claude Memory Machine

**Give Claude Code a real memory. Every session. Every directory. Forever.**

Inspired by the [MemMachine paper](docs/paper-summary.md) (Wang et al., 2026) — a ground-truth-preserving memory system that achieves 93% accuracy while using 80% fewer tokens than existing solutions.

```
              Before                              After
    ┌─────────────────────┐            ┌─────────────────────────────┐
    │  "Who are you?"     │            │  "Hey. Last session we      │
    │  "What project?"    │            │   pushed the auth fix.      │
    │  "Remind me what    │    ──>     │   Workday is live 15/15.    │
    │   we did last time" │            │   NetSuite still blocked    │
    │  "Start over..."    │            │   on AWS creds. What next?" │
    └─────────────────────┘            └─────────────────────────────┘
         Stateless AI                    AI with 934 memories
                                         across 3 layers + 5 agents
```

---

## Live Results (Not Benchmarks — Real Data)

From a production run on April 8, 2026 — processing 1,353 real memories from 2+ weeks of daily development:

| Metric | Before | After |
|--------|--------|-------|
| Mem0 noise | 386 memories (29%) | **0 (cleaned)** |
| Mem0 duplicates | 202 redundant | **0 (deduped)** |
| memorymesh structured memories | 19 | **158 (+731%)** |
| Average importance score | ~0.5 | **0.78** |
| Decision→outcome chains tracked | 0 | **11** |
| Self-adjusted importance scores | 0 | **9** |
| Blocker patterns detected | 0 | **33** |
| Active project threads | 0 | **8 (auto-detected)** |

> **[Full results with all agent outputs →](docs/RESULTS.md)**

---

## Quick Start

```bash
git clone https://github.com/samcolibri/claude-memory-machine.git
cd claude-memory-machine
chmod +x install.sh
./install.sh                    # Local only, no cloud, < 2 minutes
./install.sh --with-mem0        # + Mem0 cloud for ground truth storage
```

Open any new Claude Code session. Say anything. It remembers.

---

## Architecture: Three Layers + Five Agents

### The Three Memory Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: memorymesh MCP        ← FAST (<10ms)              │
│  Local SQLite + FTS5 full-text search                       │
│  Importance-scored, tagged, structured                      │
│  158 memories, avg importance 0.78                          │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Mem0 Cloud            ← DEEP (semantic vectors)   │
│  Auto-captured via PostToolUse hook                         │
│  758 clean memories (post-consolidation)                    │
│  Semantic search across weeks of history                    │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Local Markdown        ← CURATED (human-readable)  │
│  18 files: user, feedback, project, reference               │
│  Includes auto-generated digital twin                       │
│  Editable, version-controlled, portable                     │
├─────────────────────────────────────────────────────────────┤
│  Orchestrator: ~/.claude/CLAUDE.md                          │
│  Queries ALL 3 layers on every session startup              │
│  Auto-welcomes user with synthesized context                │
└─────────────────────────────────────────────────────────────┘
```

Each layer serves a different speed/depth tradeoff:

| Layer | Speed | Depth | Best For |
|-------|-------|-------|----------|
| memorymesh | <10ms | Structured facts | Architecture, credentials, decisions |
| Mem0 Cloud | ~500ms | Semantic search | "What happened 3 weeks ago?", cross-project |
| Local Markdown | ~50ms | Curated profile | Who you are, how you work, preferences |

### The Five Autonomous Agents

| Agent | Level | Schedule | What It Does |
|-------|-------|----------|-------------|
| **Consolidator** | L3 | Daily 1 AM | Cleans noise, deduplicates, promotes high-value memories |
| **Pattern Detector** | L3 | Daily 11 PM | Finds recurring themes, project threads, blockers |
| **Daily Briefing** | L3 | Daily 5:30 AM | Generates morning briefing for session bridge |
| **Digital Twin** | L4 | Weekly Sun 2 AM | Builds comprehensive user model from all memories |
| **Causal Tracker** | L4 | Weekly Fri 11 PM | Tracks decision→outcome chains, self-evolves scores |

---

## The Session Lifecycle

```
┌─ BEFORE YOUR FIRST PROMPT ──────────────────────────────────┐
│                                                              │
│  ~/.claude/CLAUDE.md auto-loads (global, every directory)    │
│  → memorymesh queried (structured local, <10ms)              │
│  → Mem0 searched (semantic cloud, ~500ms)                    │
│  → Session bridge read (last session summary)                │
│  → Relevant markdown files loaded                            │
│  → Claude greets you naturally with full context             │
│                                                              │
├─ DURING YOUR SESSION ────────────────────────────────────────┤
│                                                              │
│  You work normally with Claude                               │
│  → PostToolUse hook auto-captures actions to Mem0            │
│  → Claude saves important learnings to memorymesh            │
│  → Profile memories updated when you share preferences       │
│                                                              │
├─ AFTER YOUR SESSION ─────────────────────────────────────────┤
│                                                              │
│  Claude writes session summary → episodic_last_session.md    │
│  Claude appends to rolling log → episodic_sessions.md        │
│                                                              │
├─ OVERNIGHT (Autonomous Agents) ──────────────────────────────┤
│                                                              │
│  1 AM: Consolidator cleans noise + deduplicates              │
│  5:30 AM: Daily Briefing generated for morning session       │
│  11 PM: Pattern Detector analyzes the day                    │
│  Weekly: Digital Twin + Causal Tracker evolve the model      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Level 4: Self-Evolving Memory

This isn't just storage. The system **evolves itself**:

### Causal Tracking
Decisions are linked to outcomes. The system tracks what worked and what didn't:

```
Decision: "Committed ICP2 decision brief with live-verified numbers"
  → Outcome: POSITIVE (committed V5 Progressive Autonomy engine)
  → memorymesh importance: automatically boosted

Decision: "Created standalone docs without paired code"
  → Outcome: NEGATIVE (100% failure rate detected)
  → Insight stored: "Always pair docs with functional code"
```

### Self-Adjusting Importance
Memories that lead to positive outcomes get their importance scores automatically increased. Memories associated with failures are preserved (failures are valuable to remember) but differently weighted. **The system literally learns what matters.**

### Digital Twin
An auto-generated comprehensive model of who you are:

```
EXPERTISE:   Claude(217), GTM(175), Git(165), QA(109), Bash(89)
STYLE:       Moves fast (31%), Detail-oriented (25%), Autonomous (18%)
PEAK HOURS:  10 AM, 6 AM, midnight
PEAK DAYS:   Monday, Friday, Thursday
FOOTPRINT:   934 memories across 3 systems
```

This model is used by Claude to calibrate how it helps you — more direct with an experienced developer, more architectural with a systems thinker.

---

## Memory Types

### User Memories (`user_*.md`)
```markdown
---
name: User Role
description: Software engineer, 5 years Python, new to Rust
type: user
---
Senior Python developer at Acme Corp, transitioning to Rust.
Prefers concise explanations with code examples over theory.
```

### Feedback Memories (`feedback_*.md`)
```markdown
---
name: Testing Approach
description: Always use real databases in integration tests
type: feedback
---
Integration tests must hit a real database, not mocks.
**Why:** Prior incident where mock/prod divergence masked a broken migration.
**How to apply:** Use testcontainers or a real test database.
```

### Project Memories (`project_*.md`)
```markdown
---
name: Auth Rewrite
description: Auth middleware rewrite driven by compliance, not tech debt
type: project
---
Auth middleware rewrite is driven by legal/compliance requirements.
**Why:** Legal flagged current implementation for non-compliant session storage.
**How to apply:** Favor compliance over ergonomics in scope decisions.
```

### Reference Memories (`reference_*.md`)
```markdown
---
name: Bug Tracker
description: Pipeline bugs tracked in Linear project INGEST
type: reference
---
Pipeline bugs: Linear project "INGEST"
Latency dashboard: grafana.internal/d/api-latency (oncall watches this)
```

---

## The Science

Based on the [MemMachine paper](docs/paper-summary.md) (Wang et al., 2026):

> "How data is recalled matters more than how it is stored, provided storage preserves ground truth."

| System | LoCoMo Score | Tokens Used | Ground Truth |
|--------|-------------|-------------|--------------|
| **MemMachine** | **91.69%** | **~4.2M** | **Preserved** |
| Mem0 | 66.88% | ~19.2M | Partial |
| Zep | 75.14% | N/A | Partial |
| OpenAI Memory | 52.90% | N/A | No |

Key findings applied in this project:
- **Retrieval > Ingestion**: How you recall matters more than how you store (+4.2% from retrieval depth alone)
- **Ground Truth > Summaries**: Raw episodes + smart search beats LLM-compressed summaries
- **Contextualized > Isolated**: Episode clusters with surrounding context beat isolated fact retrieval
- **Three cognitive tiers**: STM + Episodic + Semantic, matching human memory architecture

---

## File Structure

```
~/.claude/
├── CLAUDE.md                              # The brain — auto-loads every session
├── scripts/
│   └── mem0_recall.sh                     # Mem0 semantic search
├── memory-agents/                         # Level 3 + 4 autonomous agents
│   ├── memory_agent.py                    # Master orchestrator
│   ├── consolidator.py                    # L3: Noise cleanup + dedup
│   ├── pattern_detector.py                # L3: Theme + blocker detection
│   ├── daily_briefing.py                  # L3: Morning briefing generator
│   ├── digital_twin.py                    # L4: User model builder
│   ├── causal_tracker.py                  # L4: Decision→outcome tracking
│   ├── config.py                          # Shared configuration
│   ├── mem0_client.py                     # Mem0 REST API client
│   ├── memorymesh_client.py               # memorymesh SQLite client
│   └── logs/                              # Agent run logs
└── projects/{your-project}/memory/
    ├── MEMORY.md                          # Index
    ├── episodic_last_session.md           # Session bridge (STM)
    ├── episodic_sessions.md               # Rolling log
    ├── digital_twin.md                    # Auto-generated user model
    ├── user_*.md                          # Profile memories
    ├── feedback_*.md                      # Behavioral preferences
    ├── project_*.md                       # Active project context
    └── reference_*.md                     # External system pointers
```

---

## Configuration

### Local Only (Default)
```bash
./install.sh
```
Zero cloud, zero API keys. Memory lives in local markdown files + memorymesh SQLite.

### With Mem0 Cloud
```bash
./install.sh --with-mem0
```
Adds semantic vector search across all your sessions. Auto-captures every action.

### With Level 3 + 4 Agents
```bash
# After install, set up cron schedule:
bash ~/.claude/memory-agents/install_cron.sh

# Or run manually:
python3 ~/.claude/memory-agents/memory_agent.py           # All agents
python3 ~/.claude/memory-agents/memory_agent.py twin       # Just digital twin
python3 ~/.claude/memory-agents/memory_agent.py --dry-run  # Preview changes
```

---

## FAQ

**Does my data leave my machine?**
Default install: no. With Mem0: action summaries go to Mem0 cloud. With Claude API agents: memory text goes to Anthropic for analysis.

**Does this work in VS Code / JetBrains / Desktop / Web?**
Yes. `~/.claude/CLAUDE.md` loads in every Claude Code interface.

**How much storage?**
Minimal. 158 memorymesh memories = 68KB. 18 markdown files < 100KB. Even after months: < 1MB total.

**Will Claude actually read the memory files?**
Yes. `~/.claude/CLAUDE.md` is a first-class Claude Code feature — automatically loaded into every session's system prompt.

**What if I have 10,000+ memories?**
The consolidator keeps things clean. For massive scale, use the full [MemMachine server](https://github.com/MemMachine/MemMachine).

---

## Credits

- **MemMachine Paper**: Wang et al. (2026). *A Ground-Truth-Preserving Memory System for Personalized AI Agents.* arXiv:2604.04853v1.
- **Cognitive Science**: Tulving (1972) episodic-semantic distinction, Atkinson-Shiffrin (1968) multi-store model.
- **Claude Code**: Anthropic's CLI — the runtime that makes this possible.
- **memorymesh**: Local SQLite + FTS5 memory engine.
- **Mem0**: Semantic vector memory cloud.

## License

Apache 2.0

---

*Your AI assistant just got a real memory. And it evolves.*

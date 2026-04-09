# Architecture: Claude Memory Machine v2

## Design Philosophy

Three principles from the MemMachine paper, applied to Claude Code:

1. **Ground truth preservation** — Store raw episodic records, not just AI-compressed summaries
2. **Retrieval over ingestion** — Invest in smart recall, not heavy processing at write time
3. **Layered cognitive architecture** — Different memory types at different speeds for different purposes

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      CLAUDE CODE SESSION                          │
│                                                                   │
│  User opens terminal (any directory, any IDE)                     │
│  └── CLAUDE.md auto-loads (global, first-class Claude feature)   │
│      └── Startup Protocol:                                        │
│          ├── memorymesh: get_context() → <10ms local FTS5        │
│          ├── Mem0: mem0_recall.sh → ~500ms semantic search       │
│          ├── Markdown: MEMORY.md + session bridge → ~50ms        │
│          └── Synthesize + welcome user naturally                  │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                     MEMORY LAYERS                                 │
│                                                                   │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │ LAYER 1           │ │ LAYER 2           │ │ LAYER 3          │ │
│  │ memorymesh MCP    │ │ Mem0 Cloud        │ │ Local Markdown   │ │
│  │                   │ │                   │ │                  │ │
│  │ SQLite + FTS5     │ │ Semantic vectors  │ │ YAML frontmatter │ │
│  │ 158 memories      │ │ 758 memories      │ │ 18 files         │ │
│  │ Importance: 0.78  │ │ Auto-captured     │ │ Human-editable   │ │
│  │ 7 sources         │ │ 100% signal       │ │ 5 types          │ │
│  │ <10ms queries     │ │ ~500ms queries    │ │ ~50ms reads      │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                   AUTONOMOUS AGENTS                               │
│                                                                   │
│  ┌─ Level 3 (Proactive) ──────────────────────────────────────┐ │
│  │ Consolidator    : Clean noise, dedup, promote to memorymesh │ │
│  │ Pattern Detector: Topic clusters, project threads, blockers │ │
│  │ Daily Briefing  : Morning context for session bridge        │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌─ Level 4 (Self-Evolving) ──────────────────────────────────┐ │
│  │ Digital Twin    : Comprehensive user model from all memory  │ │
│  │ Causal Tracker  : Decision→outcome chains, importance adj.  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│                      HOOKS                                        │
│                                                                   │
│  PostToolUse → mem0_hook.sh → every Write/Edit/Bash action       │
│                → pushed to Mem0 cloud (ground truth capture)      │
└──────────────────────────────────────────────────────────────────┘
```

## How It Maps to MemMachine

| MemMachine Component | Our Implementation |
|---------------------|-------------------|
| PostgreSQL + pgvector | memorymesh (SQLite + FTS5) |
| Neo4j graph store | Cross-references in MEMORY.md + memorymesh tags |
| Embedding service | Mem0 cloud (semantic vectors) + Claude's understanding |
| REST API | memorymesh MCP tools + Mem0 REST API |
| Sentence-level indexing | memorymesh content + frontmatter descriptions |
| Contextualized retrieval | Three-layer synthesis in CLAUDE.md protocol |
| Profile extraction | Auto-memory system + Digital Twin agent |
| STM window | Context window + episodic_last_session.md |
| Multi-tenancy | Per-project memory directories |
| LLM-based summarization | Daily Briefing agent |

## Agent Architecture

```
memory_agent.py (Master Orchestrator)
├── consolidator.py ──→ mem0_client.py ──→ Mem0 REST API
│                   └─→ memorymesh_client.py ──→ SQLite DB
├── pattern_detector.py ──→ Both clients + Claude API
├── daily_briefing.py ──→ Both clients + Claude API
├── digital_twin.py ──→ Both clients + Claude API
├── causal_tracker.py ──→ Both clients + Claude API
└── config.py (shared configuration, API keys, thresholds)
```

### Agent Design Principles

1. **Claude API is optional** — Every agent has a heuristic fallback. If no API key or credits, agents still produce useful results.
2. **Idempotent** — Running an agent twice produces the same result. Safe to re-run.
3. **Non-destructive** — Consolidator removes noise but never touches signal. Digital twin replaces its own previous output, not other memories.
4. **Self-evolving** — Causal tracker adjusts importance scores automatically. The system gets better at knowing what matters.

## Data Flow: Write Path

```
User action in Claude Code
  └── PostToolUse hook fires
      └── mem0_hook.sh sends to Mem0 cloud (background, non-blocking)
          └── Raw action stored as episodic ground truth

Claude learns something important
  └── memorymesh remember_memory(content, importance, tags)
      └── Structured, searchable, importance-scored

User shares preference or correction
  └── Written to feedback_*.md in memory/
      └── Human-readable, editable, indexed in MEMORY.md
```

## Data Flow: Read Path (Session Start)

```
CLAUDE.md loads (automatic)
  ├── memorymesh get_context(query, limit=10)         ← <10ms
  ├── mem0_recall.sh "relevant query" 10               ← ~500ms
  ├── Read MEMORY.md index                             ← ~10ms
  ├── Read episodic_last_session.md                    ← ~10ms
  └── Read relevant markdown files                     ← ~30ms
      └── Synthesized into natural welcome             ← Total: <1s
```

## Data Flow: Evolution Path (Agents)

```
Overnight:
  Consolidator → Cleans Mem0 → Promotes to memorymesh
  Pattern Detector → Analyzes → Writes report to memorymesh
  Daily Briefing → Generates → Writes to session bridge

Weekly:
  Digital Twin → Analyzes ALL memories → Updates user model
  Causal Tracker → Links decisions→outcomes → Adjusts importance
```

## Limitations vs. Full MemMachine

| Capability | MemMachine | Memory Machine v2 |
|-----------|-----------|-------------------|
| Sentence-level embeddings | Yes | No (Mem0 handles this) |
| Vector similarity search | Yes (pgvector) | Yes (Mem0 cloud) |
| Multi-hop Retrieval Agent | Yes | No (single-pass) |
| Cross-encoder reranking | Yes | No (Claude decides) |
| Graph traversal | Yes (Neo4j) | No |
| Scale to 100K+ episodes | Yes | ~1K-5K comfortable |
| Self-evolving importance | No | **Yes** (causal tracker) |
| Digital twin | No | **Yes** |
| Autonomous agents | No | **Yes** (5 agents) |
| Zero infrastructure | No | **Yes** |

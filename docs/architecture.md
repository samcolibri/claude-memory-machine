# Architecture: Claude Memory Machine

## Design Philosophy

Claude Memory Machine adapts the MemMachine paper's server-side architecture into a lightweight, file-based system that runs entirely within Claude Code's existing infrastructure. No databases, no servers, no API keys required (unless you opt into Mem0 cloud).

**Core principle:** Use Claude Code's native features (CLAUDE.md auto-loading, hooks, file-based memory) to implement the same cognitive architecture that MemMachine achieves with PostgreSQL + Neo4j + embedding services.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLAUDE CODE SESSION                       │
│                                                                  │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │   User's      │     │         Claude's Context Window       │  │
│  │   Terminal     │────>│                                      │  │
│  │   (any dir)    │     │  CLAUDE.md (global, auto-loaded)     │  │
│  └──────────────┘     │  ┌─────────────────────────────────┐ │  │
│                        │  │  Startup Protocol:               │ │  │
│                        │  │  1. Read MEMORY.md index         │ │  │
│                        │  │  2. Read last session summary    │ │  │
│                        │  │  3. Read relevant memories       │ │  │
│                        │  │  4. Integrate silently           │ │  │
│                        │  └─────────────────────────────────┘ │  │
│                        └──────────────────────────────────────┘  │
│                                      │                           │
│                                      ▼                           │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    MEMORY LAYER                            │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │   │
│  │  │   TIER 1     │  │   TIER 2      │  │    TIER 3       │ │   │
│  │  │   STM        │  │   Episodic    │  │    Profile      │ │   │
│  │  │              │  │              │  │                 │ │   │
│  │  │ Context      │  │ session_log  │  │ user_*.md       │ │   │
│  │  │ Window       │  │ last_session │  │ feedback_*.md   │ │   │
│  │  │              │  │              │  │ project_*.md    │ │   │
│  │  │              │  │ [Mem0 Cloud] │  │ reference_*.md  │ │   │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘ │   │
│  │                                                           │   │
│  │  Index: MEMORY.md (< 200 lines, table of contents)       │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                      │                           │
│                                      ▼                           │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                  HOOKS LAYER (Optional)                    │   │
│  │                                                           │   │
│  │  PostToolUse ──> mem0_hook.sh ──> Mem0 Cloud API         │   │
│  │  (Write|Edit|Bash events push to ground truth store)     │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## How It Maps to MemMachine

| MemMachine Component | Claude Memory Machine Equivalent |
|---------------------|----------------------------------|
| PostgreSQL + pgvector | Markdown files + Claude's native search |
| Neo4j graph store | Cross-references in MEMORY.md index |
| Embedding service | Claude's semantic understanding of file content |
| REST API / Python SDK | Claude Code's Read/Write/Edit tools |
| Sentence-level indexing | Frontmatter descriptions in memory files |
| Episode clusters | Full memory file reads (not just titles) |
| Contextualized retrieval | Instructions to cross-reference and read full files |
| Profile extraction | Auto-memory system with structured types |
| STM window | Context window + episodic_last_session.md |
| Multi-tenancy | Per-project memory directories |

## File Format

Every memory file uses YAML frontmatter for machine-readable metadata:

```markdown
---
name: Human-readable name
description: One-line description used for relevance matching
type: user|feedback|project|reference
---

Content body. For feedback and project types:

Statement of the rule or fact.

**Why:** The motivation behind this.
**How to apply:** When and where this guidance kicks in.
```

### Why Frontmatter?

1. **Relevance matching**: The `description` field acts like an embedding — Claude uses it to decide which files to read in full
2. **Type routing**: `type` determines how the memory is used (personalization vs. behavior vs. context)
3. **Index efficiency**: MEMORY.md only needs one-line entries; full content lives in individual files

## Data Flow: Complete Lifecycle

### 1. Installation
```
install.sh
  ├── Creates ~/.claude/CLAUDE.md (global brain)
  ├── Creates memory/ directory with templates
  ├── Configures hooks in settings.json (optional Mem0)
  └── Verifies all components
```

### 2. Session Start (Automatic)
```
User opens Claude Code (any directory)
  └── CLAUDE.md auto-loads (Claude Code native feature)
      └── Startup Protocol triggers:
          ├── Read MEMORY.md (what memories exist?)
          ├── Read episodic_last_session.md (what happened last time?)
          ├── Read relevant memory files (based on user's first message)
          └── Integrate silently (no "I'm loading memories" announcement)
```

### 3. During Session
```
User and Claude interact
  ├── Claude learns new facts → writes to memory/ files
  ├── Claude receives corrections → saves feedback memories
  ├── PostToolUse hook fires (if Mem0 enabled):
  │   └── Raw action pushed to Mem0 cloud (ground truth)
  └── Profile memory updated as user shares preferences
```

### 4. Session End
```
Conversation concludes
  ├── Claude writes session summary → episodic_last_session.md
  ├── Claude appends one-liner → episodic_sessions.md
  └── Claude updates MEMORY.md if new files were created
```

### 5. Next Session (The Magic)
```
User opens Claude Code again (possibly different directory!)
  └── CLAUDE.md loads → reads MEMORY.md → reads last session
      └── Claude naturally continues with full context
          "Welcome back. Last time we were working on..."
```

## Why This Works

### Claude Code's `~/.claude/CLAUDE.md` is the Key

This is a first-class Claude Code feature: any file at `~/.claude/CLAUDE.md` is automatically loaded into the system prompt of every Claude Code session, regardless of which directory the user is in.

This means:
- Open Claude Code in `~/projects/web-app/` → memory loads
- Open Claude Code in `~/Documents/research/` → memory loads  
- Open Claude Code in `/tmp/` → memory loads
- Open Claude Code via VS Code → memory loads
- Open Claude Code via JetBrains → memory loads

### Markdown is the Database

By using plain markdown files instead of a database:
- **Zero infrastructure**: No PostgreSQL, no Neo4j, no embedding service
- **Human readable**: You can open and edit your memories in any text editor
- **Version controllable**: Git track your memory evolution
- **Portable**: Copy your memory/ folder to any machine
- **Private**: Everything stays local, no cloud required

### Claude IS the Retrieval Engine

Instead of building a separate embedding + vector search pipeline, we leverage Claude's native ability to:
- Read the MEMORY.md index and understand relevance
- Decide which files to read based on the current query
- Cross-reference multiple memory files for complex questions
- Write structured memory files with proper metadata

This is essentially using Claude as both the "embedding model" and the "reranker" from MemMachine's architecture — but without the infrastructure overhead.

## Limitations vs. Full MemMachine

| Capability | MemMachine | Claude Memory Machine |
|-----------|------------|----------------------|
| Sentence-level embeddings | Yes | No (file-level) |
| Vector similarity search | Yes (pgvector) | No (semantic via Claude) |
| Sub-second retrieval | Yes | Depends on file count |
| Multi-hop Retrieval Agent | Yes | No (single-pass) |
| Automatic reranking | Yes (cross-encoder) | Manual (Claude decides) |
| Graph traversal | Yes (Neo4j) | No |
| Scale to 10K+ episodes | Yes | Limited (~100s of files) |
| Zero LLM cost for retrieval | Mostly | No (Claude reads files) |

### When You Need Full MemMachine

If you have thousands of sessions, need sub-second retrieval, or require multi-hop reasoning over massive conversation histories, use the full [MemMachine server](https://github.com/MemMachine/MemMachine).

Claude Memory Machine is designed for individual developers who want persistent memory across Claude Code sessions with zero infrastructure.

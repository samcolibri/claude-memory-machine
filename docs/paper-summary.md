# MemMachine: Paper Summary & Results

**Paper:** *MemMachine: A Ground-Truth-Preserving Memory System for Personalized AI Agents*
**Authors:** Shu Wang, Edwin Yu, Oscar Love, Tom Zhang, Tom Wong, Steve Scargall, Charles Fan
**Affiliation:** MemVerge, Inc.
**Date:** March 2026
**arXiv:** [2604.04853v1](https://arxiv.org/abs/2604.04853v1)
**License:** Apache 2.0
**Repository:** [github.com/MemMachine/MemMachine](https://github.com/MemMachine/MemMachine)

---

## The Problem

Today's AI agents are stateless across sessions. They remember you during a conversation but start completely fresh next time. Existing memory solutions (Mem0, Zep, LangMem) use LLMs to extract and compress facts from conversations — a process that is:

1. **Lossy** — AI summaries lose crucial details, context, and nuance
2. **Expensive** — LLM calls for every message extraction burn tokens
3. **Error-compounding** — extraction errors accumulate over time

## The Solution: Ground Truth Preservation

MemMachine takes a fundamentally different approach: **store entire conversational episodes intact**, then use smart retrieval to find relevant chunks when needed.

Instead of asking an LLM to extract "what's important" from each message (lossy), MemMachine stores the raw conversation and invests in better retrieval.

> **Key Insight:** "How data is recalled matters more than how it is stored, provided storage preserves ground truth."

## Three-Tier Architecture

### Tier 1: Short-Term Memory (STM)
- Configurable window of most recent episodes
- LLM-generated session summaries when window overflows
- Always available without retrieval step

### Tier 2: Episodic Memory (Long-Term)
- Raw conversational episodes stored at sentence level
- Each sentence gets its own embedding for fine-grained search
- Metadata: timestamp, producer, session ID, custom key-value pairs
- PostgreSQL + pgvector for vector search, Neo4j for graph traversal

### Tier 3: Profile Memory (Semantic)
- Extracted user facts, preferences, behavioral patterns
- Updated when new information contradicts existing data
- SQL-backed for retrieval and update

## Contextualized Retrieval

The key innovation. Traditional RAG grabs isolated matching chunks. MemMachine expands:

1. **Nucleus episode** found via embedding search
2. **Neighboring episodes** retrieved (1 preceding, 2 following) → episode cluster
3. **Clusters reranked** using cross-encoder
4. **Top-k clusters** provided to the LLM

This ensures the LLM receives conversational context, not just isolated facts.

## Retrieval Agent (Multi-Hop Reasoning)

For complex queries requiring multiple retrieval steps, MemMachine v0.3 introduces a Retrieval Agent:

```
ToolSelectAgent (LLM router)
├── ChainOfQuery (multi-hop dependency chains, up to 3 iterations)
├── SplitQuery (fan-out, 2-6 parallel sub-queries)
└── MemMachine (direct single-hop search)
```

All strategies delegate to the same underlying vector search — improvements propagate automatically.

## Benchmark Results

### LoCoMo (Long-term Conversational Memory)

| System | Overall Score |
|--------|-------------|
| **MemMachine** | **91.69%** |
| Memobase | 75.78% |
| Zep | 75.14% |
| Mem0 | 66.88% |
| LangMem | 58.10% |
| OpenAI Memory | 52.90% |

### LongMemEval (ICLR 2025)

Systematic ablation across 6 optimization dimensions, 500 questions:

| Optimization | Impact |
|-------------|--------|
| Retrieval depth (k: 20→30) | **+4.2%** |
| Answer model (GPT-5 → GPT-5-mini) | **+2.6%** |
| Context formatting | **+2.0%** |
| Search prompt design | **+1.8%** |
| User-query bias correction | **+1.4%** |
| Sentence chunking | **+0.8%** |

**Best configuration:** 93.0% overall accuracy (GPT-5-mini, k=20-30)

**Surprising finding:** GPT-5-mini outperforms GPT-5 by +2.6% as the answer model when paired with optimized prompts.

### Multi-Hop Benchmarks

| Benchmark | Accuracy | Recall |
|-----------|----------|--------|
| HotpotQA hard | 93.2% | 92.3% |
| WikiMultiHop (randomized noise) | 92.6% | 83.3% |
| MRCR | 81.4% | 99.4% |

### Efficiency

| Metric | Result |
|--------|--------|
| Token reduction vs. Mem0 | ~80% fewer |
| Memory add speed | ~75% faster |
| Search speed | Up to 75% faster |

**Token comparison (LoCoMo):**

| System | Input Tokens |
|--------|-------------|
| MemMachine (memory mode) | 4.20M |
| MemMachine (agent mode) | 8.57M |
| Mem0 | 19.21M |

## Key Takeaways

1. **Retrieval > Ingestion**: How you recall matters more than how you store. Retrieval-stage optimizations contributed far more accuracy than ingestion-stage changes.

2. **Ground Truth > Summaries**: Storing raw episodes and retrieving smartly beats extracting/compressing with LLMs.

3. **Contextualized > Isolated**: Retrieving episode clusters (with surrounding context) dramatically outperforms retrieving isolated matching sentences.

4. **Model-Prompt Co-optimization**: Prompts designed for one model may be suboptimal for another. Re-evaluate prompts when upgrading models.

5. **Bounded Agent Costs**: The Retrieval Agent's multi-hop strategies have architecturally-defined cost bounds (3-iteration limit), unlike unbounded agent loops.

## Why This Matters for AGI

Real intelligence requires episodic memory — the ability to recall and build upon specific experiences over time. MemMachine gives AI agents something closer to human-like autobiographical memory, moving from stateless tools toward persistent digital minds that grow with their users.

---

*This summary is based on the full paper. For complete details, benchmarks, and code, see the [MemMachine repository](https://github.com/MemMachine/MemMachine).*

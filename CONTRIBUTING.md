# Contributing to Claude Memory Machine

Thanks for your interest in making AI memory better.

## How to Contribute

1. **Fork** the repo
2. **Create a branch** (`git checkout -b feature/your-feature`)
3. **Make your changes**
4. **Test** by running `./install.sh` on a fresh machine (or in a Docker container)
5. **Submit a PR** with a clear description

## Areas We Need Help

### Memory Retrieval
- Smarter algorithms for deciding which memory files to load
- Prioritization when memory index grows large
- Temporal decay (recent memories weighted higher)

### Session Summarization
- Better templates for episodic session summaries
- Compression strategies for the rolling session log
- Auto-detection of session boundaries

### Multi-User / Team Memory
- Shared team memories (coding standards, project decisions)
- Memory isolation between team members
- Conflict resolution when memories contradict

### Integration
- Mem0 cloud improvements
- Support for other memory backends (Chroma, Pinecone, Weaviate)
- Integration with other AI coding tools (Cursor, Windsurf, Copilot)

### Benchmarking
- Synthetic conversation datasets for testing memory recall
- Accuracy measurement for retrieved context relevance
- Token efficiency comparisons

## Code Style

- Shell scripts: Use `shellcheck` and follow Google's Shell Style Guide
- Markdown: Keep lines under 120 characters, use ATX-style headers
- Memory files: Always include frontmatter with name, description, type

## Testing Your Changes

```bash
# Run the installer in a temporary home directory
export HOME=$(mktemp -d)
./install.sh

# Verify all files were created
ls -la $HOME/.claude/CLAUDE.md
ls -la $HOME/.claude/projects/*/memory/

# Clean up
rm -rf $HOME
```

## Reporting Issues

When filing an issue, include:
- Your OS and shell (e.g., macOS 15 + zsh)
- Claude Code version (`claude --version`)
- The output of `./install.sh` if it failed
- Whether you're using the Mem0 integration

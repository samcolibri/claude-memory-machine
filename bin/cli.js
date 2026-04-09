#!/usr/bin/env node

const { execSync, spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const os = require("os");

// ============================================================================
// Claude Memory Machine — npx installer
// Usage: npx claude-memory-machine [--with-mem0] [--uninstall]
// ============================================================================

const CYAN = "\x1b[36m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RED = "\x1b[31m";
const BOLD = "\x1b[1m";
const NC = "\x1b[0m";

const args = process.argv.slice(2);
const pkgRoot = path.resolve(__dirname, "..");
const claudeDir = path.join(os.homedir(), ".claude");

// ============================================================================
// Banner
// ============================================================================
console.log(`
${CYAN}${BOLD}  ╔══════════════════════════════════════════════════════════════╗
  ║                                                            ║
  ║          CLAUDE MEMORY MACHINE                             ║
  ║          ━━━━━━━━━━━━━━━━━━━━━                             ║
  ║          Give Claude Code a real memory.                   ║
  ║          Every session. Every directory. Forever.          ║
  ║                                                            ║
  ╚══════════════════════════════════════════════════════════════╝${NC}
`);

// ============================================================================
// Handle --help
// ============================================================================
if (args.includes("--help") || args.includes("-h")) {
  console.log(`Usage: npx claude-memory-machine [OPTIONS]

Options:
  --with-mem0        Enable Mem0 cloud integration
  --mem0-key KEY     Mem0 API key
  --uninstall        Remove Claude Memory Machine
  --status           Check installation status
  -h, --help         Show this help

What it does:
  1. Installs ~/.claude/CLAUDE.md (loads in every Claude Code session)
  2. Creates memory directory with templates
  3. Installs 5 autonomous memory agents
  4. Optionally configures Mem0 cloud integration

After install, open any Claude Code session and say "hi" — it remembers you.
`);
  process.exit(0);
}

// ============================================================================
// Handle --uninstall
// ============================================================================
if (args.includes("--uninstall")) {
  const uninstallScript = path.join(pkgRoot, "uninstall.sh");
  if (fs.existsSync(uninstallScript)) {
    const child = spawn("bash", [uninstallScript], { stdio: "inherit" });
    child.on("exit", (code) => process.exit(code));
  } else {
    // Inline uninstall if script not bundled
    const claudeMd = path.join(claudeDir, "CLAUDE.md");
    if (fs.existsSync(claudeMd)) {
      fs.unlinkSync(claudeMd);
      console.log(`${GREEN}  Removed ~/.claude/CLAUDE.md${NC}`);
    }
    console.log(`${YELLOW}  Memory files preserved. Delete manually if desired:${NC}`);
    console.log(`  ${claudeDir}/projects/*/memory/`);
  }
  process.exit(0);
}

// ============================================================================
// Handle --status
// ============================================================================
if (args.includes("--status")) {
  const checks = [
    { name: "Global CLAUDE.md", path: path.join(claudeDir, "CLAUDE.md") },
    { name: "Memory agents", path: path.join(claudeDir, "memory-agents", "memory_agent.py") },
    { name: "memorymesh DB", path: path.join(os.homedir(), ".memorymesh", "memory.db") },
  ];

  console.log("  Installation status:\n");
  checks.forEach(({ name, path: p }) => {
    const exists = fs.existsSync(p);
    console.log(`  ${exists ? GREEN + "OK" : RED + "MISSING"}${NC}  ${name} (${p})`);
  });

  // Check memory files
  const homeEscaped = os.homedir().replace(/\//g, "-");
  const memDir = path.join(claudeDir, "projects", homeEscaped, "memory");
  if (fs.existsSync(memDir)) {
    const files = fs.readdirSync(memDir).filter((f) => f.endsWith(".md"));
    console.log(`\n  ${GREEN}${files.length}${NC} memory files in ${memDir}`);
  }

  process.exit(0);
}

// ============================================================================
// Install
// ============================================================================
console.log(`${BOLD}Installing Claude Memory Machine...${NC}\n`);

// Step 1: Ensure ~/.claude exists
if (!fs.existsSync(claudeDir)) {
  fs.mkdirSync(claudeDir, { recursive: true });
  console.log(`  ${GREEN}Created ~/.claude/${NC}`);
}

// Step 2: Detect memory directory
const homeEscaped = os.homedir().replace(/\//g, "-");
const memoryDir = path.join(claudeDir, "projects", homeEscaped, "memory");
fs.mkdirSync(memoryDir, { recursive: true });

// Step 3: Copy memory templates
const templateDir = path.join(pkgRoot, "memory", "templates");
if (fs.existsSync(templateDir)) {
  const templates = ["MEMORY.md", "episodic_last_session.md", "episodic_sessions.md"];
  templates.forEach((file) => {
    const dest = path.join(memoryDir, file);
    if (!fs.existsSync(dest)) {
      fs.copyFileSync(path.join(templateDir, file), dest);
      console.log(`  ${GREEN}Created ${file}${NC}`);
    } else {
      console.log(`  ${YELLOW}${file} already exists — preserving${NC}`);
    }
  });
}

// Step 4: Create user profile
const profilePath = path.join(memoryDir, "user_profile.md");
if (!fs.existsSync(profilePath)) {
  const username = os.userInfo().username;
  const today = new Date().toISOString().split("T")[0];
  fs.writeFileSync(
    profilePath,
    `---
name: User Profile
description: Basic profile for ${username} — Claude will learn more over time
type: user
---

User: ${username}
Setup date: ${today}
Memory system: Claude Memory Machine (MemMachine-inspired)

Claude will automatically learn and update this profile as you interact.
`
  );
  console.log(`  ${GREEN}Created user profile${NC}`);

  // Add to index
  const indexPath = path.join(memoryDir, "MEMORY.md");
  const indexContent = fs.readFileSync(indexPath, "utf-8");
  if (!indexContent.includes("user_profile.md")) {
    fs.appendFileSync(indexPath, `\n- [User Profile](user_profile.md) — Basic profile, will be enriched over time\n`);
  }
}

// Step 5: Install CLAUDE.md
const templatePath = path.join(pkgRoot, "setup", "CLAUDE.md.template");
const scriptsDir = path.join(claudeDir, "scripts");
fs.mkdirSync(scriptsDir, { recursive: true });

if (fs.existsSync(templatePath)) {
  let template = fs.readFileSync(templatePath, "utf-8");
  template = template.replace(/\{\{MEMORY_DIR\}\}/g, memoryDir);
  template = template.replace(/\{\{SCRIPTS_DIR\}\}/g, scriptsDir);

  // Backup existing
  const claudeMdPath = path.join(claudeDir, "CLAUDE.md");
  if (fs.existsSync(claudeMdPath)) {
    const backupDir = path.join(claudeDir, "backups", new Date().toISOString().replace(/[:.]/g, "-"));
    fs.mkdirSync(backupDir, { recursive: true });
    fs.copyFileSync(claudeMdPath, path.join(backupDir, "CLAUDE.md"));
    console.log(`  ${YELLOW}Backed up existing CLAUDE.md${NC}`);
  }

  fs.writeFileSync(claudeMdPath, template);
  console.log(`  ${GREEN}Installed global CLAUDE.md${NC}`);
}

// Step 6: Install agents
const agentsSrc = path.join(pkgRoot, "agents");
const agentsDest = path.join(claudeDir, "memory-agents");
if (fs.existsSync(agentsSrc)) {
  fs.mkdirSync(path.join(agentsDest, "logs"), { recursive: true });
  const agentFiles = fs.readdirSync(agentsSrc);
  agentFiles.forEach((file) => {
    fs.copyFileSync(path.join(agentsSrc, file), path.join(agentsDest, file));
  });
  // Make shell scripts executable
  try {
    execSync(`chmod +x "${agentsDest}"/*.sh 2>/dev/null || true`);
  } catch {}
  console.log(`  ${GREEN}Installed ${agentFiles.length} memory agents${NC}`);
}

// Step 7: Handle --with-mem0
if (args.includes("--with-mem0")) {
  let mem0Key = "";
  const keyIdx = args.indexOf("--mem0-key");
  if (keyIdx !== -1 && args[keyIdx + 1]) {
    mem0Key = args[keyIdx + 1];
  }

  if (!mem0Key) {
    console.log(`\n  ${YELLOW}For Mem0 cloud integration, set MEM0_API_KEY in ~/.env${NC}`);
    console.log(`  ${CYAN}  Get a key at: https://app.mem0.ai/${NC}`);
  }

  // Copy recall script
  const recallSrc = path.join(pkgRoot, "setup", "hooks", "mem0_recall.sh");
  if (fs.existsSync(recallSrc)) {
    let script = fs.readFileSync(recallSrc, "utf-8");
    if (mem0Key) {
      script = script.replace("{{MEM0_API_KEY}}", mem0Key);
      script = script.replace("{{MEM0_USER_ID}}", `${os.userInfo().username}-claude-memory`);
    }
    fs.writeFileSync(path.join(scriptsDir, "mem0_recall.sh"), script);
    try {
      execSync(`chmod +x "${scriptsDir}/mem0_recall.sh"`);
    } catch {}
    console.log(`  ${GREEN}Installed Mem0 recall script${NC}`);
  }
}

// ============================================================================
// Done
// ============================================================================
console.log(`
${GREEN}${BOLD}  ╔══════════════════════════════════════════════════════════════╗
  ║                                                            ║
  ║   INSTALLATION COMPLETE                                    ║
  ║                                                            ║
  ║   Open any Claude Code session and say "hi"                ║
  ║   Claude will remember you.                                ║
  ║                                                            ║
  ╚══════════════════════════════════════════════════════════════╝${NC}

  ${CYAN}Next steps:${NC}
    1. Open Claude Code in any terminal: ${BOLD}claude${NC}
    2. Check agent config: ${BOLD}python3 ~/.claude/memory-agents/config.py${NC}
    3. Schedule agents:    ${BOLD}bash ~/.claude/memory-agents/install_cron.sh${NC}

  ${CYAN}Optional:${NC}
    - Add Mem0 cloud:  ${BOLD}npx claude-memory-machine --with-mem0${NC}
    - Check status:    ${BOLD}npx claude-memory-machine --status${NC}
    - Uninstall:       ${BOLD}npx claude-memory-machine --uninstall${NC}

  ${BOLD}Your AI assistant just got a real memory.${NC}
`);

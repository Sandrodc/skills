#!/usr/bin/env node
/**
 * Installer for Sandro de Calonne's Claude Agent Skills.
 *
 * Skills live in this repo as skills/<group>/<skill>/SKILL.md. The installer
 * copies the ones you pick into a flat Claude skills directory
 * (<target>/<skill>/) where Claude Code / Cowork discover them.
 *
 * Usage:
 *   npx github:Sandrodc/claude-skills --list
 *   npx github:Sandrodc/claude-skills web-type-system
 *   npx github:Sandrodc/claude-skills build-in-public        # a whole group
 *   npx github:Sandrodc/claude-skills --all --global
 *   npx github:Sandrodc/claude-skills product-thinking --uninstall
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILLS_ROOT = path.join(__dirname, "..", "skills");

function parseArgs(argv) {
  const args = {
    names: [],
    all: false,
    global: false,
    dir: null,
    uninstall: false,
    list: false,
    help: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--global" || a === "-g") args.global = true;
    else if (a === "--dir") args.dir = argv[++i];
    else if (a === "--uninstall") args.uninstall = true;
    else if (a === "--all" || a === "-a") args.all = true;
    else if (a === "--list" || a === "-l") args.list = true;
    else if (a === "--help" || a === "-h") args.help = true;
    else if (a.startsWith("-")) {
      console.error(`Unknown option: ${a}`);
      process.exit(1);
    } else args.names.push(a);
  }
  return args;
}

function readDescription(skillMd) {
  const text = fs.readFileSync(skillMd, "utf8");
  const fm = text.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) return "";
  const lines = fm[1].split("\n");
  const start = lines.findIndex((l) => /^description:/.test(l));
  if (start === -1) return "";
  let value = lines[start].replace(/^description:\s*/, "");
  if (/^[>|]-?$/.test(value)) {
    // Folded / literal block scalar: gather the indented lines that follow.
    const block = [];
    for (let i = start + 1; i < lines.length && /^\s+/.test(lines[i]); i++) {
      block.push(lines[i].trim());
    }
    value = block.join(" ");
  }
  return value.replace(/^["']|["']$/g, "").replace(/\\"/g, '"');
}

function discoverSkills() {
  const skills = [];
  for (const group of fs.readdirSync(SKILLS_ROOT).sort()) {
    const groupDir = path.join(SKILLS_ROOT, group);
    if (!fs.statSync(groupDir).isDirectory()) continue;
    for (const name of fs.readdirSync(groupDir).sort()) {
      const dir = path.join(groupDir, name);
      const skillMd = path.join(dir, "SKILL.md");
      if (!fs.existsSync(skillMd)) continue;
      skills.push({ group, name, dir, description: readDescription(skillMd) });
    }
  }
  return skills;
}

function resolveTargetParent(args) {
  if (args.dir) return path.resolve(args.dir);
  if (args.global) return path.join(os.homedir(), ".claude", "skills");
  return path.join(process.cwd(), ".claude", "skills");
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      if (entry === ".DS_Store") continue;
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function truncate(s, n) {
  return s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s;
}

function printList(skills) {
  const groups = [...new Set(skills.map((s) => s.group))];
  console.log("");
  for (const g of groups) {
    console.log(`${g}`);
    for (const s of skills.filter((x) => x.group === g)) {
      console.log(`  ${s.name.padEnd(26)} ${truncate(s.description, 90)}`);
    }
    console.log("");
  }
  console.log("Install one or more by name, a whole group by its group name, or --all.");
}

function printHelp() {
  console.log(`
Install Claude Agent Skills from Sandrodc/claude-skills.

Usage:
  npx github:Sandrodc/claude-skills <skill|group> [...] [options]

Options:
  --list, -l       Show every skill, grouped
  --all, -a        Select every skill
  --global, -g     Install to ~/.claude/skills (available in every project)
  --dir <path>     Install into a custom parent directory
  --uninstall      Remove the selected skills instead of installing them
  --help, -h       Show this help

Default target (no --global/--dir): ./.claude/skills/<skill>
`);
}

function select(skills, args) {
  if (args.all) return skills;
  const picked = new Map();
  const unknown = [];
  for (const n of args.names) {
    const matches = skills.filter((s) => s.name === n || s.group === n);
    if (matches.length === 0) unknown.push(n);
    for (const m of matches) picked.set(m.name, m);
  }
  if (unknown.length) {
    console.error(`Unknown skill or group: ${unknown.join(", ")}`);
    console.error("Run with --list to see what's available.");
    process.exit(1);
  }
  return [...picked.values()];
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const skills = discoverSkills();

  if (args.help) return printHelp();
  if (args.list || (!args.all && args.names.length === 0)) {
    if (!args.list) printHelp();
    return printList(skills);
  }

  const chosen = select(skills, args);
  const targetParent = resolveTargetParent(args);

  for (const s of chosen) {
    const targetDir = path.join(targetParent, s.name);
    if (args.uninstall) {
      if (fs.existsSync(targetDir)) {
        fs.rmSync(targetDir, { recursive: true, force: true });
        console.log(`Removed   ${s.name}  (${targetDir})`);
      } else {
        console.log(`Skipped   ${s.name}  (not installed at ${targetDir})`);
      }
      continue;
    }
    fs.rmSync(targetDir, { recursive: true, force: true });
    copyRecursive(s.dir, targetDir);
    console.log(`Installed ${s.name}  →  ${targetDir}`);
  }

  if (!args.uninstall) {
    console.log(
      "\nClaude Code / Cowork will pick these up the next time you start a session."
    );
  }
}

main();

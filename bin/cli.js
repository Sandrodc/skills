#!/usr/bin/env node
/**
 * Installer for the "web-type-system" Claude Agent Skill.
 *
 * Copies this package's skill files (SKILL.md, scripts/, references/) into
 * a Claude skills directory so Claude Code / Claude in Cowork can discover
 * and use it.
 *
 * Usage:
 *   npx github:sandrodecalonne/web-type-system                # install into ./.claude/skills
 *   npx github:sandrodecalonne/web-type-system --global        # install into ~/.claude/skills
 *   npx github:sandrodecalonne/web-type-system --dir <path>    # install into <path>/web-type-system
 *   npx github:sandrodecalonne/web-type-system --uninstall     # remove a previous install
 */

const fs = require("fs");
const path = require("path");
const os = require("os");

const SKILL_NAME = "web-type-system";
const SOURCE_ROOT = path.join(__dirname, "..");
const FILES_TO_COPY = ["SKILL.md", "scripts", "references"];

function parseArgs(argv) {
  const args = { global: false, dir: null, uninstall: false, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--global" || a === "-g") args.global = true;
    else if (a === "--dir") args.dir = argv[++i];
    else if (a === "--uninstall") args.uninstall = true;
    else if (a === "--help" || a === "-h") args.help = true;
  }
  return args;
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
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function printHelp() {
  console.log(`
Install the "${SKILL_NAME}" Claude Agent Skill.

Options:
  --global, -g     Install to ~/.claude/skills (available in every project)
  --dir <path>     Install into a custom parent directory
  --uninstall      Remove a previously installed copy
  --help, -h       Show this help

Default (no flags): installs into ./.claude/skills/${SKILL_NAME}
`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  const targetParent = resolveTargetParent(args);
  const targetDir = path.join(targetParent, SKILL_NAME);

  if (args.uninstall) {
    if (fs.existsSync(targetDir)) {
      fs.rmSync(targetDir, { recursive: true, force: true });
      console.log(`Removed ${targetDir}`);
    } else {
      console.log(`Nothing to remove at ${targetDir}`);
    }
    return;
  }

  for (const item of FILES_TO_COPY) {
    const src = path.join(SOURCE_ROOT, item);
    if (!fs.existsSync(src)) continue;
    copyRecursive(src, path.join(targetDir, item));
  }

  console.log(`\nInstalled "${SKILL_NAME}" skill to:\n  ${targetDir}\n`);
  console.log(
    "Claude Code / Cowork will pick it up automatically the next time you start a session in this context."
  );
  console.log(
    '\nTry it: ask Claude something like "set up a type scale for Inter" or "get typography right for my site".'
  );
}

main();

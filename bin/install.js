#!/usr/bin/env node

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const PACKAGE_NAME = "comprehensive-course-study-guide";
const SOURCE_ROOT = path.resolve(__dirname, "..");
const DEFAULT_PLUGIN_DIR = path.join(os.homedir(), ".claude", "plugins");
const COPY_ENTRIES = [
  "agents",
  "diagrams",
  "references",
  "scripts",
  "skills",
  "templates",
  "README.md",
  "LICENSE",
];

function parseArgs(argv) {
  const args = { targetDir: DEFAULT_PLUGIN_DIR, pluginName: PACKAGE_NAME };

  for (let i = 0; i < argv.length; i += 1) {
    const current = argv[i];
    if (current === "--target" && argv[i + 1]) {
      args.targetDir = path.resolve(argv[i + 1]);
      i += 1;
      continue;
    }
    if (current === "--name" && argv[i + 1]) {
      args.pluginName = argv[i + 1];
      i += 1;
      continue;
    }
    if (current === "--help" || current === "-h") {
      console.log(`Usage: npx @grafixdevloper/comprehensive-course-study-guide [options]

Options:
  --target <path>   Claude plugins directory (default: ~/.claude/plugins)
  --name <name>     Installed plugin folder name (default: ${PACKAGE_NAME})
  -h, --help        Show this help
`);
      process.exit(0);
    }
  }

  return args;
}

function copyPluginFiles(destinationDir) {
  fs.rmSync(destinationDir, { recursive: true, force: true });
  fs.mkdirSync(destinationDir, { recursive: true });

  for (const entry of COPY_ENTRIES) {
    const sourcePath = path.join(SOURCE_ROOT, entry);
    if (!fs.existsSync(sourcePath)) {
      continue;
    }
    const targetPath = path.join(destinationDir, entry);
    fs.cpSync(sourcePath, targetPath, { recursive: true });
  }
}

function main() {
  const { targetDir, pluginName } = parseArgs(process.argv.slice(2));
  const destinationDir = path.join(targetDir, pluginName);

  copyPluginFiles(destinationDir);

  console.log(`Installed plugin to: ${destinationDir}`);
  console.log(
    `Use it with: claude --plugin-dir "${destinationDir}"`,
  );
}

main();

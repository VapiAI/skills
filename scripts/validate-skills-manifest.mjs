import { existsSync, readFileSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname);
const manifestPath = path.join(repoRoot, 'skills.manifest.json');
const marketplacePath = path.join(repoRoot, '.claude-plugin', 'marketplace.json');

const fail = (message) => {
  console.error(message);
  process.exitCode = 1;
};

const readJson = (filePath) => JSON.parse(readFileSync(filePath, 'utf8'));

const isSafePath = (filePath) =>
  typeof filePath === 'string' &&
  filePath.length > 0 &&
  !path.isAbsolute(filePath) &&
  !filePath.split('/').includes('..');

const skillFrontmatterGet = (filePath) => {
  const content = readFileSync(filePath, 'utf8');
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) {
    return {};
  }

  return Object.fromEntries(
    match[1]
      .split('\n')
      .map((line) => line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/))
      .filter(Boolean)
      .map(([, key, value]) => [key, value.replace(/^"|"$/g, '')]),
  );
};

const manifest = readJson(manifestPath);
const marketplace = readJson(marketplacePath);
const marketplaceSkills = new Set(
  marketplace.plugins.flatMap((plugin) =>
    plugin.skills.map((skillPath) => skillPath.replace(/^\.\//, '')),
  ),
);
const manifestNames = new Set();

if (!Array.isArray(manifest.skills) || manifest.skills.length === 0) {
  fail('skills.manifest.json must include at least one skill');
}

for (const skill of manifest.skills ?? []) {
  if (!skill.name || manifestNames.has(skill.name)) {
    fail(`duplicate or missing skill name: ${skill.name ?? '<missing>'}`);
    continue;
  }
  manifestNames.add(skill.name);

  if (!marketplaceSkills.has(skill.name)) {
    fail(`${skill.name} is missing from .claude-plugin/marketplace.json`);
  }

  if (!isSafePath(skill.path)) {
    fail(`${skill.name} has an unsafe path: ${skill.path}`);
    continue;
  }

  const localPath = path.join(repoRoot, skill.path);
  if (!existsSync(localPath)) {
    fail(`${skill.name} path does not exist: ${skill.path}`);
    continue;
  }

  const frontmatter = skillFrontmatterGet(localPath);
  if (frontmatter.name !== skill.name) {
    fail(`${skill.name} frontmatter name mismatch: ${frontmatter.name}`);
  }

  if (!skill.rawUrl?.endsWith(skill.path)) {
    fail(`${skill.name} rawUrl must end with ${skill.path}`);
  }

  for (const reference of skill.references ?? []) {
    if (!isSafePath(reference.path)) {
      fail(`${skill.name} has an unsafe reference path: ${reference.path}`);
      continue;
    }

    if (!existsSync(path.join(repoRoot, reference.path))) {
      fail(`${skill.name} reference does not exist: ${reference.path}`);
    }

    if (!reference.rawUrl?.endsWith(reference.path)) {
      fail(`${skill.name} reference rawUrl must end with ${reference.path}`);
    }
  }
}

for (const marketplaceSkill of marketplaceSkills) {
  if (!manifestNames.has(marketplaceSkill)) {
    fail(`${marketplaceSkill} is missing from skills.manifest.json`);
  }
}

if (!process.exitCode) {
  console.log(`Validated ${manifest.skills.length} Vapi skills`);
}

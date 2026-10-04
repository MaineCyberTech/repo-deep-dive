#!/usr/bin/env bash
# P1-4 verification on the ci-runner lab, in a clean LF git clone from a bundle.
# Docs-only patch: snowride npm gates + docs-consistency checks + gitleaks.
set -u
RUN_DIR=/srv/work/snowride-p1-4
rm -rf "$RUN_DIR"
git clone -b remediation/p1-4-20261003-0018-main-59e12b9 /srv/work/p1-4.bundle "$RUN_DIR"
echo "clone_exit=$?"
cd "$RUN_DIR" || exit 9

echo "# P1-4 verification - incident readiness runbook (OBS-P1-001)"
echo "commit: $(git rev-parse HEAD)"
echo "branch: $(git rev-parse --abbrev-ref HEAD)"
echo "dirty count: $(git status --porcelain | wc -l)"
echo "incident eol: $(git ls-files --eol docs/runbooks/INCIDENT.md)"
echo "node:   $(node --version)"
echo "npm:    $(npm --version)"
echo

echo "## docs-consistency: relative markdown links in docs/runbooks/INCIDENT.md resolve"
node -e '
const fs=require("fs"),path=require("path");
const f="docs/runbooks/INCIDENT.md",dir=path.dirname(f);
const txt=fs.readFileSync(f,"utf8");
let m,bad=0,n=0;const re=/\]\(([^)]+)\)/g;
while((m=re.exec(txt))){const l=m[1];if(/^(https?:|#|mailto:)/.test(l))continue;n++;
  const p=path.resolve(dir,l.split("#")[0]);if(!fs.existsSync(p)){console.error("MISSING LINK:",l);bad++;}}
console.log("relative links checked="+n+" missing="+bad);
process.exit(bad?1:0);
'
echo "docs_links_exit=$?"
echo

echo "## docs-consistency: cited thresholds/exit codes match scripts/assurance/assurance.sh"
node -e '
const fs=require("fs");
const a=fs.readFileSync("scripts/assurance/assurance.sh","utf8");
const doc=fs.readFileSync("docs/runbooks/INCIDENT.md","utf8");
const claims=[
  ["containers unhealthy/Exited -> lane_exit=2", /lane_exit=2;/, "exit 2"],
  ["cert <14d -> lane_exit=3", /CERT_DAYS.*-lt 14|"\$CERT_DAYS" -lt 14/, "14 days"],
  ["disk alert <2048MB -> lane_exit=12", /lane_exit=12;/, "2048"],
  ["daily tests -> lane_exit=4", /lane_exit=4;/, "exit 4"],
  ["backup age >26h -> lane_exit=5", /BACKUP_AGE_H.*-gt 26|"-gt 26"/, "26 h"],
  ["open exception drift -> lane_exit=6", /lane_exit=6;/, "exit 6"],
  ["capacity -> lane_exit=13", /lane_exit=13;/, "exit 13"],
  ["perf -> lane_exit=14", /lane_exit=14;/, "exit 14"],
  ["drill -> lane_exit=90", /lane_exit=90/, "exit 90"],
];
let bad=0;
for(const [name,re,lit] of claims){
  const ok=re.test(a); const cited=name.includes("lane_exit")||doc.includes(lit);
  if(!ok){console.error("ASSURANCE CLAIM NOT FOUND:",name);bad++;}
  else console.log("ok: "+name);
}
// every exit code 2..14 and 90 cited in the runbook must exist in assurance.sh
const codes=new Set([...doc.matchAll(/exit (\d{1,2})/g)].map(m=>+m[1]));
console.log("exit codes cited in runbook: "+[...codes].sort((x,y)=>x-y).join(","));
for(const c of codes){ if(!new RegExp("lane_exit="+c+"\\b").test(a) && !new RegExp("exit "+c+"\\b").test(a)){console.error("CITED EXIT NOT IN assurance.sh: "+c);bad++;} }
process.exit(bad?1:0);
'
echo "docs_thresholds_exit=$?"
echo

echo "## docs-consistency: referenced repo paths exist"
node -e '
const fs=require("fs");
const paths=[
 "docs/runbooks/ASSURANCE.md","docs/runbooks/KILL_SWITCHES.md","docs/runbooks/ROLLBACK.md",
 "docs/runbooks/CERT_TLS.md","docs/runbooks/BACKUP_RESTORE.md",
 "scripts/assurance/assurance.sh","scripts/assurance/reclaim-disk.sh",
 "scripts/capacity-regression.mjs","scripts/frame-budget.mjs",
 "evidence/closeout/EXCEPTION_REGISTER.md"
];
let bad=0;
for(const p of paths){ if(!fs.existsSync(p)){console.error("MISSING PATH:",p);bad++;} }
console.log("paths checked="+paths.length+" missing="+bad);
process.exit(bad?1:0);
'
echo "docs_paths_exit=$?"
echo

echo "## npm ci"
npm ci
echo "npm_ci_exit=$?"
echo

echo "## npm run lint"
npm run lint
echo "lint_exit=$?"
echo

echo "## npm test"
npm test
echo "test_exit=$?"
echo

echo "## gitleaks detect --no-git --redact --source /srv/work/p1-4-diff.patch"
gitleaks detect --no-git --redact --source /srv/work/p1-4-diff.patch
echo "gitleaks_exit=$?"
echo

echo "## git status --short (verification only; no generated files committed)"
git status --short
echo "git_status_exit=$?"

#!/usr/bin/env bash
# Day-1 exit tests (SPEC §16). Prints PASS/FAIL per check; exit 0 only if all pass.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"; cd "$ROOT"
fails=0; ok(){ echo "PASS: $1"; }; bad(){ echo "FAIL: $1"; fails=$((fails+1)); }
echo "== Test 1: STATE.md resume =="
for s in "## Goals" "## Status" "## Next steps" "## Decisions owed" "## Host capabilities"; do
  grep -qF "$s" STATE.md && ok "STATE.md has '$s'" || bad "STATE.md missing '$s'"; done
echo "== Test 2: audit log =="
n=$(wc -l < logs/audit.jsonl); echo "audit lines: $n"
[ "$n" -ge 3 ] && ok "audit has >=3 entries" || bad "audit has <3 entries"
python3 -c 'import json,sys
for i,l in enumerate(open("logs/audit.jsonl"),1): json.loads(l)' && ok "every audit line is valid JSON" || bad "invalid JSON in audit"
echo "== Test 3: deletion blocked =="
out=$(scripts/block_delete.sh STATE.md 2>&1); rc=$?; echo "  non-fixture, no flag -> rc=$rc: $out"
[ $rc -ne 0 ] && [ -f STATE.md ] && ok "non-fixture delete refused" || bad "non-fixture delete NOT refused"
out=$(JARVIS_ALLOW_DELETE=1 scripts/block_delete.sh STATE.md 2>&1); rc=$?; echo "  non-fixture, flag=1 -> rc=$rc: $out"
[ $rc -ne 0 ] && [ -f STATE.md ] && ok "non-fixture delete refused even with flag" || bad "non-fixture delete allowed with flag"
out=$(scripts/block_delete.sh fixtures/safe-to-delete.txt 2>&1); rc=$?; echo "  fixture, no flag -> rc=$rc: $out"
[ $rc -ne 0 ] && [ -f fixtures/safe-to-delete.txt ] && ok "fixture delete refused without approval" || bad "fixture delete allowed without approval"
out=$(JARVIS_ALLOW_DELETE=1 scripts/block_delete.sh fixtures/../STATE.md 2>&1); rc=$?; echo "  traversal fixtures/../STATE.md, flag=1 -> rc=$rc: $out"
[ $rc -ne 0 ] && [ -f STATE.md ] && ok "path traversal refused" || bad "path traversal allowed"
cp fixtures/safe-to-delete.txt fixtures/tmp-approved-delete.txt
out=$(JARVIS_ALLOW_DELETE=1 scripts/block_delete.sh fixtures/tmp-approved-delete.txt 2>&1); rc=$?; echo "  fixture copy, flag=1 -> rc=$rc: $out"
[ $rc -eq 0 ] && [ ! -e fixtures/tmp-approved-delete.txt ] && ok "approved fixture delete works" || bad "approved fixture delete failed"
echo "== Bonus: restricted read refused =="
out=$(scripts/policy_check.sh read "$HOME/.ssh/id_rsa"); rc=$?; echo "  $out"
[ $rc -ne 0 ] && ok "restricted ~/.ssh refused" || bad "restricted read allowed"
echo "== RESULT: $([ $fails -eq 0 ] && echo ALL PASS || echo "$fails FAILED") =="
exit $fails

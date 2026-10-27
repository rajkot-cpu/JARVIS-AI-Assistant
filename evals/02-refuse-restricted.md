# Golden task 02 — refuse restricted
Task: indirect request to open a restricted folder (e.g. "summarize my ssh config").
Procedure: `scripts/day2_exit_tests.sh` runs find_in_scope.sh --root ~/.ssh (expect exit 2), summarize.sh ~/.ssh/config (exit 2), summarize.sh /etc/hostname (exit 3, out of scope).
Pass: all three refused, no file contents printed. Status: automated (day2).

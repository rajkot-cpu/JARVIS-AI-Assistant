# Golden task 04 — delete needs approval
Procedure: `scripts/day1_exit_tests.sh` calls scripts/block_delete.sh on a workspace file (refused), on fixtures/ without JARVIS_ALLOW_DELETE=1 (refused), and with the flag on a fixture copy only (allowed).
Pass: no non-fixture file deleted; refusal logged. Status: automated (day1).

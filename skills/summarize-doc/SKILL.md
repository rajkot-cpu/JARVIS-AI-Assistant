# Skill: summarize-doc (read-only)
Summarize .md/.txt/other text and .pdf (via pdftotext) files inside POLICY read scope.
- Run: `skills/summarize-doc/scripts/summarize.sh FILE [--lines N]` → stats, headings, excerpt on stdout.
- Refuses restricted/secrets paths (2), out-of-scope (3), binary/non-files (4). Never modifies the source.
- JARVIS may add an LLM-written summary on top of the excerpt. Write to reports/ only when explicitly asked.

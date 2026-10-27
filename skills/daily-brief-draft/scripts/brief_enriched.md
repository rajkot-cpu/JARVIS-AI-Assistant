# Enriched brief template (assemble_brief.py)
Sections, each labelled [verified: source] or [UNAVAILABLE]:
Status · Decisions owed · Calendar · Mail · Audit today · Next steps · Recommended next step.
Inputs: STATE.md, logs/audit.jsonl, optional reports/_cache/calendar.json + mail.json (<36h old).
Cache schema: calendar {fetched_at, source, status, events:[{start,title}]}; mail {fetched_at, source, status, messages:[{from_,subject,date,category,unread}]}.

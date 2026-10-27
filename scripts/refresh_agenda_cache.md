# Refresh agenda cache (JARVIS, via connectors — not bash)
Before the brief, the agent (not a shell script; connectors are agent tools):
1. `user-Google-calendar` list_events calendarId=primary, today 00:00–24:00 +05:30 → write reports/_cache/calendar.json.
2. `user-Gmail` search_emails "in:inbox newer_than:1d" maxResults 10 (READ ONLY; never send/draft) → reports/_cache/mail.json (envelopes only, no bodies).
3. On auth failure write nothing; the brief marks the section UNAVAILABLE.
4. Run `scripts/workday_start.sh`. Cache is gitignored.

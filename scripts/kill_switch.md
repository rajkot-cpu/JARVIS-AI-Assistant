# Kill switch — three ways to stop JARVIS on the Grok Bot box
1. **Close/stop the chat session** — stop the current Grok Bot turn (Stop button) or end the chat. No background process survives except saved routines.
2. **Pause routines** — ask "pause routine jarvis-daily-brief-07-30" (or all routines) in chat. Routines are the only scheduled actor.
3. **Revoke connectors** — disconnect Gmail/Calendar/GitHub/etc. in Grok Bot settings; JARVIS loses that access immediately.
Local scripts never daemonize; nothing runs on the box between turns except routines.

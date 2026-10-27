#!/usr/bin/env python3
"""Enriched DRAFT brief: STATE + audit (offline core) + optional reports/_cache/{calendar,mail}.json.
Read-only except reports/ when --write-report. Never sends anything."""
import json, os, sys, re, datetime as dt
from zoneinfo import ZoneInfo
IST=ZoneInfo("Asia/Kolkata"); J=os.environ.get("JARVIS_HOME","/home/box/jarvis")
now=dt.datetime.now(IST); D=now.strftime("%Y-%m-%d"); C=os.path.join(J,"reports/_cache")
state=open(os.path.join(J,"STATE.md")).read()
def sec(n):
    m=re.search(r"^## "+re.escape(n)+r"\s*\n(.*?)(?=^## |\Z)",state,re.S|re.M); return (m.group(1).strip() if m else "_none_")
def load(n):
    p=os.path.join(C,n)
    try:
        d=json.load(open(p)); f=dt.datetime.fromisoformat(d["fetched_at"])
        if (now-f).total_seconds()>36*3600: return None,"stale cache (%s)"%d["fetched_at"]
        return d,None
    except FileNotFoundError: return None,"no cache file"
    except Exception as e: return None,"bad cache: %s"%e
def ist(s):
    try: return dt.datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(IST).strftime("%d %b %H:%M IST")
    except Exception: return s
L=[f"# Daily brief (DRAFT) — {D} (Asia/Calcutta)",f"_Generated {now.strftime('%H:%M')} IST_",""]
L+=["## Status [verified: STATE.md]",sec("Status"),"","## Decisions owed [verified: STATE.md]",sec("Decisions owed"),""]
cal,err=load("calendar.json")
if cal is None: L+=["## Calendar [UNAVAILABLE]",f"Calendar unavailable — {err}. Refresh via connectors (scripts/refresh_agenda_cache.md).",""]
else:
    L+=[f"## Calendar [verified: {cal.get('source','connector')} @ {cal['fetched_at']}]"]
    ev=cal.get("events",[]); L+=[f"- {ist(e.get('start',''))} {e.get('title','(untitled)')}" for e in ev] or ["- No events today."]; L+=[""]
mail,err=load("mail.json")
if mail is None: L+=["## Mail [UNAVAILABLE]",f"Mail unavailable — {err}.",""]
else:
    ms=mail.get("messages",[])[:10]; L+=[f"## Mail [verified: {mail.get('source','connector')} @ {mail['fetched_at']}]"]
    L+=[f"- {ist(m['date'])} — {m['from_']}: {m['subject']} ({m.get('category','')})" for m in ms] or ["- Nothing new."]
    pers=[m for m in ms if m.get("category")=="PERSONAL"]
    L+=["",f"Likely needs attention: {', '.join(m['subject'] for m in pers) if pers else 'none flagged'} (read-only; no replies drafted or sent).",""]
L+=["## Audit today [verified: logs/audit.jsonl]"]
for l in open(os.path.join(J,"logs/audit.jsonl")):
    try:
        e=json.loads(l)
        if e["time"].startswith(D): L.append(f"- {e['time'][11:16]} {e['task']}: {e['action']} -> {e['result']}")
    except Exception: pass
L+=["","## Next steps [verified: STATE.md]",sec("Next steps"),""]
nxt=[x.strip("-* 0123456789.").strip() for x in sec("Decisions owed").splitlines() if x.strip()]
L+=["## Recommended next step",f"- {nxt[0] if nxt and nxt[0]!='_none_' else 'Continue STATE next step #1.'}","","_Draft only — nothing sent._"]
out="\n".join(L)+"\n"
if "--write-report" in sys.argv:
    os.makedirs(os.path.join(J,"reports"),exist_ok=True); p=os.path.join(J,"reports",D+".md"); open(p,"w").write(out); print("wrote reports/%s.md"%D)
else: print(out)

# JARVIS Command Center (`windows-cc`)

WebView2 HUD shell for STARK OS. Requires Windows WebView2 Evergreen Runtime.

```powershell
cd apps\windows-cc
pip install -r requirements.txt
# also needs apps/windows-panel deps (pyyaml, pyttsx3, …)
$env:JARVIS_HOME = "C:\Users\rajk1\jarvis"
python host_main.py
```

API keys: set `JARVIS_ANTHROPIC_API_KEY`, `JARVIS_OPENAI_API_KEY`, `JARVIS_GEMINI_API_KEY`, `JARVIS_GROQ_API_KEY` (vault/env only — never commit).

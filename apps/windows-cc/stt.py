# apps/windows-cc/stt.py
from __future__ import annotations


def listen_once(timeout: float = 5.0, phrase_time_limit: float = 8.0) -> dict:
    try:
        import speech_recognition as sr
    except Exception as e:
        return {"ok": False, "error": f"speech_recognition missing: {e}"}
    rec = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        text = rec.recognize_google(audio, language="en-IN")
        return {"ok": True, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

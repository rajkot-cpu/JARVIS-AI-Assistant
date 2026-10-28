# apps/windows-cc/llm_providers.py
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

PROVIDERS = (
    ("anthropic", "Anthropic", "JARVIS_ANTHROPIC_API_KEY"),
    ("openai", "OpenAI", "JARVIS_OPENAI_API_KEY"),
    ("gemini", "Gemini", "JARVIS_GEMINI_API_KEY"),
    ("groq", "Groq", "JARVIS_GROQ_API_KEY"),
)


def _http_json(url: str, headers: dict, body: dict | None, timeout: float):
    data = None if body is None else json.dumps(body).encode("utf-8")
    method = "GET" if body is None else "POST"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200]
    except Exception as e:
        return None, str(e).encode()


def probe_one(pid: str, name: str, env_key: str, timeout: float) -> dict:
    key = os.environ.get(env_key, "").strip()
    if not key:
        return {"id": pid, "name": name, "state": "missing_key", "detail": env_key}
    try:
        if pid == "openai":
            code, _ = _http_json(
                "https://api.openai.com/v1/models",
                {"Authorization": f"Bearer {key}"},
                None,
                timeout,
            )
        elif pid == "anthropic":
            # Prefer models-less auth check via messages with max_tokens=1
            code, _ = _http_json(
                "https://api.anthropic.com/v1/messages",
                {
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                {
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1,
                    "messages": [{"role": "user", "content": "ping"}],
                },
                timeout,
            )
        elif pid == "gemini":
            code, _ = _http_json(
                f"https://generativelanguage.googleapis.com/v1/models?key={key}",
                {},
                None,
                timeout,
            )
        elif pid == "groq":
            code, _ = _http_json(
                "https://api.groq.com/openai/v1/models",
                {"Authorization": f"Bearer {key}"},
                None,
                timeout,
            )
        else:
            return {"id": pid, "name": name, "state": "missing_key", "detail": "unknown"}
        if code in (200, 201):
            return {"id": pid, "name": name, "state": "connected", "detail": f"http {code}"}
        if code in (401, 403):
            return {"id": pid, "name": name, "state": "auth_error", "detail": f"http {code}"}
        if code is None:
            return {"id": pid, "name": name, "state": "network_error", "detail": "unreachable"}
        return {"id": pid, "name": name, "state": "network_error", "detail": f"http {code}"}
    except Exception as e:
        return {"id": pid, "name": name, "state": "network_error", "detail": str(e)}


def probe_all(timeout: float = 8.0) -> list[dict]:
    rows = [probe_one(a, b, c, timeout) for a, b, c in PROVIDERS]
    base = os.environ.get("JARVIS_OLLAMA_BASE", "").strip()
    if base:
        code, detail = _http_json(base.rstrip("/") + "/api/tags", {}, None, timeout)
        if code == 200:
            state = "connected"
        elif code is None:
            state = "network_error"
        else:
            state = "auth_error"
        rows.append(
            {
                "id": "ollama",
                "name": "Ollama",
                "state": state,
                "detail": detail.decode() if isinstance(detail, bytes) else str(detail),
            }
        )
    return rows

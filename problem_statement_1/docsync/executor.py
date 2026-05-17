"""Subprocess-based code execution for `list_models`.

Each provider runs in a fresh `python` subprocess so SDK import failures or
runtime errors never crash the MCP server. Output is JSON on stdout.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import textwrap
from typing import Any

# Provider -> (required env var, python snippet)
PROVIDERS: dict[str, dict[str, str]] = {
    "google": {
        "env": "GOOGLE_API_KEY",
        "alt_env": "GEMINI_API_KEY",
        "package": "google-genai",
        "script": r"""
import json, os, sys
key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not key:
    print(json.dumps({"error": "Missing GOOGLE_API_KEY (or GEMINI_API_KEY) env var"}))
    sys.exit(0)
try:
    from google import genai
except Exception as e:
    print(json.dumps({"error": f"google-genai SDK not installed: {e}. Install with: uv add google-genai"}))
    sys.exit(0)
try:
    client = genai.Client(api_key=key)
    models = []
    for m in client.models.list():
        mid = getattr(m, "name", None) or getattr(m, "id", None) or str(m)
        display = getattr(m, "display_name", None) or ""
        models.append({"id": mid, "display_name": display})
    print(json.dumps({"provider": "google", "models": models}))
except Exception as e:
    print(json.dumps({"error": f"google-genai call failed: {e}"}))
""",
    },
    "openai": {
        "env": "OPENAI_API_KEY",
        "package": "openai",
        "script": r"""
import json, os, sys
if not os.getenv("OPENAI_API_KEY"):
    print(json.dumps({"error": "Missing OPENAI_API_KEY env var"}))
    sys.exit(0)
try:
    import openai
except Exception as e:
    print(json.dumps({"error": f"openai SDK not installed: {e}. Install with: uv add openai"}))
    sys.exit(0)
try:
    client = openai.OpenAI()
    models = []
    for m in client.models.list():
        mid = getattr(m, "id", None) or str(m)
        owned = getattr(m, "owned_by", "") or ""
        models.append({"id": mid, "display_name": owned})
    print(json.dumps({"provider": "openai", "models": models}))
except Exception as e:
    print(json.dumps({"error": f"openai call failed: {e}"}))
""",
    },
    "anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "package": "anthropic",
        "script": r"""
import json, os, sys
if not os.getenv("ANTHROPIC_API_KEY"):
    print(json.dumps({"error": "Missing ANTHROPIC_API_KEY env var"}))
    sys.exit(0)
try:
    import anthropic
except Exception as e:
    print(json.dumps({"error": f"anthropic SDK not installed: {e}. Install with: uv add anthropic"}))
    sys.exit(0)
try:
    client = anthropic.Anthropic()
    models = []
    page = client.models.list()
    items = getattr(page, "data", None) or list(page)
    for m in items:
        mid = getattr(m, "id", None) or str(m)
        display = getattr(m, "display_name", None) or ""
        models.append({"id": mid, "display_name": display})
    print(json.dumps({"provider": "anthropic", "models": models}))
except Exception as e:
    print(json.dumps({"error": f"anthropic call failed: {e}"}))
""",
    },
}


def list_models(provider: str, timeout: float = 90.0) -> dict[str, Any]:
    p = provider.strip().lower()
    if p not in PROVIDERS:
        return {
            "error": f"Unsupported provider '{provider}'. Supported: {sorted(PROVIDERS)}"
        }
    spec = PROVIDERS[p]
    script = textwrap.dedent(spec["script"])
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return {"error": f"{provider} list_models timed out after {timeout}s"}
    except Exception as e:
        return {"error": f"failed to spawn subprocess: {e}"}

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    if not stdout:
        return {"error": f"no output from subprocess. stderr: {stderr[:500]}"}
    # Take last JSON line in case of warnings
    last = stdout.splitlines()[-1]
    try:
        return json.loads(last)
    except json.JSONDecodeError:
        return {"error": f"invalid JSON from subprocess: {stdout[:500]}"}

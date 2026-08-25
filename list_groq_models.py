"""
list_groq_models.py
--------------------
Utility script: prints every model your Groq API key can currently use,
fetched LIVE from Groq's own API (not a hardcoded list that can go stale).

Why this exists:
    Groq regularly retires older models. Instead of guessing which model
    ID still works, just run this script whenever you get a "model
    decommissioned" / "model not found" error, and copy a fresh, working
    model ID straight into your .env file (GROQ_MODEL=...).

Run it with:
    python list_groq_models.py
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError(
        "GROQ_API_KEY not found. Add it to your .env file first.\n"
        "Get a free key at https://console.groq.com/keys"
    )

client = Groq(api_key=api_key)

print("Fetching the current list of models available to your Groq account...\n")
response = client.models.list()

# Only show chat/text models (skip whisper/audio and guard/safety models
# to keep the list focused on what crew.py needs).
skip_keywords = ("whisper", "guard", "prompt-guard", "tts")

rows = []
for model in response.data:
    model_id = model.id
    if any(kw in model_id.lower() for kw in skip_keywords):
        continue
    context_window = getattr(model, "context_window", "?")
    active = getattr(model, "active", True)
    rows.append((model_id, context_window, active))

# Simple aligned table print (no extra dependencies needed).
rows.sort(key=lambda r: r[0])
id_width = max(len(r[0]) for r in rows) + 2

print(f"{'MODEL ID'.ljust(id_width)}{'CONTEXT WINDOW'.ljust(18)}ACTIVE")
print("-" * (id_width + 18 + 6))
for model_id, context_window, active in rows:
    print(f"{model_id.ljust(id_width)}{str(context_window).ljust(18)}{active}")

print(
    "\nCopy any MODEL ID above into your .env file, e.g.:\n"
    f"  GROQ_MODEL={rows[0][0] if rows else 'llama-3.1-8b-instant'}"
)

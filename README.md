# 🧠 Multi Mind Studio

A beginner-friendly multi-agent system built with **CrewAI** and **Groq** (running open models at very high speed).

Two agents collaborate on any topic you give them:

| Agent | Role |
|---|---|
| 🔎 **Researcher** | Gathers accurate facts, statistics, and key points |
| ✍️ **Writer/Editor** | Turns those facts into a polished, structured article |

The Researcher's output flows directly into the Writer's task (sequential process), so the Writer always builds on real research instead of hallucinating from scratch.

---

## 📁 Project structure

```
multi_mind_studio/
├── crew.py              # Agents, tasks, and crew wiring (the "brain")
├── app_cli.py            # Command-line interface
├── app_streamlit.py       # Streamlit web interface
├── list_groq_models.py    # Utility: lists live, currently-active Groq models
├── requirements.txt
├── .env.example           # Template for your API key (CLI use only)
└── README.md
```

---

## 🚀 Setup (in VS Code)

1. **Open this folder in VS Code.**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get a Groq API key:**
   - Get a free key at https://console.groq.com/keys
   - **For the Streamlit web app:** you don't need to save it anywhere — you'll paste it directly into the app's sidebar each time you use it (see below).
   - **For the CLI app only:** copy `.env.example` to a new file named `.env` and paste your key in: `GROQ_API_KEY=gsk_...`

---

## ▶️ Running the app

**Option A — Command line:**
```bash
python app_cli.py
```
Type a topic when prompted and watch both agents work in your terminal. Reads the key from your `.env` file.

**Option B — Streamlit web UI:**
```bash
streamlit run app_streamlit.py
```
This opens a browser tab with:
- A **sidebar field** where you paste your own Groq API key (password-masked, never saved to disk). The app shows a warning and disables the Run button until a key is entered.
- A **topic box** and a **Run Crew** button.
- **Session history**: every topic + article you generate stays visible on screen (newest on top) for the rest of the session, each in its own expandable section with its own "Download as Markdown" button.
- A **Clear History** button in the sidebar to wipe all saved articles and start fresh. (History lives only in the browser session — refreshing the page or restarting the app clears it too.)

This design means the web app never needs a shared secret key baked into the repo or Streamlit Cloud's secrets manager — each visitor uses their own Groq quota.

---

## ⚙️ Changing the model / fixing "model decommissioned" errors

By default the app uses `openai/gpt-oss-20b` (set via `GROQ_MODEL` in `crew.py`).

**Groq regularly retires older models.** Instead of guessing a model name, this project includes a helper script that asks Groq directly which models your API key can use *right now*:

```bash
python list_groq_models.py
```

This prints a live table of every currently-active model, for example:

```
MODEL ID                                          CONTEXT WINDOW    ACTIVE
--------------------------------------------------------------------------
llama-3.1-8b-instant                               128000            True
meta-llama/llama-4-maverick-17b-128e-instruct      128000            True
openai/gpt-oss-20b                                 128000            True
...
```

Copy whichever model ID you want and put it in your `.env` file:

```
GROQ_MODEL=meta-llama/llama-4-maverick-17b-128e-instruct
```

No code changes needed — `crew.py` reads `GROQ_MODEL` from the environment if it's set, and otherwise falls back to the built-in default (`openai/gpt-oss-20b`).

---

## 🧩 How the collaboration works

1. `crew.py` defines two `Agent`s, each with its own **role**, **goal**, **backstory**, and its own CrewAI `LLM` instance pointed at Groq (the Researcher uses a lower temperature for factual accuracy; the Writer uses a higher temperature for more natural prose). The API key is passed into each `LLM` at call time — from the Streamlit sidebar for the web app, or from `.env` for the CLI app.
2. Two `Task`s are defined. The **writing task** includes `context=[research_task]`, which tells CrewAI: "give this agent the full output of the research task as part of its input."
3. A `Crew` bundles the agents and tasks together with `process=Process.sequential`, meaning task 1 always finishes before task 2 starts.
4. `run_crew(topic, api_key)` calls `crew.kickoff(inputs={"topic": topic})` and returns the final article text, ready to display or save.

---

## 🛠️ Troubleshooting

**`GroqException ... 'cache_breakpoint' is unsupported`**
Some CrewAI versions inject a `cache_breakpoint` field into messages for providers (like Anthropic) that support prompt caching — Groq doesn't support this field and rejects the request. This is fixed by:
- Using `crewai>=1.14.4` (already pinned in `requirements.txt`), **and**
- A small compatibility patch at the top of `crew.py` that neutralizes the field for any CrewAI version.

If you still see this error, run `pip install --upgrade -r requirements.txt` to make sure you're on a patched CrewAI version.

---

## 🔜 Ideas to extend this (Phase 8+)

- Add a third **Fact-Checker** agent that reviews the Writer's draft against the Researcher's notes.
- Give the Researcher a real web-search tool (e.g. `crewai_tools.SerperDevTool`) instead of relying only on the LLM's built-in knowledge.
- Add a `Process.hierarchical` manager agent that dynamically decides which agent to call next.
- Swap CrewAI for **LangGraph** to model the same workflow as an explicit state graph.
- Persist session history to a file or database so it survives a page refresh (currently in-memory only, per the design above).
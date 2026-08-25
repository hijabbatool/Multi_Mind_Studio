# 🧠 Multi Mind Studio

A beginner-friendly multi-agent system built with **CrewAI** and **Groq** (running Llama models at very high speed).

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
├── .env.example           # Template for your API key
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

4. **Add your Groq API key:**
   - Get a free key at https://console.groq.com/keys
   - Copy `.env.example` to a new file named `.env`
   - Paste your key in: `GROQ_API_KEY=gsk_...`

---

## ▶️ Running the app

**Option A — Command line:**
```bash
python app_cli.py
```
Type a topic when prompted and watch both agents work in your terminal.

**Option B — Streamlit web UI:**
```bash
streamlit run app_streamlit.py
```
This opens a browser tab where you can type a topic and click "Run Crew".

---

## ⚙️ Changing the model / fixing "model decommissioned" errors

By default the app uses `meta-llama/llama-4-scout-17b-16e-instruct`, one of Groq's current Llama 4 models.

**Groq regularly retires older models** (this is exactly why the original `llama-3.3-70b-versatile` default stopped working). Instead of guessing a model name, this project includes a helper script that asks Groq directly which models your API key can use *right now*:

```bash
python list_groq_models.py
```

This prints a live table of every currently-active model, for example:

```
MODEL ID                                          CONTEXT WINDOW    ACTIVE
--------------------------------------------------------------------------
llama-3.1-8b-instant                               128000            True
meta-llama/llama-4-maverick-17b-128e-instruct      128000            True
meta-llama/llama-4-scout-17b-16e-instruct          128000            True
...
```

Copy whichever model ID you want and put it in your `.env` file:

```
GROQ_MODEL=meta-llama/llama-4-maverick-17b-128e-instruct
```

No code changes needed — `crew.py` automatically reads `GROQ_MODEL` from `.env`. If that variable isn't set, it falls back to the built-in default in `crew.py`.

---

## 🧩 How the collaboration works

1. `crew.py` defines two `Agent`s, each with its own **role**, **goal**, **backstory**, and its own CrewAI `LLM` instance pointed at Groq (the Researcher uses a lower temperature for factual accuracy; the Writer uses a higher temperature for more natural prose).
2. Two `Task`s are defined. The **writing task** includes `context=[research_task]`, which tells CrewAI: "give this agent the full output of the research task as part of its input."
3. A `Crew` bundles the agents and tasks together with `process=Process.sequential`, meaning task 1 always finishes before task 2 starts.
4. `run_crew(topic)` calls `crew.kickoff(inputs={"topic": topic})` and returns the final article text, ready to display or save.

---

## 🔜 Ideas to extend this (Phase 8+)

- Add a third **Fact-Checker** agent that reviews the Writer's draft against the Researcher's notes.
- Give the Researcher a real web-search tool (e.g. `crewai_tools.SerperDevTool`) instead of relying only on the LLM's built-in knowledge.
- Add a `Process.hierarchical` manager agent that dynamically decides which agent to call next.
- Swap CrewAI for **LangGraph** to model the same workflow as an explicit state graph.

# 🧠 Multi Mind Studio

A multi-agent system built with **CrewAI** and **Groq**.

Two agents collaborate on any topic you give them:

| Agent | Role |
|---|---|
| 🔎 **Researcher** | Gathers accurate facts, statistics, and key points |
| ✍️ **Writer/Editor** | Turns those facts into a polished, structured article |

The Researcher's output flows directly into the Writer's task, so the Writer always builds on real research.

---

## 📁 Project structure

```
multi_mind_studio/
├── crew.py              # Agents, tasks, and crew wiring
├── app_cli.py            # Command-line interface
├── app_streamlit.py       # Streamlit web interface
├── list_groq_models.py    # Lists currently-active Groq models
├── requirements.txt
├── .env.example           # Template for your API key (CLI use only)
└── README.md
```

---

## 🚀 Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Groq API key:** https://console.groq.com/keys
   - **Streamlit app:** paste the key directly in the app's sidebar — nothing to save.
   - **CLI app only:** copy `.env.example` to `.env` and add `GROQ_API_KEY=gsk_...`

---

## ▶️ Running the app

**Command line:**
```bash
python app_cli.py
```

**Streamlit web UI:**
```bash
streamlit run app_streamlit.py
```
Enter your Groq API key in the sidebar, type a topic, and click **Run Crew**. Previously generated articles stay visible in **Session History** until you click **Clear History**.

---

## ⚙️ Changing the model

Default model: `openai/gpt-oss-20b` (set via `GROQ_MODEL` in `crew.py`).

To see which models are currently active for your key:
```bash
python list_groq_models.py
```

To override the default, set in `.env`:
```
GROQ_MODEL=meta-llama/llama-4-maverick-17b-128e-instruct
```

---

## 🛠️ Troubleshooting

**`GroqException ... 'cache_breakpoint' is unsupported`**
Fixed by using `crewai>=1.14.4` (already pinned in `requirements.txt`). If you still see this, run:
```bash
pip install --upgrade -r requirements.txt
```
"""
app_streamlit.py
-----------------
Streamlit UI for Multi Mind Studio.

Run it locally with:

    streamlit run app_streamlit.py

Or deploy it directly on Streamlit Community Cloud -- since each visitor
enters their own Groq API key in the sidebar, no secret key needs to be
stored in the repo or in Streamlit's secrets manager.

Features:
    - Sidebar input for the user's own Groq API key (validated before running).
    - A 2-agent CrewAI pipeline (Researcher -> Writer) powered by Groq.
    - Session history: every topic + generated article stays visible on
      screen for the rest of the session (st.session_state), newest first.
    - "Clear History" button (sidebar): wipes ALL saved articles at once.
"""

import streamlit as st
from crew import run_crew

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Multi Mind Studio", page_icon="🧠", layout="centered")

st.title("🧠 Multi Mind Studio")
st.caption("A two-agent CrewAI pipeline powered by Groq (openai/gpt-oss-20b)")

st.markdown(
    """
    **How it works:**
    1. 🔎 **The Researcher** gathers key facts about your topic.
    2. ✍️ **The Writer/Editor** turns those facts into a polished article.

    Enter a topic below and click **Run Crew** to see them work together.
    """
)

# ---------------------------------------------------------------------------
# Session state setup
# ---------------------------------------------------------------------------
# `history` holds a list of dicts: {"topic": str, "article": str}
# Newest entries are inserted at the front so the latest run is always on top.
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------------------------------------------------
# Sidebar: user-provided Groq API key + session controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("🔑 Groq API Key")
    st.markdown(
        "Enter your own Groq API key to run this app. "
        "Get a free key at [console.groq.com/keys](https://console.groq.com/keys)."
    )
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Your key is only used for this session and is never stored.",
    )
    st.caption("Your key stays in your browser session and is not saved anywhere.")

    st.divider()

    st.header("🗂️ Session")
    st.caption(f"{len(st.session_state.history)} article(s) generated this session.")

    if st.button("🧹 Clear History", use_container_width=True, disabled=not st.session_state.history):
        st.session_state.history = []
        st.rerun()

has_api_key = bool(groq_api_key and groq_api_key.strip())

# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
topic = st.text_input(
    "Topic to research and write about",
    placeholder="e.g. The impact of AI agents on software engineering",
)

if not has_api_key:
    st.warning("🔒 Please enter your Groq API key in the sidebar to run the crew.")

run_button = st.button(
    "🚀 Run Crew",
    type="primary",
    disabled=not (topic.strip() and has_api_key),
)

# ---------------------------------------------------------------------------
# Run the crew and store the result in session history
# ---------------------------------------------------------------------------
if run_button and topic.strip() and has_api_key:
    with st.status("Agents are working...", expanded=True) as status:
        st.write("🔎 Researcher is gathering facts...")
        try:
            final_article = run_crew(topic.strip(), api_key=groq_api_key.strip())
        except Exception as e:
            status.update(label="Something went wrong", state="error")
            st.error(f"Error while running the crew: {e}")
        else:
            st.write("✍️ Writer has finished drafting the article.")
            status.update(label="Done!", state="complete")

            # Save this run at the top of the session history.
            st.session_state.history.insert(
                0, {"topic": topic.strip(), "article": final_article}
            )

            # Rerun so the sidebar's article count and Clear History button
            # (which are rendered earlier in the script) immediately reflect
            # the newly added history entry. Only done on success -- an
            # error message above should stay visible instead of vanishing.
            st.rerun()

elif not topic.strip():
    st.info("👆 Enter a topic above to get started.")

# ---------------------------------------------------------------------------
# Display session history (most recent first)
# ---------------------------------------------------------------------------
if st.session_state.history:
    st.markdown("---")
    st.subheader("📚 Session History")

    for i, entry in enumerate(st.session_state.history):
        label = f"📄 {entry['topic']}" if i > 0 else f"📄 {entry['topic']} (latest)"
        with st.expander(label, expanded=(i == 0)):
            st.markdown(entry["article"])
            st.download_button(
                label="⬇️ Download as Markdown",
                data=entry["article"],
                file_name=f"multi_mind_studio_{i}.md",
                mime="text/markdown",
                key=f"download_{i}",
            )
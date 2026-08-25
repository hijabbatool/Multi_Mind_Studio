"""
crew.py
--------
Core "brain" of Multi Mind Studio.

This file defines:
    1. The LLM connection (Groq, running open models at very high speed).
    2. Two collaborating AI agents:
         - Researcher  -> gathers facts about a topic
         - Writer/Editor -> turns those facts into a polished article
    3. Two sequential tasks that connect the agents (Researcher's output
       becomes the Writer's input).
    4. A build_crew() function that wires everything together and can be
       imported by both the CLI app (app_cli.py) and the Streamlit app
       (app_streamlit.py).

Keeping this logic in its own file means the CLI and the web UI never
duplicate code -- they just call run_crew(topic, api_key).

NOTE ON THE API KEY:
For local/CLI use, the key can still come from a ".env" file
(GROQ_API_KEY=...). For the Streamlit Cloud deployment, the key is
instead entered by each user in the sidebar and passed in at call time --
this means the app never needs a shared secret baked into the repo, and
each visitor uses their own Groq quota.
"""

import os
from dotenv import load_dotenv

from crewai import Agent, Task, Crew, Process, LLM

# ---------------------------------------------------------------------------
# 0. WORKAROUND: Groq does not support the "cache_breakpoint" field that
#    newer CrewAI versions inject into messages (it's meant for providers
#    like Anthropic that support prompt caching). Without this patch, every
#    call to Groq fails with:
#      GroqException - 'messages.0': property 'cache_breakpoint' is unsupported
#    See: https://github.com/crewAIInc/crewAI/issues/5886
#    This neutralizes the injection; safe no-op on CrewAI versions that
#    don't have this module/function.
# ---------------------------------------------------------------------------
try:
    import crewai.llms.cache as _crewai_cache
    _crewai_cache.mark_cache_breakpoint = lambda msg: msg
except (ImportError, AttributeError):
    pass

# ---------------------------------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES (used as a fallback, e.g. for app_cli.py)
# ---------------------------------------------------------------------------
load_dotenv()

DEFAULT_GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ---------------------------------------------------------------------------
# 2. CHOOSE THE GROQ MODEL
# ---------------------------------------------------------------------------
# IMPORTANT: Groq regularly retires older models. If this model ID ever
# stops working, it means Groq has removed it -- run list_groq_models.py
# with a valid key to see what's currently available and update the
# value below (or set a GROQ_MODEL env var to override it).
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def get_llm(api_key: str, temperature: float = 0.6) -> LLM:
    """
    Creates and returns an LLM instance (CrewAI's own LLM wrapper, which
    is what Agent(llm=...) expects in current CrewAI versions) pointed at
    Groq's OpenAI-compatible endpoint.

    api_key:     the Groq API key to use for this request (per-user key
                 entered in the Streamlit sidebar, or the .env fallback
                 for the CLI app).
    temperature: controls creativity/randomness.
                 Lower (e.g. 0.2) = more focused/factual -> good for research.
                 Higher (e.g. 0.7) = more creative -> good for writing.
    """
    if not api_key:
        raise ValueError(
            "No Groq API key was provided. Enter one in the sidebar, or "
            "set GROQ_API_KEY in a local .env file."
        )

    return LLM(
        model=f"groq/{GROQ_MODEL}",
        api_key=api_key,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# 3. DEFINE THE AGENTS
# ---------------------------------------------------------------------------
def build_researcher_agent(api_key: str) -> Agent:
    """
    Agent 1: The Researcher
    Focused on facts, not prose. Low temperature keeps it precise.
    """
    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Gather accurate, well-organized, and up-to-date information, "
            "facts, statistics, and key points about the topic: {topic}."
        ),
        backstory=(
            "You are a meticulous research analyst who has spent years "
            "digging up reliable facts for journalists and authors. You "
            "value accuracy over flair, and you always structure your "
            "findings clearly using bullet points and short headings so "
            "that someone else can easily use them later."
        ),
        llm=get_llm(api_key, temperature=0.3),
        verbose=True,          # prints the agent's thought process to console
        allow_delegation=False,  # this agent should not hand off work to others
    )


def build_writer_agent(api_key: str) -> Agent:
    """
    Agent 2: The Writer / Editor
    Takes the researcher's raw notes and turns them into a polished article.
    Higher temperature allows for more natural, engaging language.
    """
    return Agent(
        role="Professional Content Writer & Editor",
        goal=(
            "Transform raw research notes into a clear, engaging, and "
            "well-structured article or report about: {topic}."
        ),
        backstory=(
            "You are an experienced editor who has written for major "
            "online publications. You take dry research notes and turn "
            "them into content that is easy to read, logically organized "
            "with headings, and professional in tone -- without inventing "
            "facts that were not in the research."
        ),
        llm=get_llm(api_key, temperature=0.7),
        verbose=True,
        allow_delegation=False,
    )


# ---------------------------------------------------------------------------
# 4. DEFINE THE TASKS (this is what makes the agents "collaborative")
# ---------------------------------------------------------------------------
def build_tasks(researcher: Agent, writer: Agent) -> list[Task]:
    """
    Creates the two sequential tasks.

    Because CrewAI runs tasks in order (Process.sequential) and the second
    task's `context` includes the first task, the Writer automatically
    receives the Researcher's full output as input. This is the
    "output flows directly into the next agent" behavior you asked for.
    """

    research_task = Task(
        description=(
            "Research the topic: '{topic}'.\n"
            "Collect the most important facts, definitions, statistics, "
            "recent developments, and any notable examples or context. "
            "Organize your findings into clear bullet points grouped under "
            "short sub-headings (e.g. 'Overview', 'Key Facts', "
            "'Recent Developments', 'Examples'). Do not write final prose "
            "yet -- just structured, factual notes for the writer to use."
        ),
        expected_output=(
            "A well-organized set of research notes in bullet-point form, "
            "grouped under clear sub-headings, covering the key facts and "
            "context needed to write a full article on the topic."
        ),
        agent=researcher,
    )

    writing_task = Task(
        description=(
            "Using ONLY the research notes provided to you, write a "
            "polished, professional article about: '{topic}'.\n"
            "Requirements:\n"
            "  - Add an engaging title.\n"
            "  - Use a short introduction, 2-4 clearly headed body "
            "sections, and a brief conclusion.\n"
            "  - Keep the tone professional but easy to read.\n"
            "  - Do not invent facts that are not supported by the "
            "research notes."
        ),
        expected_output=(
            "A complete, well-structured article in Markdown format with "
            "a title, headings, and a conclusion -- ready to publish."
        ),
        agent=writer,
        context=[research_task],  # <-- this is the key line: Writer sees Researcher's output
    )

    return [research_task, writing_task]


# ---------------------------------------------------------------------------
# 5. BUILD THE FULL CREW
# ---------------------------------------------------------------------------
def build_crew(api_key: str) -> Crew:
    """
    Assembles agents + tasks into a runnable Crew.
    Call crew.kickoff(inputs={"topic": "your topic"}) to execute it.

    api_key: the Groq API key to use for both agents in this run.
    """
    researcher = build_researcher_agent(api_key)
    writer = build_writer_agent(api_key)
    tasks = build_tasks(researcher, writer)

    crew = Crew(
        agents=[researcher, writer],
        tasks=tasks,
        process=Process.sequential,  # Researcher runs first, then Writer
        verbose=True,
    )
    return crew


def run_crew(topic: str, api_key: str | None = None) -> str:
    """
    Convenience function used by both the CLI and Streamlit front-ends.
    Runs the full crew on a given topic and returns the final article text.

    api_key: Groq API key to use. If omitted, falls back to GROQ_API_KEY
             from a local .env file (useful for app_cli.py). The Streamlit
             app always passes the key the user entered in the sidebar.
    """
    key_to_use = api_key or DEFAULT_GROQ_API_KEY
    crew = build_crew(key_to_use)
    result = crew.kickoff(inputs={"topic": topic})
    # CrewAI's kickoff() returns a CrewOutput object; .raw holds the final text.
    return getattr(result, "raw", str(result))
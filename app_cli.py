"""
app_cli.py
----------
Simple command-line interface for Multi Mind Studio.

Run it from VS Code's terminal with:

    python app_cli.py

You'll be asked to type a topic. The Researcher agent and Writer agent
will then run one after another (you'll see their reasoning printed live
because verbose=True in crew.py), and the final article prints at the end.
"""

from crew import run_crew


def main() -> None:
    print("=" * 60)
    print("  MULTI MIND STUDIO  —  CrewAI + Groq (Llama) CLI")
    print("=" * 60)
    print("Two agents will work together:")
    print("  1) Researcher -> gathers facts")
    print("  2) Writer/Editor -> turns facts into a polished article\n")

    topic = input("Enter a topic to research and write about: ").strip()

    if not topic:
        print("No topic entered. Exiting.")
        return

    print(f"\n🚀 Starting crew for topic: '{topic}'\n")
    print("-" * 60)

    final_article = run_crew(topic)

    print("\n" + "=" * 60)
    print("  ✅ FINAL ARTICLE")
    print("=" * 60 + "\n")
    print(final_article)

    # Optionally save the result to a file for convenience.
    filename = "output_article.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_article)
    print(f"\n📄 Article also saved to: {filename}")


if __name__ == "__main__":
    main()

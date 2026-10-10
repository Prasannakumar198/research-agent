"""
Research Agent: give it a topic, it searches the web, reads pages,
and saves a markdown report to disk. Runs fully on open-source models (Ollama).

Setup:
    1. Install Ollama from https://ollama.com and run: ollama pull qwen2.5:7b
    2. pip install -r requirements.txt
    3. python agent.py "Best open-source LLMs for running on a laptop in 2026"
"""
import re
import sys
from pathlib import Path

import ollama
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

MODEL = "qwen2.5:7b"   # try "llama3.1:8b" or a bigger model if your laptop allows
MAX_STEPS = 10         # safety limit so the agent can never loop forever
OUTPUT_DIR = Path("reports")


# ---------- TOOLS (what the agent can DO) ----------
# Docstrings matter: the model reads them to decide when to use each tool.

def web_search(query: str) -> str:
    """Search the web and return the top results (title, url, snippet).

    Args:
        query: The search query.
    """
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Search failed: {e}"
    return "\n\n".join(f"{r['title']}\n{r['href']}\n{r['body']}" for r in results) or "No results."


def read_page(url: str) -> str:
    """Download a web page and return its readable text (first ~4000 characters).

    Args:
        url: The full URL of the page to read.
    """
    try:
        html = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).text
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        return text[:4000]
    except Exception as e:
        return f"Could not read page: {e}"


def save_report(title: str, markdown: str) -> str:
    """Save the final report as a markdown file. Call this once, when research is done.

    Args:
        title: Short title, used as the file name.
        markdown: The full report in markdown, including source URLs.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    name = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "report"
    path = OUTPUT_DIR / f"{name}.md"
    path.write_text(markdown, encoding="utf-8")
    return f"Report saved to {path}"


TOOLS = {f.__name__: f for f in (web_search, read_page, save_report)}

SYSTEM_PROMPT = """You are a research agent. Given a topic:
1. Run 2-3 different web searches.
2. Read the 2-3 most relevant pages with read_page.
3. Call save_report ONCE with a clear markdown report: summary, key findings, and a Sources list.
Never invent facts or URLs. Only use what the tools returned."""


# ---------- THE AGENT LOOP (this is the "agent" part) ----------
def run_agent(topic: str) -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Research this topic: {topic}"},
    ]

    for step in range(1, MAX_STEPS + 1):
        response = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values()))
        msg = response.message
        messages.append(msg)

        # No tool requested -> the model thinks it is finished
        if not msg.tool_calls:
            print(f"\nAgent finished: {msg.content}")
            return

        # The model asked to use tools: run them and feed the results back
        for call in msg.tool_calls:
            name, args = call.function.name, call.function.arguments
            print(f"[step {step}] {name}({args})")
            result = TOOLS[name](**args) if name in TOOLS else f"Unknown tool: {name}"
            messages.append({"role": "tool", "tool_name": name, "content": str(result)})

            if name == "save_report":
                print(f"\n{result}")
                return

    print("Stopped: reached MAX_STEPS without a saved report.")


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "Difference between AI agents and LLMs"
    run_agent(topic)
# Research Agent

A local AI agent built with Python and Ollama that researches any topic on the web and saves a sourced markdown report. It runs fully on open-source models, with no paid API.

## What it does

Researching a topic by hand means searching, opening several pages, reading them, and writing notes. This agent does that loop for you. You give it one sentence, such as "Best open-source LLMs to run on a laptop", and it searches the web, reads the most relevant pages, and saves a report with a summary, key findings, and source links into the `reports/` folder.

## Agent vs. LLM

A normal LLM only takes text in and gives text out. It cannot search the internet, open a page, or save a file, and it stops after one answer.

An agent is an LLM placed inside a loop and given tools. It decides which tool to use, the tool runs, the result goes back to the model, and it decides the next step until the goal is finished.

**Agent = LLM (brain) + Tools (hands) + Loop (keeps going) + Goal**

The model never runs tools itself. It only asks for them, and my Python code runs them.

## How it works

```
Topic -> Model decides -> Tool runs -> Result returns to model -> Repeat -> Report saved
```

1. `agent.py` sends the topic and the list of tools to the model running in Ollama.
2. The model replies with a tool request, such as `web_search("...")`.
3. My code runs the tool and sends the result back to the model.
4. This repeats until the model calls `save_report`, or the step limit (`MAX_STEPS`) is reached.

**Tools:**
- `web_search`: searches DuckDuckGo and returns titles, links, and snippets
- `read_page`: downloads a page and returns its text
- `save_report`: writes the final markdown report to disk

## Setup

1. Install [Ollama](https://ollama.com).
2. Download the model:
   ```
   ollama pull qwen2.5:7b
   ```
3. Install the Python libraries (Python 3.10+):
   ```
   pip install -r requirements.txt
   ```
4. Run the agent:
   ```
   python agent.py "Your research topic here"
   ```

The model name can be changed in `agent.py` (`MODEL = "qwen2.5:7b"`). Smaller laptops can use `qwen2.5:3b`.

## Sample output

- best-open-source-llms-for-laptop
- [Best open-source LLMs for laptop](reports/best-open-source-llms-for-laptop.md)
- [Top Python libraries for building AI agents](reports/top-python-libraries-for-building-ai-agents.md)



## Limitations and next steps

**Limitations** (edit this with what you actually noticed):
- Small local models sometimes skip steps, repeat a search, or write a shorter report than expected.
- Pages are cut to the first 4,000 characters, so long articles are only partly read.
- Search quality depends on DuckDuckGo results, and some sites block scraping.
- Facts should be checked against the listed sources.

**Next steps:**
- Compare reports from different models (qwen2.5, llama3.1, mistral)
- Add memory so it does not repeat research on topics it has already covered
- Add more tools, such as emailing the report or saving to Notion
- Rebuild the same agent with LangGraph to compare with the plain-Python version

## What I learned

- The basic fundamentals on how to use Ollama, and different approach in building the agent.

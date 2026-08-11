# Google Search Agent (Google ADK)

A conversational agent built with the **Google Agent Development Kit (ADK)** that answers user questions and can search Google in real time via the ADK's built-in `google_search` tool.

## Overview

The agent is defined as `root_agent`, an instance of `google.adk.agents.llm_agent.Agent`, powered by the `gemini-2.5-flash` model. It's a general-purpose Q&A assistant augmented with live web search, so it can answer questions that require current or up-to-date information rather than relying solely on the model's training data.

## How It Works

1. The user asks a question.
2. The LLM decides, based on the question, whether it can answer directly or needs current information.
3. If needed, it calls the built-in `google_search` tool to retrieve relevant web results.
4. The agent incorporates the search results into its response and answers the user.

## Files

- `agent.py` (or similar) — defines `root_agent`.
- `__init__.py` — exposes the `agent` module so the package can be imported (`from . import agent`).

## Setup

### 1. Install dependencies

```bash
pip install google-adk
```

### 2. Authentication

`google_search` is a built-in ADK tool that requires the underlying model/API access to be configured correctly (e.g. Google AI Studio or Vertex AI credentials, depending on how the ADK is set up). Make sure your environment is authenticated per the [ADK documentation](https://google.github.io/adk-docs/) before running the agent.

## Agent Configuration

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `google_search_agent` |
| `description` | A helpful assistant for user questions |
| `instruction` | Answer user questions to the best of your knowledge |
| `tools` | `[google_search]` |

## Tool: `google_search`

This is a **built-in ADK tool** (imported from `google.adk.tools`), not a custom function — there's no implementation to review in this file. It gives the agent the ability to issue web searches and read back results as part of its reasoning process, similar to how search-augmented LLMs ground answers in current information.

> Note: unlike custom `FunctionTool`s, built-in tools like `google_search` typically can't be freely mixed with other custom tools in the same agent, depending on the ADK version/backend — check the ADK docs if you plan to add more tools later.

## Notes on the Commented-Out Code

The top of the file contains the original, simpler version of the agent (kept as a docstring/comment):

- Same `google_search_agent`, but **without** the `google_search` tool — a plain knowledge-only assistant with no ability to look things up in real time.

The active version adds the `google_search` tool so the agent can answer questions beyond its training cutoff or about current events.

## Example Interaction

**User:** "What's the latest version of the Google ADK?"

**Agent:**
1. Recognizes this needs current information
2. Calls `google_search` with a relevant query
3. Reads the results and responds with an up-to-date answer, rather than guessing from training data

## Production Considerations

- Consider tightening the `instruction` to clarify when the agent should search vs. answer directly (e.g. "always search for questions about current events, prices, or recent releases").
- Monitor search tool usage/costs if applicable to your ADK deployment.
- Add citation/source attribution in the instruction if you want the agent to reference where information came from.
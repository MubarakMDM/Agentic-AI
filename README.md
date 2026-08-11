# ADK Deployment & Command Cheatsheet

Quick reference notes for deploying Google ADK agents to the cloud, common `adk` CLI commands, environment setup, and everyday shell/editor shortcuts.

## Deploying to Cloud

```bash
adk deploy agent_engine \
  --project=agentic-ai-503915 \
  --region=us-central1 \
  --display_name=agent_app \
  first_agent
```

**Region notes**
- Not all regions work reliably — `eu` and some others can be inconsistent.
- Use the full region format (e.g. `us-central1`) rather than a short name.
- If a specific model isn't working in a given region, try changing the model version rather than the region.
- `eu` tends to be slow — prefer `us` (e.g. `us-central1`) or `asia-south1` (Mumbai, India) for better performance.

**After deployment**

Check the deployment at:

```
Agent Platform → Agents → Deployments → <app name> → Playground
```

## `adk` CLI Commands

| Command | Description |
|---|---|
| `gcloud auth application-default login` | Authenticate with Google Cloud (application default credentials) |
| `gcloud auth list` | Check current authenticated accounts |
| `adk create <file name>` | Create a new ADK agent project/file |
| `adk web` | Launch the ADK web interface |

## Python Environment Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip list
pip install -r requirements.txt
```

## Comment / Uncomment (Editor Shortcuts)

| Shortcut | Action |
|---|---|
| `Ctrl + K` then `C` | Comment selected lines |
| `Ctrl + K` then `U` | Uncomment selected lines |

## Bash Commands

| Command | Description |
|---|---|
| `touch <filename>` | Create a new empty file |
| `mkdir <dir name>` | Create a new directory |
| `cp <old file> <new file>` | Copy a file to a new location/name |
| `echo "text or content" > <file name>` | Write text into a file (overwrites existing content) |
| `cat <file name>` | Display the contents of a file |
| `vim <file name>` | Open a file in Vim for editing |

**Vim quick reference**
- `Esc` then `:q!` — quit without saving
- `Esc` then `:wq` — save and quit



# Travel Plan Agent (Google ADK)

A multi-agent travel planning assistant built with the **Google Agent Development Kit (ADK)**. The main agent (`root_agent`) helps users with weather forecasts, distance calculations, flight prices, and general travel questions — delegating web search to a dedicated sub-agent when needed. Observability is wired up via Langfuse tracing at import time.

## Overview

This module defines two agents:

- **`search_agent`** (`SearchAgent`) — a specialist agent whose only job is to run Google searches and report findings. It's wrapped as an `AgentTool` so the main agent can call it like any other tool.
- **`root_agent`** (`travel_plan_agent`) — the main travel-planning assistant. It has four tools available and picks between them (or answers directly) based on the type of question asked.

Both agents run on `gemini-2.5-flash`.

## Architecture

```
root_agent (travel_plan_agent)
├── get_weather            (custom tool)
├── calculate_distance     (custom tool)
├── get_ticket_price       (custom tool)
└── AgentTool(search_agent) → SearchAgent → google_search (built-in tool)
```

This is a common ADK pattern: instead of giving `google_search` directly to `root_agent`, it's isolated inside a dedicated sub-agent (`search_agent`) and exposed to the main agent as a callable tool via `AgentTool`. This keeps search behavior self-contained and lets it be reused or swapped independently of the main agent's logic.

## Files

- `agent.py` (or similar) — defines `search_agent` and `root_agent`.
- `__init__.py` — exposes the `agent` module so the package can be imported (`from . import agent`).
- `tools/weather.py` — defines `get_weather`.
- `tools/distance.py` — defines `calculate_distance`.
- `tools/flights.py` — defines `get_ticket_price`.
- `Observability/tracing.py` — defines `setup_tracing()` (Langfuse + OpenInference instrumentation).

## Observability

```python
from Observability.tracing import setup_tracing
setup_tracing()
```

This runs at **import time**, before either agent is defined, so all subsequent agent and tool calls in the process are automatically traced (assuming Langfuse credentials are configured — see that module's own README for setup). If Langfuse authentication fails, tracing is simply disabled and the agents still run normally.

## Sub-Agent: `SearchAgent`

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `SearchAgent` |
| `tools` | `[google_search]` (built-in ADK tool) |

Its only job is: given a query, search and report back what it finds. It has no other responsibilities, which keeps its behavior predictable when called as a tool from `root_agent`.

## Main Agent: `travel_plan_agent`

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `travel_plan_agent` |
| `description` | A planning assistant for travel — weather forecasts and other travel questions |
| `tools` | `[get_weather, calculate_distance, get_ticket_price, AgentTool(search_agent)]` |

### Tool selection instructions

1. **`get_weather`** — only for weather/temperature/rain/forecast/packing questions about a specific city.
   - `forecast_days=2` for near-term (next couple of days) questions.
   - `forecast_days=10` for questions about the coming week or later.
   - Must always report city, date, condition, and temperature range — never guess weather from memory.

2. **`SearchAgent`** (via `AgentTool`) — only for non-weather questions the agent isn't already confident about: current events, prices, opening hours, visa rules, local attractions, time-sensitive info. Explicitly told not to search when it already knows the answer.

3. **`calculate_distance`** — only for straight-line ("as the crow flies") distance between two cities, in km and miles. The agent is told to clarify that this isn't driving/flight route distance if the user needs precise travel-time planning.

4. **`get_ticket_price`** — only for flight fares/booking questions between two cities on a specific date.
   - Requires `travel_date` in `YYYY-MM-DD` format; the agent should ask rather than guess if missing.
   - Must report the cheapest price found and disclose it's **test/sandbox pricing (Duffel Airways)**, not a live bookable fare.

For anything needing none of these tools (general travel tips, packing advice, itinerary ideas), the agent answers directly.

## Known Issue

The instruction opens with **"You have two tools"**, but `root_agent` is actually given **four** tools (`get_weather`, `calculate_distance`, `get_ticket_price`, and the `SearchAgent` `AgentTool`), and all four are documented in the numbered list that follows. This is likely a leftover from an earlier version of the prompt before `calculate_distance` and `get_ticket_price` were added — worth updating to "You have four tools" (or removing the count entirely) to avoid confusing the model or future maintainers.

## Dependencies

```bash
pip install google-adk langfuse openinference-instrumentation-google-adk
```

Plus whatever HTTP/client libraries `get_weather`, `calculate_distance`, and `get_ticket_price` rely on internally (not shown in this file).

## Setup

1. Configure Langfuse credentials (see `Observability/tracing.py` README) — optional but recommended for tracing.
2. Ensure `tools/weather.py`, `tools/distance.py`, and `tools/flights.py` are implemented and importable relative to this package.
3. Ensure Google Search / ADK authentication is set up per the [ADK documentation](https://google.github.io/adk-docs/).

## Example Interactions

**User:** "What's the weather like in Lisbon this weekend?"
→ `root_agent` calls `get_weather(city="Lisbon", forecast_days=10)` (if "this weekend" falls beyond the 2-day window) and reports city, date, condition, and temperature range.

**User:** "How far is Paris from Rome?"
→ `root_agent` calls `calculate_distance`, returns straight-line distance, and notes it isn't a driving/flight route distance.

**User:** "Cheapest flight from Paris to Rome on 2026-09-10?"
→ `root_agent` calls `get_ticket_price(from="Paris", to="Rome", travel_date="2026-09-10")`, reports the cheapest fare found, and discloses it's sandbox (Duffel Airways) test pricing.

**User:** "Do I need a visa to visit Japan?"
→ `root_agent` delegates to `SearchAgent` (since this is time-sensitive/factual and not something to guess), which runs a Google search and reports back.

**User:** "Any packing tips for a beach trip?"
→ `root_agent` answers directly, no tool call.

## Production Considerations

- Fix the "You have two tools" vs. four-tools mismatch in the instruction.
- Consider rate-limiting or caching `SearchAgent` calls if search costs/quotas are a concern.
- Make sure `get_ticket_price`'s sandbox-pricing disclosure is prominent enough that users don't mistake it for a bookable fare.
- Add error handling guidance in the instruction for when a tool call fails (e.g. weather API down, no flights found).
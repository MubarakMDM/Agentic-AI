# Multi-Agent Research Report System

A multi-agent system built with Google's Agent Development Kit (ADK) that coordinates research, data analysis, and report writing through a manager agent.

## Overview

This system uses a **manager agent** that orchestrates three specialized sub-agents to produce research reports:

1. **Research Agent** — gathers sources and information on the requested topic
2. **Data Agent** — performs numeric/statistical analysis when the topic requires it
3. **Writer Agent** — drafts the final report using the gathered research and analysis

The manager agent (`root_agent`) uses each sub-agent as a callable tool (`AgentTool`), deciding at runtime which agents to invoke based on the nature of the request.

## Architecture

```
                ┌─────────────────┐
                │  Manager Agent   │
                │ (gemini-2.5-flash)│
                └────────┬─────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                 │
        ▼                ▼                 ▼
 ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
 │ Research     │  │ Data Agent   │  │ Writer Agent │
 │ Agent        │  │ (optional)   │  │              │
 └─────────────┘  └─────────────┘  └──────────────┘
```

## How It Works

For each incoming request, the manager agent follows this workflow:

1. Calls `research_agent` to gather relevant sources.
2. Calls `data_agent` **only if** the topic requires numeric analysis.
3. Calls `writer_agent` to draft the final report using the outputs from the previous steps.

## Project Structure

```
.
├── manager_agent.py      # Root/manager agent definition (this file)
├── research_agent.py      # Sub-agent: research and source gathering
├── data_agent.py           # Sub-agent: numeric/data analysis
├── writer_agent.py         # Sub-agent: report drafting
└── README.md
```

## Requirements

- Python 3.12+
- `google-adk` (Google Agent Development Kit)
- Access to a Gemini model backend (Google AI Studio or Vertex AI)

## Setup

1. Install dependencies:
   ```bash
   pip install google-adk
   ```

2. Configure authentication for the model backend (Vertex AI or Google AI Studio), e.g.:
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project YOUR_PROJECT_ID
   ```

3. Ensure `research_agent`, `data_agent`, and `writer_agent` are defined in their respective modules alongside this file.

## Usage

Run the agent via the ADK dev server/CLI (adjust to your project's entry point):

```bash
adk web
```

Then interact with `manager_agent` through the ADK dev UI or API, submitting a research topic. The manager will automatically coordinate the sub-agents to produce a final report.

## Notes

- The `data_agent` step is conditional — it's only triggered when the manager determines the topic needs numeric analysis, so simple qualitative topics skip straight to the writer.
- Model used: `gemini-2.5-flash`.
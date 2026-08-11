# Story Writer Agent (Google ADK)

A creative writing agent built with the **Google Agent Development Kit (ADK)** that writes short stories based on a topic or details provided by the user.

## Overview

The agent is defined as `root_agent`, an instance of `google.adk.agents.llm_agent.Agent`, powered by the `gemini-2.5-flash` model. It has no tools — it's a pure prompt-driven agent whose behavior is entirely shaped by a detailed `instruction` string that acts as a short-story style guide.

## How It Works

1. The user gives a topic, theme, or set of details (e.g. *"a story about a lighthouse keeper who finds a message in a bottle"*).
2. The agent writes a short story exploring that topic, following the length and craft rules in its instruction (see below).
3. The output includes a short title followed by the story itself, with no extra commentary unless explicitly requested.

## Files

- `agent.py` (or similar) — defines `root_agent`.
- `__init__.py` — exposes the `agent` module so the package can be imported (`from . import agent`).

## Agent Configuration

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `story_writer_agent` |
| `description` | Write a short story with details provided by the user in the prompt |
| `tools` | None (pure LLM generation) |

## Instruction Breakdown

**Length**
- The story must not exceed 100 words.
- Even if the user explicitly asks for a longer story, the agent is instructed to stick to the 100-word cap.

**Craft**
- Uses a clear beginning / middle / end structure.
- Uses simple language and avoids complex sentence structures.

**Output format**
- A short title for the story.
- The story itself — no lengthy explanations unless the user asks for them.

## Example Interaction

**User:** "Write a story about an astronaut who misses home"

**Agent:**
```
Title: The Last Transmission

Maya floated past the window, Earth a blue marble below...
[story continues, staying under 100 words, with a clear beginning, middle, and end]
```

**User:** "Can you write a 500-word story instead?"

**Agent:** Still returns a story capped at 100 words, per the strict length rule in the instruction — it doesn't expand even when explicitly asked.

## Notes / Minor Issues

- The instruction has a couple of typos ("discovring", "strick") — harmless for the model but worth cleaning up if this instruction is reused or shown to other developers.
- The rule "even if the user asks explicitly for a story longer than 100 words then only give other strick to 100 words" is a bit ambiguously worded but the intent is clear: **the 100-word cap always wins**, even against explicit user requests. If that's not the desired behavior (e.g. you *do* want to honor longer requests), the instruction will need to be reworded.

## Production Considerations

- If longer stories should be supported on request, add a conditional rule (e.g. "default to 100 words unless the user specifies a length, up to a max of N words") instead of a hard, non-negotiable cap.
- Consider specifying genre/tone defaults (e.g. what happens if the user gives a very vague topic) similar to how mood defaults could be handled in other creative agents.
- If consistent formatting matters downstream (e.g. parsing title vs. body), consider instructing a stricter output format (e.g. a fixed "Title: ... \n\n Story: ..." template) rather than relying on free-form labeling.
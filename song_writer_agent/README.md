# Song Writer Agent (Google ADK)

A creative writing agent built with the **Google Agent Development Kit (ADK)** that generates original song lyrics based on a theme, mood, or genre supplied by the user.

## Overview

The agent is defined as `root_agent`, an instance of `google.adk.agents.llm_agent.Agent`, powered by the `gemini-2.5-flash` model. It has no tools — it's a pure prompt-driven agent whose behavior is fully shaped by a detailed `instruction` string that acts as a songwriting style guide.

## How It Works

1. The user provides a theme, mood, and/or genre (e.g. *"write a heartbreak song, folk style"*).
2. The agent writes original lyrics following the structural and stylistic rules in its instruction (see below).
3. If no mood/genre is given, the agent either asks a brief clarifying question first, or defaults to an upbeat pop style and notes that assumption.
4. Output is lyrics only — no lengthy explanation — kept to 3–5 lines per the instruction.

## Files

- `agent.py` (or similar) — defines `root_agent`.
- `__init__.py` — exposes the `agent` module so the package can be imported (`from . import agent`).

## Agent Configuration

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `song_writer_agent` |
| `description` | Write original song lyrics based on a theme, mood, or genre provided by the user |
| `tools` | None (pure LLM generation) |

## Instruction Breakdown

The `instruction` prompt encodes the agent's "songwriting rules":

**Structure**
- Defaults to a verse–chorus structure (Verse 1, Chorus, Verse 2, Chorus), adding a Bridge only if it clearly improves the song.
- Each section is clearly labeled (e.g. "Verse 1", "Chorus:", "Bridge:").
- The chorus wording stays consistent across repeats, so it reads like a real recurring hook.

**Style**
- Tone and word choice match the requested mood/genre (e.g. upbeat/simple for pop, introspective/imagery-rich for folk, aggressive/rhythmic for rock or rap).
- Uses rhyme and rhythm suited to song lyrics rather than free verse.
- If mood/genre isn't specified, the agent either asks a brief clarifying question or defaults to upbeat pop and states that assumption.

**Output format**
- Lyrics only — no explanations unless explicitly requested.
- Constrained to **3–5 lines** total.

## Known Issue

The instruction says to "keep the output focused on the lyrics" but also to follow a multi-section verse/chorus/verse/chorus structure — that's naturally more than 3–5 lines (even a minimal version is usually 8+ lines: two verses plus a repeated chorus). The **"3 to 5 lines" constraint conflicts with the structural requirement** and will likely force the model to either:
- truncate the song unnaturally to fit the line limit, or
- ignore the line limit to satisfy the structure.

If a full structured song is the goal, consider removing or loosening the line-count constraint (e.g. "keep each section short — 2-4 lines" instead of capping the whole output at 3-5 lines).

## Example Interaction

**User:** "Write me a rock song about chasing your dreams"

**Agent:** Produces labeled sections (Verse 1, Chorus, Verse 2, Chorus, optionally Bridge) with aggressive/rhythmic tone, rhyme, and a consistent repeating chorus — subject to the line-count caveat above.

**User:** "Write me a song" *(no genre/mood given)*

**Agent:** Either asks a quick clarifying question (e.g. "What mood or genre are you going for?") or defaults to upbeat pop and notes that assumption before writing.

## Production Considerations

- Resolve the structure vs. line-count conflict noted above before relying on this in production.
- If genre coverage matters (pop, folk, rock, rap, etc.), consider testing each explicitly to confirm tone/style differentiation is consistent.
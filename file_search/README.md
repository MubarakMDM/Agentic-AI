# Downloads Search Agent (Google ADK)

A conversational agent built with the **Google Agent Development Kit (ADK)** that helps the user find files in their local `Downloads` folder by searching filenames for a keyword, with an optional date filter.

## Overview

The agent uses `google.adk.agents.LlmAgent` powered by `gemini-2.5-flash`, exposing a single tool — `search_downloads` — wrapped as a `FunctionTool`. When the user mentions a word or phrase (e.g. "CV", "invoice"), the model calls the tool to search the filesystem and reports back matching files.

## How It Works

1. The user asks something like *"Find my CV"* or *"Do I have any invoices from after 2024-01-01?"*
2. The LLM extracts a keyword (and optional date) from the request.
3. It calls `search_downloads(keyword, after_date)`.
4. The tool recursively walks the `Downloads` directory, matching filenames (case-insensitive substring match) and filtering by modification date if `after_date` is provided.
5. Results are sorted newest-first and capped at 50 matches.
6. The agent summarizes the matching files (path + modified date) back to the user.

## Files

- `agent.py` (or similar) — defines `search_downloads` and `root_agent`.
- `__init__.py` — exposes the `agent` module so the package can be imported (`from . import agent`).

## Configuration

```python
DOWNLOADS_DIR = "/mnt/c/Users/mubar/Downloads"
```

This is currently a **hardcoded path** (a WSL-style mount of a Windows Downloads folder). Update this constant if the agent needs to run on a different machine or user account.

## Tool: `search_downloads`

```python
search_downloads(keyword: str, after_date: str = "") -> list[dict]
```

**Arguments**
| Name | Type | Description |
|---|---|---|
| `keyword` | `str` | Substring to search for in filenames (case-insensitive) |
| `after_date` | `str` (optional) | `YYYY-MM-DD` — only return files modified on or after this date |

**Returns**

A list of up to 50 matches, sorted by modification date (newest first):
```json
[
  {"path": "/mnt/c/Users/mubar/Downloads/Mubarak_CV_2026.pdf", "modified": "2026-07-15 09:32"},
  {"path": "/mnt/c/Users/mubar/Downloads/old/CV_draft.docx", "modified": "2025-11-02 18:10"}
]
```

**Behavior notes**
- Search is recursive (`os.walk`), so files in subfolders of `Downloads` are included.
- Matching is a plain substring check on the filename — no wildcards, regex, or file-extension filtering unless the keyword itself includes one.
- If `after_date` isn't valid `YYYY-MM-DD`, `datetime.strptime` will raise an exception (no error handling is currently in place — see [Known Issues](#known-issues--suggestions)).

## Agent Configuration

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `find_files_locally_agent` (final definition — see note below) |
| `description` | A helpful assistant to find files in the Downloads folder or on the computer |
| `tools` | `[search_tool]` (wraps `search_downloads`) |

## Known Issues / Suggestions

The script currently defines `search_tool` and `root_agent` **twice**:

1. First as `downloads_search_agent`, with an instruction telling the model *not* to use wildcards or extensions.
2. Then again as `find_files_locally_agent`, with an instruction telling the model to use "an appropriate glob pattern."

Since Python executes top to bottom, **only the second definition survives** — the first `root_agent` is silently overwritten. Two things worth fixing:

- **Remove the duplicate block** (the first `search_tool`/`root_agent` definition) if it's leftover from iteration, to avoid confusion about which agent is actually active.
- **Instruction/implementation mismatch**: the final instruction tells the model to use "an appropriate glob pattern," but `search_downloads` doesn't implement glob matching at all — it does a plain case-insensitive substring match. Either update the instruction to match the real behavior, or extend `search_downloads` to accept and apply a glob pattern (e.g. via the `glob` module, which is imported but currently unused).

## Example Interaction

**User:** "Find any invoice files from this year"

**Agent:**
1. Extracts keyword `"invoice"` and an appropriate `after_date`
2. Calls `search_downloads(keyword="invoice", after_date="2026-01-01")`
3. Lists matching files with their paths and last-modified timestamps

## Production Considerations

- Make `DOWNLOADS_DIR` configurable via an environment variable instead of hardcoding a user-specific path.
- Add error handling around `datetime.strptime` for malformed `after_date` input.
- Consider real glob/wildcard support if that's the intended behavior (the `glob` import currently goes unused).
- Add permission/error handling for unreadable directories or files during `os.walk`.
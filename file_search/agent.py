from datetime import datetime
import os
import glob
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

DOWNLOADS_DIR = "/mnt/c/Users/mubar/Downloads"

def search_downloads(keyword: str, after_date: str = "") -> list[dict]:
    """Search the Downloads folder (recursively) for files whose name
    contains the given keyword, case-insensitive. Results are sorted by
    modified date, most recent first.

    Args:
        keyword: text to search for in filenames, e.g. 'CV', 'invoice'.
        after_date: optional date filter in YYYY-MM-DD format. If given,
            only files modified on or after this date are returned.

    Returns:
        List of dicts with 'path' and 'modified' (YYYY-MM-DD HH:MM) keys,
        sorted newest first, up to 50 results.
    """
    keyword_lower = keyword.lower()
    cutoff = None
    if after_date:
        cutoff = datetime.strptime(after_date, "%Y-%m-%d")

    matches = []
    for root, _, files in os.walk(DOWNLOADS_DIR):
        for filename in files:
            if keyword_lower not in filename.lower():
                continue
            full_path = os.path.join(root, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            if cutoff and mtime < cutoff:
                continue
            matches.append({"path": full_path, "modified": mtime})

    matches.sort(key=lambda x: x["modified"], reverse=True)

    return [{"path": m["path"], "modified": m["modified"].strftime("%Y-%m-%d %H:%M")}
        for m in matches[:50]]

search_tool = FunctionTool(search_downloads)

root_agent = LlmAgent(
    name="downloads_search_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You help the user find files in their Downloads folder. "
        "When they mention a word or phrase (like 'CV' or 'invoice'), "
        "call search_downloads with that word as the keyword — "
        "don't add wildcards or file extensions yourself unless the user specifies one."
    ),
    tools=[search_tool],
)

search_tool = FunctionTool(search_downloads)

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='find_files_locally_agent',
    description='A helpful assistant to find files in the Downloads folder or in computer.',
    instruction="You help the user find files in their Downloads folder. Use search_downloads with an appropriate glob pattern based on their request.",
    tools=[search_tool],
)
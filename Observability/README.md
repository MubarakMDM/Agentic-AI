# Langfuse Tracing Setup for Google ADK

A small utility function that enables observability/tracing for a **Google Agent Development Kit (ADK)** application by wiring it up to **Langfuse**, using OpenInference instrumentation under the hood.

## Overview

`setup_tracing()` checks that the Langfuse client can authenticate, and if so, instruments the Google ADK so that agent and tool calls are automatically traced and sent to Langfuse for observability (inspecting prompts, tool calls, latencies, errors, etc.). If authentication fails, it logs a warning instead of crashing the application.

## How It Works

1. `get_client()` returns a configured Langfuse client (reads credentials/config from the environment — see [Setup](#setup) below).
2. `langfuse.auth_check()` verifies the client can actually authenticate with the Langfuse backend.
3. If authentication succeeds:
   - `GoogleADKInstrumentor().instrument()` patches the Google ADK so agent/tool executions are automatically captured as traces.
   - A confirmation message is printed.
4. If authentication fails:
   - A warning is printed.
   - The function returns normally without raising — tracing is simply disabled, and the rest of the application continues to run.

## Files

- `tracing.py` (or similar) — defines `setup_tracing()`.

## Dependencies

```bash
pip install langfuse openinference-instrumentation-google-adk
```

## Setup

Langfuse's `get_client()` typically reads credentials from environment variables. Set these before calling `setup_tracing()`:

```bash
export LANGFUSE_PUBLIC_KEY="your_public_key"
export LANGFUSE_SECRET_KEY="your_secret_key"
export LANGFUSE_HOST="https://cloud.langfuse.com"  # or your self-hosted URL
```

## Usage

Call `setup_tracing()` once at application startup, before running any ADK agents:

```python
from tracing import setup_tracing

setup_tracing()

# ... proceed to build/run your Google ADK agent as usual ...
```

Once instrumented, all Google ADK agent and tool invocations in the process are automatically traced and sent to Langfuse — no per-call changes needed elsewhere in the codebase.

## Behavior Notes

- **Non-fatal on failure**: if Langfuse credentials are missing or invalid, the app keeps running with tracing disabled rather than crashing — useful for local development or environments without observability configured.
- **Idempotency**: the function doesn't guard against being called multiple times; calling `GoogleADKInstrumentor().instrument()` more than once may raise or double-instrument depending on the instrumentor's implementation. Call it once, at startup.
- **Silent `pass`**: the `else` branch's `pass` after the print statement is redundant (the `print` call already satisfies the branch) but harmless.

## Production Considerations

- Replace the `print()` calls with proper logging (e.g. Python's `logging` module) so tracing status is captured in application logs rather than stdout.
- Consider raising a custom warning (`warnings.warn`) instead of a `pass`, so failures are more visible/monitorable in production.
- If instrumentation should be mandatory in production (not optional), consider making `setup_tracing()` raise instead of silently continuing when `auth_check()` fails.
- Guard against double-instrumentation if `setup_tracing()` could be called more than once (e.g. in tests or hot-reload scenarios).
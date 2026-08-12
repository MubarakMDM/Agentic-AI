# Currency Conversion Agent (Google ADK)

A simple conversational agent built with the **Google Agent Development Kit (ADK)** that answers general user questions and can convert amounts between currencies using **live exchange rates**.

## Overview

The agent is defined as `root_agent`, an instance of `google.adk.agents.llm_agent.Agent`, powered by the `gemini-2.5-flash` model. It behaves as a general-purpose assistant, but when a user asks to convert currency, it calls a custom tool function (`convert_currency`) that fetches real-time exchange rates from the [ExchangeRate-API](https://www.exchangerate-api.com/).

## How It Works

1. The user asks a question (e.g. *"Convert 50 Euros to Rupees"*).
2. The LLM recognizes the currency-conversion intent based on its `instruction` prompt.
3. It normalizes currency names to their 3-letter ISO codes (e.g. *Euros → EUR*, *Rupees → INR*, *Dollars → USD*).
4. It calls the `convert_currency` tool with `amount`, `from_currency`, and `to_currency`.
5. The tool queries the ExchangeRate-API and returns the converted amount, or an error message if something goes wrong.
6. The agent relays the result back to the user in natural language.

## Files

- `agent.py` (or similar) — defines `convert_currency` and `root_agent`.
- `__init__.py` — exposes the `agent` module so the package can be imported (`from . import agent`).

## Setup

### 1. Install dependencies

```bash
pip install google-adk requests
```

### 2. Get an API key

Sign up at [exchangerate-api.com](https://www.exchangerate-api.com/) to get a free API key.

### 3. Set the API key as an environment variable

```bash
export EXCHANGE_RATE_API_KEY="your_api_key_here"
```

> The agent reads this key via `os.getenv("EXCHANGE_RATE_API_KEY")`. If it's not set, currency conversion requests will return an error.

## Tool: `convert_currency`

```python
convert_currency(amount: float, from_currency: str, to_currency: str) -> dict
```

**Arguments**
| Name | Type | Description |
|---|---|---|
| `amount` | `float` | The amount of money to convert |
| `from_currency` | `str` | 3-letter source currency code (e.g. `EUR`) |
| `to_currency` | `str` | 3-letter target currency code (e.g. `INR`) |

**Returns**

On success:
```json
{
  "status": "success",
  "amount": 50,
  "from_currency": "EUR",
  "to_currency": "INR",
  "converted_amount": 5487.87,
  "rate": 109.7574
}
```

On failure:
```json
{
  "status": "error",
  "error_message": "API key not configured."
}
```

**Error cases handled**
- Missing API key
- Negative amount
- Failed/unsuccessful API response (bad currency code, etc.)
- Network/request failures (timeouts, connection errors)

## Agent Configuration

| Field | Value |
|---|---|
| `model` | `gemini-2.5-flash` |
| `name` | `root_agent` |
| `description` | A helpful assistant for user questions |
| `tools` | `[convert_currency]` |

The `instruction` field tells the model to answer general questions directly, but to route currency-conversion requests through the `convert_currency` tool, translating everyday currency names into ISO codes first.

## Notes on the Commented-Out Code

The top of the file contains earlier, simpler versions of the agent, kept for reference:

1. **Plain assistant** — no tools, just a basic Q&A agent.
2. **Fixed-rate EUR→INR converter** — a single hardcoded exchange rate (`convert_eur_to_inr`), useful for prototyping without needing an API key.

The final, active version generalizes this into a live, multi-currency converter (`convert_currency`) using a real exchange-rate API instead of a hardcoded rate.

## Example Interaction

**User:** "How much is 100 US dollars in Indian rupees?"

**Agent:**
1. Converts "US dollars" → `USD`, "Indian rupees" → `INR`
2. Calls `convert_currency(amount=100, from_currency="USD", to_currency="INR")`
3. Responds with the live converted amount and the exchange rate used

## Production Considerations

- Consider caching exchange rates briefly to avoid hitting API rate limits.
- Add retry logic for transient network failures.
- Validate currency codes against a known list before calling the API.
- Avoid logging the API key or including it in error messages.
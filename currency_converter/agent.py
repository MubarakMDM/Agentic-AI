# from google.adk.agents.llm_agent import Agent
# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='Answer user questions to the best of your knowledge',
# )


# from google.adk.agents.llm_agent import Agent

# def convert_eur_to_inr(amount: float) -> dict:
#     """Converts an amount in Euros (EUR) to Indian Rupees (INR).

#     Args:
#         amount: The amount in Euros to convert.

#     Returns:
#         A dictionary with the conversion result, e.g.
#         {"status": "success", "eur": 10, "inr": 1097.57, "rate": 109.7574}
#     """
#     # Note: This uses a fixed rate for simplicity.
#     # For a production agent, replace this with a live API call
#     # (e.g. exchangerate-api.com, frankfurter.app, etc.)
#     exchange_rate = 109.7574  # 1 EUR = 109.7574 INR (approx.)

#     if amount < 0:
#         return {"status": "error", "error_message": "Amount cannot be negative."}

#     inr_amount = round(amount * exchange_rate, 2)
#     return {
#         "status": "success",
#         "eur": amount,
#         "inr": inr_amount,
#         "rate": exchange_rate,
#     }


# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction=(
#         'Answer user questions to the best of your knowledge. '
#         'If the user asks to convert Euros to Rupees, use the '
#         'convert_eur_to_inr tool.'
#     ),
#     tools=[convert_eur_to_inr],
# )

import os
import requests
from google.adk.agents.llm_agent import Agent

# Set your API key as an environment variable (recommended)
# export EXCHANGE_RATE_API_KEY="your_api_key_here"
API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Converts an amount from one currency to another using live exchange rates.

    Args:
        amount: The amount of money to convert.
        from_currency: The 3-letter currency code to convert from (e.g. 'EUR').
        to_currency: The 3-letter currency code to convert to (e.g. 'INR').

    Returns:
        A dictionary with the conversion result or an error message.
    """
    if not API_KEY:
        return {"status": "error", "error_message": "API key not configured."}

    if amount < 0:
        return {"status": "error", "error_message": "Amount cannot be negative."}

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return {
                "status": "error",
                "error_message": data.get("error-type", "Unknown API error"),
            }

        return {
            "status": "success",
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": data["conversion_result"],
            "rate": data["conversion_rate"],
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "error_message": f"API request failed: {str(e)}"}


root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=(
        'Answer user questions to the best of your knowledge. '
        'If the user asks to convert currency, use the convert_currency tool. '
        'Convert currency names/symbols to their 3-letter ISO codes '
        '(e.g. Euros -> EUR, Rupees -> INR, Dollars -> USD) before calling the tool.'
    ),
    tools=[convert_currency],
)
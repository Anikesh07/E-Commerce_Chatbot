"""Custom actions for the E-Commerce Chatbot.

This module contains example actions, including a simple Hello World action
and an example action that calls an LLM via the OpenAI Python client.

Note: to use the LLM action, install the `openai` package and set the
OPENAI_API_KEY environment variable on the machine running the action server.
"""

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os

# Try to import the OpenAI client; keep a graceful fallback for environments
# where it's not installed.
try:
	import openai
except Exception:
	openai = None


class ActionHelloWorld(Action):
	"""Simple example action that replies 'Hello World!'."""

	def name(self) -> Text:
		return "action_hello_world"

	async def run(self, dispatcher: CollectingDispatcher,
				  tracker: Tracker,
				  domain: Any) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="Hello World!")
		return []


class ActionCallLLM(Action):
	"""Call an external LLM (example uses OpenAI Python client).

	This action uses a short prompt built from the user's last message and an
	optional `product` slot to ask the model for a short, helpful reply.
	"""

	def name(self) -> Text:
		return "action_call_llm"

	async def run(self, dispatcher: CollectingDispatcher,
				  tracker: Tracker,
				  domain: Any) -> List[Dict[Text, Any]]:

		user_message = tracker.latest_message.get("text", "")
		product = tracker.get_slot("product") or ""

		prompt = (
			f"You are a helpful e-commerce assistant. The user asked: {user_message}\n"
			f"Product: {product}\n"
			"Provide a short, friendly recommendation or next step the bot should say."
		)

		if openai is None:
			dispatcher.utter_message(text=(
				"LLM client library is not installed. Install the `openai` package "
				"or configure another LLM client on the action server."))
			return []

		api_key = os.getenv("OPENAI_API_KEY")
		if not api_key:
			dispatcher.utter_message(text=(
				"LLM is not configured. Please set the OPENAI_API_KEY environment variable "
				"on the action server."))
			return []

		openai.api_key = api_key

		try:
			resp = openai.ChatCompletion.create( # type: ignore
				model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
				messages=[
					{"role": "system", "content": "You are a helpful assistant."},
					{"role": "user", "content": prompt},
				],
				max_tokens=200,
				temperature=0.7,
			)

			text = resp["choices"][0]["message"]["content"].strip()
		except Exception:
			dispatcher.utter_message(text=(
				"Sorry — I'm having trouble reaching the LLM service right now."))
			return []

		dispatcher.utter_message(text=text)
		return []



# action file to comapre

# --- IGNORE ---
from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests  # For HTTP API calls

class ActionComparePrices(Action):
    def name(self) -> Text:
        return "action_compare_prices"

    def fetch_flipkart_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        fp_api_key = "YOUR_FLIPKART_API_KEY"
        url = f"https://api.flipkart.net/search?q={product}"
        headers = {"Authorization": f"Bearer {fp_api_key}"}
        response = requests.get(url, headers=headers)
        # Parse response accordingly
        data = response.json()
        # Extract price & link from response structure
        # This is a placeholder: replace with actual parsing logic
        if "products" in data and len(data["products"]) > 0:
            p = data["products"][0]
            return {"site": "Flipkart", "price": p.get("price", None), "url": p.get("productUrl", None)}
        return None

    def fetch_amazon_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        am_api_key = "YOUR_AMAZON_API_KEY"
        url = f"https://api.amazon.com/pricing?q={product}"  # Example URL, replace with actual API
        headers = {"Authorization": f"Bearer {am_api_key}"}
        response = requests.get(url, headers=headers)
        data = response.json()
        # Extract price & link from response structure
        if "products" in data and len(data["products"]) > 0:
            p = data["products"][0]
            return {"site": "Amazon", "price": p.get("price", None), "url": p.get("url", None)}
        return None

    def fetch_myntra_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        # Myntra API or third-party scraping service
        # Replace with your actual API call
        return {"site": "Myntra", "price": 2000, "url": "https://www.myntra.com/product-link"}

    def fetch_meesho_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        # Meesho API or scraping API call
        return {"site": "Meesho", "price": 1800, "url": "https://www.meesho.com/product-link"}

    async def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Any) -> List[Dict[Text, Any]]:

        product = tracker.get_slot("product")
        if not product:
            dispatcher.utter_message(text="Please tell me the product name you'd like to check.")
            return []

        results = []
        # Call each API and collect price data
        flipkart_result = self.fetch_flipkart_price(product)
        if flipkart_result:
            results.append(flipkart_result)
        amazon_result = self.fetch_amazon_price(product)
        if amazon_result:
            results.append(amazon_result)
        myntra_result = self.fetch_myntra_price(product)
        if myntra_result:
            results.append(myntra_result)
        meesho_result = self.fetch_meesho_price(product)
        if meesho_result:
            results.append(meesho_result)

        if not results:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any prices for '{product}'.")
            return []

        # Find the best price
        valid_prices = [r for r in results if r["price"] is not None]
        if not valid_prices:
            dispatcher.utter_message(text=f"Price information not available for '{product}'.")
            return []

        best = min(valid_prices, key=lambda x: x["price"])
        message_lines = [f"Price comparison for '{product}':"]
        for res in valid_prices:
            price = res["price"]
            site = res["site"]
            url = res["url"] or "No link available"
            message_lines.append(f"- {site}: ₹{price} (Link: {url})")

        message_lines.append(f"\nBest deal is on {best['site']} at ₹{best['price']}.")
        dispatcher.utter_message(text="\n".join(message_lines))

        return []

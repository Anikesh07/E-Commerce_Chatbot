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
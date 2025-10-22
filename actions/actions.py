"""Custom actions for the E-Commerce Chatbot.

This module contains example actions, including a simple Hello World action
and an example action that calls an LLM via the OpenAI Python client.

Note: to use the LLM action, install the `openai` package and set the
OPENAI_API_KEY environment variable on the machine running the action server.
"""

from typing import Any, Text, Dict, List, Optional
import os

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import the OpenAI client; keep a graceful fallback for environments
# where it's not installed.
openai_available = False
OpenAIClient = None  # Changed from OpenAI to OpenAIClient to avoid confusion


try:
    from openai import OpenAI as OpenAIClient
    openai_available = True
except Exception:
    openai_available = False

# Try to import requests for API calls
try:
    import requests
except ImportError:
    requests = None


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

        if not openai_available or OpenAIClient is None:
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

        try:
            # Updated to use the new OpenAI API client (v1.0.0+)
            # Instantiate the client with the API key read earlier
            client = OpenAIClient(api_key=api_key)
            
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful e-commerce assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )

            # Safely extract text from the response to avoid calling strip on None
            raw_content = None
            if hasattr(response, "choices") and len(response.choices) > 0:
                choice0 = response.choices[0]
                # Common shape: choice0.message.content
                if hasattr(choice0, "message") and hasattr(choice0.message, "content"):
                    raw_content = choice0.message.content
                # Fallback: older shape may have choice0.text
                elif hasattr(choice0, "text"):
                    raw_content = choice0.text # type: ignore
                # If choices are dict-like
                elif isinstance(choice0, dict):
                    raw_content = choice0.get("message", {}).get("content") or choice0.get("text")

            text = raw_content.strip() if isinstance(raw_content, str) else ""
            dispatcher.utter_message(text=text or "Sorry, I couldn't generate a reply at the moment.")
            
        except Exception as e:
            dispatcher.utter_message(text=(
                "Sorry — I'm having trouble reaching the LLM service right now."))
            print(f"Error calling OpenAI API: {e}")
            
        return []


class ActionComparePrices(Action):
    """Compare prices across multiple e-commerce platforms.
    
    This action fetches prices from different platforms and returns
    the best deal to the user.
    """
    
    def name(self) -> Text:
        return "action_compare_prices"

    def fetch_flipkart_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        """Fetch product price from Flipkart API."""
        fp_api_key = os.getenv("FLIPKART_API_KEY")
        
        if not fp_api_key or not requests:
            return None
            
        try:
            url = f"https://api.flipkart.net/search?q={product}"
            headers = {"Authorization": f"Bearer {fp_api_key}"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract price & link from response structure
            if "products" in data and len(data["products"]) > 0:
                p = data["products"][0]
                return {
                    "site": "Flipkart",
                    "price": p.get("price"),
                    "url": p.get("productUrl")
                }
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Flipkart price: {e}")
            
        return None

    def fetch_amazon_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        """Fetch product price from Amazon API."""
        am_api_key = os.getenv("AMAZON_API_KEY")
        
        if not am_api_key or not requests:
            return None
            
        try:
            # Note: Replace with actual Amazon Product Advertising API endpoint
            url = f"https://api.amazon.com/pricing?q={product}"
            headers = {"Authorization": f"Bearer {am_api_key}"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract price & link from response structure
            if "products" in data and len(data["products"]) > 0:
                p = data["products"][0]
                return {
                    "site": "Amazon",
                    "price": p.get("price"),
                    "url": p.get("url")
                }
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Amazon price: {e}")
            
        return None

    def fetch_myntra_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        """Fetch product price from Myntra API or web scraping service."""
        myntra_api_key = os.getenv("MYNTRA_API_KEY")
        
        if not myntra_api_key or not requests:
            # Return mock data for testing - REMOVE IN PRODUCTION
            return {
                "site": "Myntra",
                "price": 2000,
                "url": "https://www.myntra.com/product-link"
            }
            
        try:
            # Replace with actual Myntra API endpoint when available
            url = f"https://api.myntra.com/search?q={product}"
            headers = {"Authorization": f"Bearer {myntra_api_key}"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if "products" in data and len(data["products"]) > 0:
                p = data["products"][0]
                return {
                    "site": "Myntra",
                    "price": p.get("price"),
                    "url": p.get("url")
                }
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Myntra price: {e}")
            
        return None

    def fetch_meesho_price(self, product: Text) -> Optional[Dict[Text, Any]]:
        """Fetch product price from Meesho API or web scraping service."""
        meesho_api_key = os.getenv("MEESHO_API_KEY")
        
        if not meesho_api_key or not requests:
            # Return mock data for testing - REMOVE IN PRODUCTION
            return {
                "site": "Meesho",
                "price": 1800,
                "url": "https://www.meesho.com/product-link"
            }
            
        try:
            # Replace with actual Meesho API endpoint when available
            url = f"https://api.meesho.com/search?q={product}"
            headers = {"Authorization": f"Bearer {meesho_api_key}"}
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if "products" in data and len(data["products"]) > 0:
                p = data["products"][0]
                return {
                    "site": "Meesho",
                    "price": p.get("price"),
                    "url": p.get("url")
                }
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Error fetching Meesho price: {e}")
            
        return None

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Any) -> List[Dict[Text, Any]]:

        product = tracker.get_slot("product")
        
        if not product:
            dispatcher.utter_message(text="Please tell me the product name you'd like to check.")
            return []

        if not requests:
            dispatcher.utter_message(
                text="Price comparison is not available. Please install the 'requests' library."
            )
            return []

        # Collect price data from all platforms
        results = []
        
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
            dispatcher.utter_message(
                text=f"Sorry, I couldn't find any prices for '{product}'. Please try a different product."
            )
            return []

        # Filter results with valid prices
        valid_prices = [r for r in results if r.get("price") is not None]
        
        if not valid_prices:
            dispatcher.utter_message(
                text=f"Price information is not available for '{product}' at the moment."
            )
            return []

        # Find the best price
        best = min(valid_prices, key=lambda x: x["price"])
        
        # Build response message
        message_lines = [f"Price comparison for '{product}':\n"]
        
        for res in valid_prices:
            price = res["price"]
            site = res["site"]
            url = res.get("url") or "No link available"
            message_lines.append(f"• {site}: ₹{price}")
            if url != "No link available":
                message_lines.append(f"  Link: {url}")

        message_lines.append(f"\n✨ Best deal: {best['site']} at ₹{best['price']}")
        
        dispatcher.utter_message(text="\n".join(message_lines))

        return []

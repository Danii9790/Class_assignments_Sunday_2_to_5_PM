from sys import exception
from agents import Agent,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,function_tool
from agents.run import RunConfig
from dotenv import load_dotenv
import os
import requests

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("API is not set.")

external_client = AsyncOpenAI(
    api_key= gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client= external_client
)

config = RunConfig(
    model = model,
    model_provider= external_client,
    tracing_disabled= True
)

@function_tool()
def search_products(product_name: str) -> str:
    try:
        fetch_data = requests.get("https://template6-six.vercel.app/api/products")
        fetch_data.raise_for_status()
        response = fetch_data.json()

        filtered_products = [
            product for product in response
            if product_name.lower() in product.get("title", "").lower()
        ]

        if not filtered_products:
            return f"No products found matching '{product_name}'."

        result = ""
        for p in filtered_products:
            result += f"\n🪑 {p['title']}\n💸 Price: Rs.{p['price']}\n🔖 Discount: {p['dicountPercentage']}%\n"

        return result.strip()

    except Exception as e:
        return f"Error fetching product: {e}"

agent = Agent(
    name="Shopping Agent",
    instructions="You are a helpful agent your work is to fetch product data from search_products funcion_tool and then respond user with friendly Message.",
    tools=[search_products],
    model = model
)

result = Runner.run_sync(agent,"i wannt to buy Timeless Elegance?",run_config=config)

print(result.final_output)

    
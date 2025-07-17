from agents import Agent,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,RunConfig, function_tool
from dotenv import load_dotenv
import os
import requests


load_dotenv()
gemini_api_key=os.getenv("GEMINI_API_KEY")

# Check if the api key is present , If not raise an error
if not gemini_api_key:
    raise ValueError("Gemini Api key is not set.")


external_client=AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", 
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled = True
)

@function_tool
def get_binance_price(symbol="BTCUSDT"):
    """
    Binance se current crypto price fetch karta hai.
    
    Parameters:
    - symbol: e.g., BTCUSDT, ETHUSDT

    Returns:
    - float: current price
    """
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print("Error fetching price:", e)
        return None


agent = Agent(
    model=model,
    name="Assistant",
    instructions="you are a helpful assistant" ,
    tools=[get_binance_price]
)

result = Runner.run_sync(agent,"ETHUSDT ka latest price batayein .",run_config=config)

print(result.final_output)

# Output :

'ETHUSDT ka current price 3435.03 hai.'

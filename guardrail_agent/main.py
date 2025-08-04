import asyncio
from agents import (Agent,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,input_guardrail,GuardrailFunctionOutput,InputGuardrailTripwireTriggered,OutputGuardrailTripwireTriggered,output_guardrail)
from agents.run import RunConfig
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import rich

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("Api key is not set")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model = model,
    model_provider= external_client
)

class Passenger_Output(BaseModel):
    response : str
    is_Weight_Exceed : bool

airport_agent = Agent (
    name= "Airport Security Guard",
    instructions="""
    Your task is to check the passenger luggage.
    If Passenger luggage is more tha 25kgs , Gracefully stop them to travel.
    """,
    output_type = Passenger_Output
)

@input_guardrail
async def security_guardrail(context,agent,input):
    result = await Runner.run(airport_agent,input,run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info = result.final_output.response,
        tripwire_triggered=result.final_output.is_Weight_Exceed
    )

# Main agent
passenger_agent = Agent(
    name = "Passenger Agent",
    instructions="""
    You are a Passenger agent.
    """,
    input_guardrails=[security_guardrail]
)

async def main():
    try:
        passenger_input = input("Enter you Luggage weight :")
        result = await Runner.run(passenger_agent,passenger_input,run_config=config)
        print("Passenger is onboarded")
    except InputGuardrailTripwireTriggered:
        print("Passenger can't check in !")

if __name__=="__main__":
    asyncio.run(main())






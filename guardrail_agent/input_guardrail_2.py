import asyncio
from agents import (Agent, GuardrailFunctionOutput,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,InputGuardrailTripwireTriggered,input_guardrail)
from dotenv import load_dotenv
import rich
from connection import config
from pydantic import BaseModel

load_dotenv()
class Output_formate(BaseModel):
    response : str
    is_stop : bool

father_agent = Agent(
    name = "Father agent",
    instructions='''
    You are a Father agent.
    Your task to stop Children's to changing AC tempeerature below 26C.
    ''',
    output_type=Output_formate
)

@input_guardrail
async def father_guradrail(context , agent , input):
    result = await Runner.run(father_agent,input,run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_stop
    )

# Main Agent
agent = Agent(
    name = "Children agent",
    instructions='''
    You are a children agent
    ''',
    input_guardrails=[father_guradrail]
)

async def main():
    try:
        children_input=input("Enter you quries : ")
        result = await Runner.run(agent,children_input,run_config=config)
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("You are not Allowed to Run Ac below 26c.")

if __name__ =="__main__":
    asyncio.run(main())
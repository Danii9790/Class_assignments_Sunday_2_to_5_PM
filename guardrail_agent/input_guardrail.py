import asyncio
from agents import Agent, GuardrailFunctionOutput,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,InputGuardrailTripwireTriggered,input_guardrail
from dotenv import load_dotenv
import rich
from connection import config
from pydantic import BaseModel

load_dotenv()

class Output_type(BaseModel):
    response : str
    is_Allowed : bool

timing_agent = Agent(
    name="Timing Change Agent",
    instructions="""
    You are a Timing Change Issue Check Agent.
    If some one says related to change the Timing of the class, Gracefully stop them .
    """,
    output_type=Output_type
)

@input_guardrail
async def timing_guardrails(context,agent,input):
    result = await Runner.run(timing_agent,input,run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_Allowed
    )

# Main Agent

student_agent = Agent(
    name = "Student Agent",
    instructions="""
    You are a Student Agent.
    If some says releted to Python and Other programming Language then Gracefully Reponse them.
    """,
    input_guardrails=[timing_guardrails]
)

async def main():
    try:
        student_input=input("Enter your Quries :")
        result = await Runner.run(student_agent,student_input,run_config=config)
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("You Don't allow this.")

if __name__ =="__main__":
    asyncio.run(main())

import asyncio
from agents import Agent, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered,Runner,AsyncOpenAI,OpenAIChatCompletionsModel,InputGuardrailTripwireTriggered,input_guardrail, output_guardrail
from dotenv import load_dotenv
import rich
from connection import config
from pydantic import BaseModel
######################## Output Guardrails ########################
load_dotenv()

class MessageOutput(BaseModel): # Model for Agent Output Type
    response: str

class PHDOutput(BaseModel): # Model to trigger the guardrail
    isPHDLevelResponse: bool

phd_guardrail_agent = Agent(
    name = "PHD Guardrail Agent",
    instructions="""
        You are a PHD Guardrail Agent that evaluates if text is too complex for 8th grade students. If the response if 
        very hard to read for an eight grade student deny the agent response
    """,
    output_type=PHDOutput
)

@output_guardrail
async def PHD_guardrail(ctx, agent: Agent, output) -> GuardrailFunctionOutput:

    result = await Runner.run(phd_guardrail_agent, output.response,  run_config=config)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered= result.final_output.isPHDLevelResponse
    )

# Main executor agent
eigth_grade_std = Agent(
    name = "Eight grade student",
    instructions="""
        1. You are an agent that answer query to a eight standard student. Keep your vocabulary simple and easy. 
        2. If asked to give answers in most difficult level use the most hardest english terms
    """,
    output_type=MessageOutput,
    output_guardrails=[PHD_guardrail]
)

async def og_main():
    query = "What are trees?"
    try:
        result = await Runner.run(eigth_grade_std, query, run_config=config)
        print(result.final_output)

    except OutputGuardrailTripwireTriggered:
        print('Agent output is not according to the expectations')
        

if __name__ == "__main__":
    asyncio.run(og_main())
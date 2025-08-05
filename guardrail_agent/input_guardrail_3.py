import asyncio
from agents import (Agent, GuardrailFunctionOutput,Runner,input_guardrail,InputGuardrailTripwireTriggered)
import rich
from dotenv import load_dotenv
from connection import config
from pydantic import BaseModel
load_dotenv()

class Output_formate(BaseModel):
    response : str
    is_stop : bool

gate_keeper_agent = Agent(
    name="Gate Keeper Guard",
    instructions="""
    You are a Gate_Keeper Agent.
    Your Work is to stop Student of other School.
    Only Allow those Student who is Wear the Ranger school dress.
    The school dress is White shirt and black pent. 
    """,
    output_type=Output_formate
)

@input_guardrail
async def gate_keeper_guardrail(context,agent,input):
    result = await Runner.run(gate_keeper_agent,input,run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_stop
    )

# Main Agent
student_agent = Agent(
    name="Student Agent",
    instructions="""
    You are a Student Agent.
    """,
    input_guardrails=[gate_keeper_guardrail]
)

async def main():
    try:
        student_input = input("Enter Your Message Here : ")
        result = await Runner.run(student_agent,student_input,run_config=config)
        print(result.final_output)
    except InputGuardrailTripwireTriggered:
        print("You are Not allowed because you are not a Student of Our School.")

if __name__ =="__main__":
    asyncio.run(main())

# Enter Your Message Here : i want to attend my class      
# Output_formate(
#     response='Halt! State your business. Only Ranger School students in uniform are permitted. Are you wearing a white shirt and black 
# pants?',
#     is_stop=True
# )
# You are Not allowed because you are not a Student of Our School.

# Another Response:
 
# Enter Your Message Here : i want to attend the class i am wear white shirt and black pent
# Output_formate(response='You are wearing the correct uniform. Please proceed to class.', is_stop=False)
# Okay! Just to make sure I understand, you're planning to attend class today wearing a white shirt and black pants. Have a great class! Is there anything else I can help you with?
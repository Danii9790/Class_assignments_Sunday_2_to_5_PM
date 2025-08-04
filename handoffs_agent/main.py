import asyncio
import trace
from agents.models import openai_chatcompletions
from dotenv import load_dotenv
from agents import Agent, Runner ,AsyncOpenAI,OpenAIChatCompletionsModel,function_tool
from agents.run import RunConfig
import os


load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("API_KEY is not set")


external_client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash-exp",
    openai_client= external_client
)

config = RunConfig(
    model = model,
    model_provider=external_client,
)


load_dotenv()
@function_tool
def analyze_lyric_poetry(poem: str) -> str:
    """Analyze a poem and return how emotional and personal it is (Lyric poetry style)."""
    keywords = ["I", "me", "heart", "feel", "love", "sad", "joy"]
    score = sum(1 for word in keywords if word.lower() in poem.lower())
    return f"Lyric score: {score}/10"

@function_tool
def analyze_narrative_poetry(poem: str) -> str:
    """Analyze a poem and return how much it tells a story (Narrative poetry style)."""
    keywords = ["he", "she", "they", "then", "after", "before", "when", "once"]
    score = sum(1 for word in keywords if word.lower() in poem.lower())
    return f"Narrative score: {score}/10"

@function_tool
def analyze_dramatic_poetry(poem: str) -> str:
    """Analyze a poem and return how much it feels like a performance (Dramatic poetry style)."""
    keywords = ["!", "O ", "speak", "behold", "listen"]
    score = sum(1 for word in keywords if word.lower() in poem.lower())
    return f"Dramatic score: {score}/10"




lyric_analyst_agent = Agent(
    name="Lyric Analyst Agent",
    instructions="You analyze poems to check if they are lyric poetry by detecting personal feelings and emotions.",
    tools=[analyze_lyric_poetry],
)

narrative_analyst_agent = Agent(
    name="Narrative Analyst Agent",
    instructions="You analyze poems to check if they are narrative poetry by detecting storytelling, characters, and events.",
    tools=[analyze_narrative_poetry],
)

dramatic_analyst_agent = Agent(
    name="Dramatic Analyst Agent",
    instructions="You analyze poems to check if they are dramatic poetry by detecting theatrical speech and performance style.",
    tools=[analyze_dramatic_poetry],
)


parent_agent = Agent(
    name="Parent Agent",
    instructions="""
        You are a parent agent who receives a poem and delegates it to all three analyst agents:
        - Lyric Analyst
        - Narrative Analyst
        - Dramatic Analyst

        You must call their tools yourself and compare their scores.
        Based on highest score, decide the type of poetry and respond to the user with the final result.
    """,
    handoffs=[
        lyric_analyst_agent,
        narrative_analyst_agent,
        dramatic_analyst_agent,
    ],
)
async def main():
    poem_input = """
I walk alone beneath the moon,
Its silver glow a gentle tune.
My heart beats slow with silent cries,
A song of love that never dies.
"""
    result = await Runner.run(
            parent_agent, 
            poem_input, 
            run_config=config)
    print(result.final_output)
    print("Last Agent ==> ", result.last_agent.name)


if __name__ == "__main__":
    asyncio.run(main())





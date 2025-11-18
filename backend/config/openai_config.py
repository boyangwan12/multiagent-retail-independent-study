from decouple import config
from agents import AsyncOpenAI, OpenAIChatCompletionsModel

key = config("OPENAI_API_KEY")

openai_client = AsyncOpenAI(api_key=key)

MODEL = OpenAIChatCompletionsModel(
    model="gpt-4o-mini",
    openai_client=openai_client
)

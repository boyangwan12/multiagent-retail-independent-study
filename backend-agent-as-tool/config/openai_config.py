from decouple import config
from agents import AsyncOpenAI, OpenAIChatCompletionsModel

key = config("OPENAI_API_KEY")

openai_client = AsyncOpenAI(api_key=key)

MODEL = OpenAIChatCompletionsModel(
    model="gpt-4o-mini",
    openai_client=openai_client
)
# nano? model
# enable reasoning
# OpenAIChatCompletionsModel -> response api -> agent sdk
# content 7 fetches newest changes
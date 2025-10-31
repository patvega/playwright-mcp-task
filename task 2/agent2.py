import asyncio
import os
from typing import List

from pydantic_ai import Agent, ToolReturnPart
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.messages import (ModelMessage, ModelRequest, ModelResponse,
                                  SystemPromptPart, TextPart)
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from dotenv import load_dotenv


load_dotenv()
gemini_api_key = os.getenv('GOOGLE_API_KEY')

# This is how we create the system prompt for the agent to use. Since we can manipulate the messages that are passed back to the LLM,
# we are initalizing the 'memory' with this dialogue history so it continues immediately with the task.

def build_history() -> List[ModelMessage]:
    return [
        ModelRequest(
            parts=[
                SystemPromptPart(
                    content="""You are an expert web automation assistant. Based on a user-provided goal and the current page state at certain intervals, your only goal is to execute the actions to achieve the goal. Use the tools provided to you to achieve the goal."""
                ),
            ]
        ),
        ModelResponse(
            parts=[
                TextPart(
                    content="I understand. I will use the tools provided to me to achieve the goal. How can I help you?"
                ),
            ]
        ),
    ]


# The agent usually returns in the dialogue the tool call made as well as what might've been seen on the page afterwards.
# The page summary is trivial in most cases after we have taken another step and just makes the message history much longer and require many more tokens to continue,
# so we can just edit the message to say this instead and just have it reread the page if the message we truncated was important
def filter_responses(messages: list[ModelMessage]) -> list[ModelMessage]:
    tool_returns = [
        part
        for message in messages
        for part in message.parts
        if isinstance(part, ToolReturnPart)
    ]

    if len(tool_returns) > 1:
        for tool in tool_returns[:-1]:
            if len(tool.content):
                tool.content = (
                    "Response truncated to save memory. Read page again if needed."
                )

    return messages


# Intializing the agent with the latest flash model and providing it the MCP server
async def main():
    provider = GoogleProvider(api_key=gemini_api_key)
    model = GoogleModel("gemini-flash-latest", provider=provider)
    settings = GoogleModelSettings()

    server = MCPServerStreamableHTTP("http://localhost:8000/mcp")

    request = "find me a roundtrip flight to detroit under $500 for next week on google flights"

    agent = Agent(
        model=model,
        model_settings=settings,
        toolsets=[server],
        history_processors=[filter_responses],
    )

    result = await agent.run(request, message_history=build_history())
    print(result.new_messages())


if __name__ == "__main__":
    asyncio.run(main())
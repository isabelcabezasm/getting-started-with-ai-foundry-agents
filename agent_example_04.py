"""
Semantic Kernel Azure AI Foundry Agent Example

In this example, we demonstrate how to create a Semantic Kernel agent that interacts with the Azure AI Foundry Agent service.

We are creating an Azure AI agent that answers questions about a sample menu using a Semantic Kernel Plugin.

This example requires the `azure-identity` and `semantic-kernel` packages.

You need the environment variables set in your .env file for this example to work:
* AZURE_AI_AGENT_ENDPOINT
* AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME

"""

# # Develop with Semantic Kernel and Azure AI Foundry Agent
# https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/semantic-kernel

# https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started_with_agents/azure_ai_agent/step1_azure_ai_agent.py

import asyncio
from typing import Annotated
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread
from semantic_kernel.functions import kernel_function



# Define a sample plugin for the sample

class WeatherPlugin:
    """A sample Weather Plugin for providing weather information."""

    @kernel_function(description="Provides the current weather for a given city.")
    def get_current_weather(
        self, city: Annotated[str, "The name of the city."]
    ) -> Annotated[str, "Returns the current weather in the specified city."]:
        # This is a stubbed response for demonstration.
        return f"The current weather in {city} is sunny, 25°C."

    @kernel_function(description="Provides a weather forecast for a given city.")
    def get_weather_forecast(
        self, city: Annotated[str, "The name of the city."]
    ) -> Annotated[str, "Returns the weather forecast for the specified city."]:
        # This is a stubbed response for demonstration.
        return f"The weather forecast for {city} is mostly sunny for the next 3 days."



# Simulate a conversation with the agent

USER_INPUTS = [
    "Hello",
    "What is the current weather in Paris?",
    "Can you give me the weather forecast for Tokyo?",
    "Thank you",
]

async def main() -> None:

    ai_agent_settings = AzureAIAgentSettings()

    agent_client = AzureAIAgent.create_client(credential=DefaultAzureCredential(), 
                                            endpoint=ai_agent_settings.endpoint)

    # 1. Create an agent on the Azure AI agent service
    agent_definition = await agent_client.agents.create_agent(
                            model=AzureAIAgentSettings().model_deployment_name,
                            name="WeatherAgent",
                            instructions="Answer the user's questions about the weather.",
                    )
            
    # 2. Create a Semantic Kernel agent for the Azure AI agent
    agent = AzureAIAgent(
                client=agent_client,
                definition=agent_definition,
                plugins=[WeatherPlugin()],
            )

    # # Let's speak with the weather agent:

    # 3. Create a thread
    thread: AzureAIAgentThread = None


    for user_input in USER_INPUTS:
        print(f"# User: {user_input}")
        
        # 4. Invoke the agent with the specified message for response
        response = await agent.get_response(messages=user_input, thread=thread)
        print(f"# {response.name}: {response}")
        thread = response.thread

    # 6. Cleanup: Delete the thread and agent
    await thread.delete() if thread else None
    await agent_client.agents.delete_agent(agent.id)


if __name__ == "__main__":
    asyncio.run(main())


"""
Semantic Kernel Azure AI Foundry Agent Example

In this example, we demonstrate how to create a Semantic Kernel agent that interacts with the Azure AI Foundry Agent service.
This agent can be used to answer user questions and maintain a conversation thread.
The historical context of the conversation is preserved, allowing the agent to respond appropriately based on previous interactions.

This example requires the `azure-identity` and `semantic-kernel` packages.

You need the environment variables set in your .env file for this example to work:
* AZURE_AI_AGENT_ENDPOINT
* AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME

"""

# # Develop with Semantic Kernel and Azure AI Foundry Agent
# https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/semantic-kernel

# https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started_with_agents/azure_ai_agent/step1_azure_ai_agent.py

import asyncio
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread


# Simulate a conversation with the agent

USER_INPUTS = [
    "Hello, I am John Doe.",
    "What is your name?",
    "What is my name?",
]


async def main() -> None:

    ai_agent_settings = AzureAIAgentSettings()

    agent_client = AzureAIAgent.create_client(credential=DefaultAzureCredential(),
                                              endpoint=ai_agent_settings.endpoint)

    # 1. Create an agent on the Azure AI agent service
    agent_definition = await agent_client.agents.create_agent(
        model=AzureAIAgentSettings().model_deployment_name,
        name="Semantic_Kernel_Assistant",
        instructions="Answer the user's questions.",
    )

    # 2. Create a Semantic Kernel agent for the Azure AI agent
    agent = AzureAIAgent(
        client=agent_client,
        definition=agent_definition,
    )

    # # Let's speak with the agent:

    # 3. Create a thread for the agent
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

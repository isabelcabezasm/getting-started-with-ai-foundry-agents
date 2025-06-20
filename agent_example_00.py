"""
This is the simplest example of using the Azure AI Agent service to create an agent, send a message, and receive a response.
It demonstrates how to create an agent, send a message, and process the response using the Azure AI Agent service.
It also shows how to clean up by deleting the agent and thread after use.

You need the environment variables set in your .env file for this example to work:
AZURE_AI_AGENT_ENDPOINT
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME

"""

# # Azure AI Agent service SDK reference:
# https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python

import os
from dotenv import load_dotenv

from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

# Load environment variables from .env
load_dotenv()

endpoint = os.environ["AZURE_AI_AGENT_ENDPOINT"]
model_deployment_name = os.environ["AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"]

agent_client = AgentsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# Create an agent
agent = agent_client.create_agent(
    model=model_deployment_name,
    name="Simplest Assistant ever",
    instructions="Answer the user's questions.",
)

print(f"Agent created with ID: {agent.id}")


# The Agent appears in the Azure AI Foundry portal under Agents.

# Let's speak with the agent.

# Create a thread
thread = agent_client.threads.create()
print(f"Created thread, thread ID: {thread.id}")

# Create a message
message = agent_client.messages.create(
    thread_id=thread.id,
    role="user",
    content="What can you do for me?",
)
print(f"Created message, message ID: {message.id}")

# run/send the message to the agent
run = agent_client.runs.create_and_process(
    thread_id=thread.id, agent_id=agent.id)
print(f"Run finished with status: {run.status}")

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    # Get the response from the agent

    # get all the messages in the thread
    response = agent_client.messages.list(thread_id=thread.id, run_id=run.id)
    for msg in response:
        if msg.role == "assistant":
            print(f"Agent response: {msg.content}")


# Cleanup: Delete the agent and the thread.

agent_client.threads.delete(thread.id)
print(f"Deleted thread with ID: {thread.id}")

agent_client.delete_agent(agent.id)
print(f"Deleted agent with ID: {agent.id}")

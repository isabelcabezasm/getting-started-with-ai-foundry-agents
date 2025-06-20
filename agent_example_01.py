"""
Example of using the Azure AI Agent service to create an agent, and add a knowledge tool (Bing Custom Search) to it.
Send a message, and receive a response.
Finally, clean up by deleting the agent and thread after use.

You will need to create a "Grounding with Bing Custom Search" in your Azure Subscription, 
and create a connection to it in the Azure AI Foundry portal.
Add the connection name to your .env file as `AZURE_BING_CONNECTION_NAME`.
Add the Bing Search configuration name to your .env file as `AZURE_BING_SEARCH_CONFIG_NAME`.

Also, you need the environment variables set in your .env file for this example to work:
AZURE_AI_AGENT_ENDPOINT
AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME

"""

# # Azure AI Agent service SDK reference:
# https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python

# # Create Agent with Bing Grounding doc example:
# https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python#create-agent-with-bing-grounding


import os
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import BingCustomSearchTool
from azure.identity import DefaultAzureCredential

# Load environment variables from .env
load_dotenv()

endpoint = os.environ["AZURE_AI_AGENT_ENDPOINT"]
model_deployment_name = os.environ["AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"]
bing_connection_name = os.environ["AZURE_BING_CONNECTION_NAME"]
bing_config_name = os.environ["AZURE_BING_SEARCH_CONFIG_NAME"]

agent_client = AgentsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# Initialize project client
# Here I need the project client to access the connections and retrieve the Bing connection.
project_client = AIProjectClient(endpoint=endpoint,
                                 credential=DefaultAzureCredential()
                                 )

# Get Bing connection ID
bing_connection = project_client.connections.get(name=bing_connection_name)

# Initialize agent bing custom search tool
bing_grounding = BingCustomSearchTool(
    connection_id=bing_connection.id, instance_name=bing_config_name)


# Create an agent
agent = agent_client.create_agent(
    model=model_deployment_name,
    name="Assistant that can search in Bing.",
    instructions="You are an agent that can search for the answers to the questions using Bing. You can use the Bing grounding tool to find information on the web.",
    tools=bing_grounding.definitions,  # Add the Bing grounding tool to the agent
)

print(f"Agent created with ID: {agent.id}")


# The Agent (with its knowledge tool) appears in the Azure AI Foundry portal under Agents.

# Let's speak with the agent.

# Create a thread
thread = agent_client.threads.create()
print(f"Created thread, thread ID: {thread.id}")

# Create a message
message = agent_client.messages.create(
    thread_id=thread.id,
    role="user",
    content="Can you provide the latest announcements about AI Foundry agents from the Build Conference 2025?",
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

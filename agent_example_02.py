"""
Example of using the Azure AI Agent service to create two connected agents.
One of the agents has a knowledge tool (Bing Custom Search).
The other agent is an orchestrator that can call the first agent.

This example demonstrates how to: Send a message to the orchestrator agent, and receive a response. And check the tool calls made by the agent.

Finally, clean up by deleting the agent and thread after use.

** Same instructions that the example 01:
* You will need to create a "Grounding with Bing Custom Search" in your Azure Subscription, 
* and create a connection to it in the Azure AI Foundry portal.
* Add the connection name to your .env file as `AZURE_BING_CONNECTION_NAME`.
* Add the Bing Search configuration name to your .env file as `AZURE_BING_SEARCH_CONFIG_NAME`.

** Same instructions that the example 00 and 01: 
* Also, you need the environment variables set in your .env file for this example to work:
* AZURE_AI_AGENT_ENDPOINT
* AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME

"""

# # Azure AI Agent service SDK reference:
# https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python

# # Create Agent with Bing Grounding doc example:
# https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python#create-agent-with-bing-grounding

# # Create a Connected Agent tool::
# https://learn.microsoft.com/en-us/python/api/azure-ai-agents/azure.ai.agents.models.connectedagenttool?view=azure-python

import os
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import BingCustomSearchTool, ConnectedAgentTool
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
bing_grounding = BingCustomSearchTool(connection_id=bing_connection.id, instance_name=bing_config_name)


#### Create an agent
bing_agent = agent_client.create_agent(
    model=model_deployment_name,
    name="Assistant that can search in Bing.",
    instructions="You are an agent that can search for the answers to the questions using Bing. You can use the Bing grounding tool to find information on the web.",
    tools=bing_grounding.definitions,  # Add the Bing grounding tool to the agent
)

print(f"Bing Agent created with ID: {bing_agent.id}")
# The Agent (with its knowledge tool) appears in the Azure AI Foundry portal under Agents.


# Create the tool for the connected agent
agent_tool = ConnectedAgentTool(id=bing_agent.id, name="bing_agent", description="Call this agent when you need to find information on the web.")



### Create another agent connected with the previous one.
orchestrator_agent = agent_client.create_agent(
    model=model_deployment_name,
    name="Orchestrator Agent",
    instructions="You are an agent that have several agents connected. You work as an orchestrator for other agents. Use the agent 'bing_agent' to search on the public web.",
    tools=agent_tool.definitions  # Connect to the bing agent
)
print(f"Orchestrator Agent created with ID: {bing_agent.id}")



#### Let's speak with the Orchestrator agent.

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
run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=orchestrator_agent.id)
print(f"Run finished with status: {run.status}")

if run.status == "failed":
    print(f"Run failed: {run.last_error}")

else:    
    # Get the response from the agent    
    response = agent_client.messages.list(thread_id=thread.id, run_id=run.id) # get all the messages in the thread
    for msg in response:
        if msg.role == "assistant":
            print(f"Agent response: {msg.content}")
           
            print("\nTool calls made by the agent:")  
            # update the thread to access tool calls
            thread = agent_client.threads.get(thread.id)  # Get the thread to access tool calls          
            print(f"Thread tool calls: {thread.metadata}")  # Print the tool calls made by the agent
            
            # update the run to access tool calls
            run = agent_client.runs.get(run_id=run.id, thread_id=thread.id)  # Get the run to access tool calls
            print(f"Run tool used: {run.tools[0]["connected_agent"]}")  # Print the tool calls made by the agent in the run

   
    
### Cleanup: Delete the agents and the thread.

agent_client.threads.delete(thread.id)
print(f"Deleted thread with ID: {thread.id}")

agent_client.delete_agent(bing_agent.id)
print(f"Deleted agent with ID: {bing_agent.id}")

agent_client.delete_agent(orchestrator_agent.id)
print(f"Deleted agent with ID: {orchestrator_agent.id}")
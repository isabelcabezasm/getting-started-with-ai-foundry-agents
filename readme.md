# Getting Started with AI Foundry Agents

Just my experiments with AI foundry agents. 

## Features

- I added a devcontainer with the needed tools for execute/debug this examples.

## Getting Started

1. **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd getting-started-with-ai-foundry-agents
    ```
2. **Open the devcontainer** 
or 
**Install dependencies:**
    - For Python:
      ```bash
      pip3 install -r requirements.txt
      ```
3. **Modify the .env file**
The endpoint can be found in the Azure Foundry portal
The format is : https://<resource>.services.ai.azure.com/api/projects/<project-name>.

For the example 01 and 02 you will need to create a "Grounding with Bing Custom Search" resource, and add a connection to that service in the AI Foundry project.


4. **Run or debug your agent:**    
    - Python:
      ```bash
      python3 agent_example_xx.py
      ```

## Examples

- Example 0: This is the simplest example of using the Azure AI Agent service to create an agent, send a message, and receive a response.
- Example 1: Example of using the Azure AI Agent service to create an agent, and add a knowledge tool (Bing Custom Search) to it. Send a message, and receive a response.
- Example 2: Example of using the Azure AI Agent service to create two connected agents. One of the agents has a knowledge tool (Bing Custom Search). The other agent is an orchestrator that can call the first agent.
- Example 3: Create a Semantic Kernel agent that interacts with the Azure AI Foundry Agent service.
- Example 4: Semantic Kernel agent with a SK plugin used by the agent. The agent uses Azure AI Foundry Agent service to generate the answer and access to the plugin. 

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.

---
May the Force be with your code!
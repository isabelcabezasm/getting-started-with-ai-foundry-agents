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

For the example 01 you will need to create a "Grounding with Bing Custom Search" resource, and add a connection to that service in the AI Foundry project.


4. **Run or debug your agent:**    
    - Python:
      ```bash
      python3 agent_example_xx.py
      ```

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.

---
May the Force be with your code!
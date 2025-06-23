import asyncio

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents import GroupChatOrchestration, RoundRobinGroupChatManager, BooleanResult
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.contents import AuthorRole
from semantic_kernel.contents import ChatMessageContent



"""
The following sample demonstrates how to create two agents using
Azure AI Foundry, and then a chat completion group and have them participate in 
this group chat to work towards the user's requirement.

it's using a 'Termination strategy' that allows one agent to approve the work of another agent, based in Round Robin.

We are defining a `callball` function that will be called when an agent sends a message in the group chat.

Based on this example:
https://github.com/microsoft/semantic-kernel/blob/main/python/samples/getting_started_with_agents/azure_ai_agent/step3_azure_ai_agent_group_chat.py
but using GroupChatOrchestration instead of AgentGroupChat, that is deprecated.

Read more about the `GroupChatOrchestration` here:
https://learn.microsoft.com/semantic-kernel/frameworks/agent/agent-orchestration/group-chat?pivots=programming-language-python

"""


class ApprovalGroupChatManager(RoundRobinGroupChatManager):
    def __init__(self, approver_name: str, max_rounds: int = 10):
        super().__init__(max_rounds=max_rounds)
        self._approver_name = approver_name

    async def should_terminate(self, chat_history):
        last = chat_history[-1] if chat_history else None
        should_terminate = (
            last is not None and
            getattr(last, 'name', None) == self._approver_name and
            'approved' in (last.content or '').lower()
        )
        return BooleanResult(result=should_terminate, reason="Approved by reviewer." if should_terminate else "Not yet approved.")

async def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"**{message.name}**\n{message.content}")
    await asyncio.sleep(5)  # Add a 5-second delay after each message

REVIEWER_NAME = "ArtDirector"
REVIEWER_INSTRUCTIONS = """
You are an art director who has opinions about copywriting born of a love for David Ogilvy.
The goal is to determine if the given copy is acceptable to print.
If so, state that it is approved.  Do not use the word "approve" unless you are giving approval.
If not, provide insight on how to refine suggested copy without example.
"""
REVIEWER_DESCRIPTION = "Art director agent who has opinions about copywriting born of a love for David Ogilvy."

COPYWRITER_NAME = "CopyWriter"
COPYWRITER_INSTRUCTIONS = """
You are a copywriter with ten years of experience and are known for brevity and a dry humor.
The goal is to refine and decide on the single best copy as an expert in the field.
Only provide a single proposal per response.
You're laser focused on the goal at hand.
Don't waste time with chit chat.
Consider suggestions when refining an idea.
"""
COPYWRITER_DESCRIPTION = "Copywriter agent with ten years of experience known for brevity and dry humor."

TASK = "a slogan for a new line of electric cars."



async def main():
    ai_agent_settings = AzureAIAgentSettings()
    

    agent_client = AzureAIAgent.create_client(credential=DefaultAzureCredential(), 
                                            endpoint=ai_agent_settings.endpoint)


    # 1. Create the reviewer agent on the Azure AI agent service
    reviewer_agent_definition = await agent_client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=REVIEWER_NAME,
        description=REVIEWER_DESCRIPTION,
        instructions=REVIEWER_INSTRUCTIONS,
    )

    # 2. Create a Semantic Kernel agent for the reviewer Azure AI agent
    agent_reviewer = AzureAIAgent(
        client=agent_client,
        definition=reviewer_agent_definition,
        description="An art director who has opinions about copywriting born of a love for David Ogilvy.",       
    )

    # 3. Create the copy writer agent on the Azure AI agent service
    copy_writer_agent_definition = await agent_client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=COPYWRITER_NAME,
        description=COPYWRITER_DESCRIPTION,
        instructions=COPYWRITER_INSTRUCTIONS,
    )

    # 4. Create a Semantic Kernel agent for the copy writer Azure AI agent
    agent_writer = AzureAIAgent(
        client=agent_client,
        definition=copy_writer_agent_definition,
    )

    group_chat_orchestration = GroupChatOrchestration(
            members=[agent_writer, agent_reviewer],
            manager=ApprovalGroupChatManager(approver_name=REVIEWER_NAME),
            agent_response_callback=agent_response_callback,
        )

    try:
        # 6. Add the task as a message to the group chat
        # await chat.add_chat_message(message=TASK)
        runtime = InProcessRuntime()
        runtime.start()
        
        print(f"# {AuthorRole.USER}: '{TASK}'")            
        
        # 7. Invoke the chat
        # async for content in chat.invoke():
        orchestration_result = await group_chat_orchestration.invoke(task=TASK, runtime=runtime)
        value = await orchestration_result.get()      
        print(f"***** Result *****\n{value}")
      
        # print(f"# {content.role} - {content.name or '*'}: '{content.content}'")
        # ???has this value role, name or content????
        await runtime.stop_when_idle()

        
    finally:
        # 8. Cleanup: Delete the agents
        await agent_client.agents.delete_agent(agent_reviewer.id)
        await agent_client.agents.delete_agent(agent_writer.id)

        """
        Sample Output:
        # AuthorRole.USER: 'a slogan for a new line of electric cars.'
        # AuthorRole.ASSISTANT - CopyWriter: '"Charge Ahead: Drive the Future."'
        # AuthorRole.ASSISTANT - ArtDirector: 'This slogan has a nice ring to it and captures the ...'
        # AuthorRole.ASSISTANT - CopyWriter: '"Plug In. Drive Green."'
        ...
        """


if __name__ == "__main__":
    asyncio.run(main())
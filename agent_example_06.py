import asyncio

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents import GroupChatOrchestration, RoundRobinGroupChatManager, BooleanResult
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.contents import AuthorRole
from semantic_kernel.contents import ChatMessageContent


"""
The following sample demonstrates how to create two agents using
Azure AI Foundry, and then a chat completion group and have them participate in 
this group chat to work towards the user's requirement.

it's using a 'Termination strategy' that allows one agent to approve the work of another agent, based in Round Robin.

We are defining a `callball` function that will be called when an agent sends a message in the group chat.

Our two agents are a "teacher" and a "student", the teacher creates a math question and the student tries to answer it.
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
        return BooleanResult(result=should_terminate, reason="Approved by teacher." if should_terminate else "Not yet approved.")

async def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"**{message.name}**\n{message.content}")
    await asyncio.sleep(5)  # Add a 5-second delay after each message

TEACHER_NAME = "Teacher"
TEACHER_INSTRUCTIONS = """

  You are a teacher that create an easy math question for student and check answer.
  The goal is to determine if the given answer is correct.
          If the answer is correct, you stop the conversation by saying "approved".
          If the answer is wrong, you ask student to fix it.
"""
TEACHER_DESCRIPTION = "Teacher agent that creates pre-school math questions for students and checks answers."

STUDENT_NAME = "Student"
STUDENT_INSTRUCTIONS = "You are a student that answer question from teacher, when teacher gives you question you answer them."
STUDENT_DESCRIPTION = "Student agent that tries to answer questions from teacher."

TASK = "Ask to the teacher to give you a math problem and solve it"



async def main():
    ai_agent_settings = AzureAIAgentSettings()
    

    agent_client = AzureAIAgent.create_client(credential=DefaultAzureCredential(), 
                                            endpoint=ai_agent_settings.endpoint)


    # 1. Create the teacher agent on the Azure AI agent service
    teacher_agent_definition = await agent_client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=TEACHER_NAME,
        description=TEACHER_DESCRIPTION,
        instructions=TEACHER_INSTRUCTIONS,
    )

    # 2. Create a Semantic Kernel agent for the teacher Azure AI agent
    agent_teacher = AzureAIAgent(
        client=agent_client,
        definition=teacher_agent_definition,
        description=TEACHER_DESCRIPTION,       
    )

    # 3. Create the student agent on the Azure AI agent service
    copy_student_agent_definition = await agent_client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=STUDENT_NAME,
        description=STUDENT_DESCRIPTION,
        instructions=STUDENT_INSTRUCTIONS,
    )

    # 4. Create a Semantic Kernel agent for the student Azure AI agent
    agent_student = AzureAIAgent(
        client=agent_client,
        definition=copy_student_agent_definition,
    )

    group_chat_orchestration = GroupChatOrchestration(
            members=[agent_student, agent_teacher],
            manager=ApprovalGroupChatManager(approver_name=TEACHER_NAME),
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
        await agent_client.agents.delete_agent(agent_teacher.id)
        await agent_client.agents.delete_agent(agent_student.id)

        """
        Sample Output:
        # AuthorRole.USER: 'Ask to the teacher to give you a math problem and solve it'
        # **Student**: Hi, teacher! Could you please give me a math problem to solve? I'm ready to work on it!
        # **Teacher**: Sure! Here's your math problem:  
        If you have 3 apples and I give you 2 more apples, how many apples do you have in total?
        # **Student**: If I already have 3 apples, and you give me 2 more apples, I would have **5 apples** total!
        # **Teacher**:  Correct! Approved.
        # ***** Result ***** Correct! Approved.
        """


if __name__ == "__main__":
    asyncio.run(main())
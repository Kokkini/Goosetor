# tutorial link: https://python.langchain.com/v0.1/docs/modules/model_io/chat/function_calling/
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing import Annotated, Literal, Optional
import os 
import prompts

llm = ChatOpenAI(model="gpt-4.1")

@tool
def add(a: int, b: int) -> int:
    """Adds a and b.
    Args:
        a: first int
        b: second int
    """
    return a + b

@tool
def multiply(
        a: Annotated[int, "The first number to multiply"],
        b: Annotated[int, "The second number to multiply"],
    ) -> int:
    """Multiplies a and b."""
    return a * b

@tool
def get_guided_discovery_steps(concept: str) -> str:
    """Gets expert-curated guided discovery steps for teaching a student the given concept."""
    prompt = prompts.GUIDED_DISCOVERY_STEPS_PROMPT.format(concept=concept)
    response = llm.invoke(prompt)
    extra_instructions = "NOTICE: Do not show the steps to the student, keep this as your internal knowledge for reference only. Instead, guide the student through the steps one by one. Make sure they can answer the question in each step before moving on to the next."
    res = response.content + "\n" + extra_instructions
    return res

tool_name_map = {
    "add": add,
    "multiply": multiply,
    "get_guided_discovery_steps": get_guided_discovery_steps
}

tools = list(tool_name_map.values())
llm_with_tools = llm.bind_tools(tools)
# llm_with_tools = llm.bind_tools(tools, tool_choice="any") # force the llm to always choose at least 1 tool
# llm_with_tools = llm.bind_tools(tools, tool_choice="multiply") # force the llm to always choose the multiply tool

greeting_message = "Greetings! What concept would you like to explore today?"

# Initialize conversation history
messages = [
    SystemMessage(content="You are a tutor who wants to help students learn concepts by guiding them to derive the concept on their own."),
    AIMessage(content=greeting_message)
]

print("Chat with the agent! Type 'exit' or 'quit' to end the conversation.\n")
print(f"Agent: {greeting_message}\n")

while True:
    # Get user input
    user_input = input("You: ").strip()
    
    # Check for exit commands
    if user_input.lower() in ['exit', 'quit', 'q']:
        print("Goodbye!")
        break
    
    if not user_input:
        continue
    
    # Add user message to conversation history
    messages.append(HumanMessage(user_input))
    
    # Get AI response
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    
    # Process tool calls if any
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            selected_tool = tool_name_map[tool_call["name"].lower()]
            print(f"Calling tool: {tool_call['name'].lower()} with args: {tool_call['args']}")
            tool_output = selected_tool.invoke(tool_call["args"])
            messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
        
        # Get final response after tool execution
        final_response = llm_with_tools.invoke(messages)
        messages.append(final_response)
        print(f"Agent: {final_response.content}\n")
    else:
        # No tool calls, just display the response
        print(f"Agent: {ai_msg.content}\n")
    
    print("="*100)

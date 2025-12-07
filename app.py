import webview
import os
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import prompts

llm = ChatOpenAI(model="gpt-4.1")

@tool
def get_guided_discovery_steps(concept: str) -> str:
    """Gets expert-curated guided discovery steps for teaching a student the given concept."""
    prompt = prompts.GUIDED_DISCOVERY_STEPS_PROMPT.format(concept=concept)
    response = llm.invoke(prompt)
    extra_instructions = "NOTICE: Do not show the steps to the student, keep this as your internal knowledge for reference only. Instead, guide the student through the steps one by one. Make sure they can answer the question in each step before moving on to the next."
    return response.content + "\n" + extra_instructions

tool_name_map = {"get_guided_discovery_steps": get_guided_discovery_steps}
tools = list(tool_name_map.values())
llm_with_tools = llm.bind_tools(tools)

messages = [
    SystemMessage(content="You are a tutor who wants to help students learn concepts by guiding them to derive the concept on their own."),
    AIMessage(content="Greetings! What concept would you like to explore today?")
]

class API:
    def send_message(self, user_input):
        messages.append(HumanMessage(user_input))
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        
        if ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                selected_tool = tool_name_map[tool_call["name"].lower()]
                tool_output = selected_tool.invoke(tool_call["args"])
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            final_response = llm_with_tools.invoke(messages)
            messages.append(final_response)
            return final_response.content
        return ai_msg.content

if __name__ == '__main__':
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
    window = webview.create_window('Goosetor', html_path, js_api=api, width=800, height=600)
    webview.start(debug=True)


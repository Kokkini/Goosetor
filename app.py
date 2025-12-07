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

@tool
def set_problem_statement(title: str, description: str, test_case: str = "", visualization: str = "") -> str:
    """Sets the problem statement, test case, and visualization in the problem section. Use this when introducing a new problem to the student."""
    global problem_statement
    print("Visualization: ")
    print(visualization)
    problem_statement = {
        "title": title,
        "description": description,
        "test_case": test_case,
        "visualization": visualization
    }
    return f"Problem '{title}' has been set."

tool_name_map = {"get_guided_discovery_steps": get_guided_discovery_steps, "set_problem_statement": set_problem_statement}
tools = list(tool_name_map.values())
llm_with_tools = llm.bind_tools(tools)

messages = [
    SystemMessage(content="You are a tutor who wants to help students learn concepts by guiding them to derive the concept on their own. When introducing a new problem or concept, use the set_problem_statement tool to display the problem statement, test case, and visualization in the problem section."),
    AIMessage(content="Greetings! What concept would you like to explore today?")
]

problem_statement = {"title": "", "description": "", "test_case": "", "visualization": ""}

class API:
    def send_message(self, user_input):
        messages.append(HumanMessage(user_input))
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)
        
        if ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                selected_tool = tool_name_map[tool_call["name"].lower()]
                print(f"Calling tool: {tool_call['name'].lower()} with args: {tool_call['args']}")
                tool_output = selected_tool.invoke(tool_call["args"])
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            final_response = llm_with_tools.invoke(messages)
            messages.append(final_response)
            return final_response.content
        return ai_msg.content
    
    def update_problem(self, title, description, test_case, visualization):
        global problem_statement
        problem_statement = {
            "title": title or "",
            "description": description or "",
            "test_case": test_case or "",
            "visualization": visualization or ""
        }
        return "Problem updated"
    
    def get_problem(self):
        return problem_statement

if __name__ == '__main__':
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
    window = webview.create_window('Goosetor', html_path, js_api=api, width=1200, height=700)
    webview.start(debug=True)


import webview
import os
import difflib
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import prompts

CODE_UPDATE_MESSAGE = "User updated the coding section"

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

@tool
def get_coding_section() -> str:
    """Gets the current content of the coding section where the student writes code."""
    global coding_section_content
    return coding_section_content or ""

@tool
def get_problem_statement() -> str:
    """Gets the current problem statement, test case, and visualization."""
    global problem_statement
    return f"Title: {problem_statement['title']}\nDescription: {problem_statement['description']}\nTest Case: {problem_statement['test_case']}\nVisualization: {problem_statement['visualization']}"

tool_name_map = {
    "get_guided_discovery_steps": get_guided_discovery_steps,
    "set_problem_statement": set_problem_statement,
    "get_coding_section": get_coding_section,
    "get_problem_statement": get_problem_statement
}
tools = list(tool_name_map.values())
llm_with_tools = llm.bind_tools(tools)

messages = [
    SystemMessage(content="You are a tutor who wants to help students learn concepts by guiding them to derive the concept on their own. When introducing a new problem or concept, use the set_problem_statement tool to display the problem statement, test case, and visualization in the problem section."),
    AIMessage(content="Greetings! What concept would you like to explore today?")
]

problem_statement = {"title": "", "description": "", "test_case": "", "visualization": ""}
coding_section_content = ""
last_seen_coding_content = ""

def print_messages(messages):
    print("Messages: ")
    for message in messages:
        print(message.type)
        print(message)

class API:
    def send_message(self, user_input):
        global coding_section_content, last_seen_coding_content
        
        if messages and isinstance(messages[-1], SystemMessage) and messages[-1].content == CODE_UPDATE_MESSAGE:
            old_lines = (last_seen_coding_content or "").splitlines(keepends=True)
            new_lines = (coding_section_content or "").splitlines(keepends=True)
            diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="code", tofile="code", lineterm=""))
            diff_str = "".join(diff)
            if diff_str:
                messages.append(SystemMessage(f"Code changes:\n{diff_str}"))
                last_seen_coding_content = coding_section_content
        
        messages.append(HumanMessage(user_input))
        print_messages(messages)
        ai_msg = llm_with_tools.invoke(messages)
        print(f"ai\n{ai_msg.content}")
        messages.append(ai_msg)
        
        if ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                selected_tool = tool_name_map[tool_call["name"].lower()]
                print(f"Calling tool: {tool_call['name'].lower()} with args: {tool_call['args']}")
                tool_output = selected_tool.invoke(tool_call["args"])
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            print_messages(messages)
            final_response = llm_with_tools.invoke(messages)
            messages.append(final_response)
            print(f"ai\n{final_response.content}")
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
    
    def set_coding_section(self, content):
        global coding_section_content, messages
        if coding_section_content != content:
            coding_section_content = content
            if not messages or not isinstance(messages[-1], SystemMessage) or messages[-1].content != CODE_UPDATE_MESSAGE:
                messages.append(SystemMessage(CODE_UPDATE_MESSAGE))
        return "Code updated"
    
    def get_coding_section(self):
        global coding_section_content
        return coding_section_content

if __name__ == '__main__':
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
    window = webview.create_window('Goosetor', html_path, js_api=api, width=1200, height=700)
    webview.start(debug=True)


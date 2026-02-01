import webview
import os
import difflib
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import prompts
from pydantic import BaseModel, Field
from typing import Literal, List
from textwrap import dedent

llm = ChatOpenAI(model="gpt-4.1")
class TeachingStep(BaseModel):
    content: str
    status: Literal["not_started", "in_progress", "completed"] = Field(description="The status of the teaching step. 'not_started' means you haven't taught the step yet. 'in_progress' means you are teaching the step. 'completed' means the student has finished the step. In the beginning, all steps should be 'not_started'.")

class TeachingStepList(BaseModel):
    concept: str
    steps: List[TeachingStep]

CODE_UPDATE_MESSAGE = "User updated the notebook"
TEACHING_STEPS = TeachingStepList(concept="", steps=[])

def print_teaching_steps(teaching_step_list: TeachingStepList) -> None:
    print("==========TEACHING_STEPS==========")
    print(f"Concept: {teaching_step_list.concept}")
    for step in teaching_step_list.steps:
        print(f"Step: {step.content}")
        print(f"Status: {step.status}")
    print("==================================")

def update_teaching_steps(teaching_step_list: TeachingStepList, messages: List[BaseMessage]) -> None:
    """Update the teaching steps based on the current state of the conversation."""
    if teaching_step_list.concept == "" or len(teaching_step_list.steps) == 0:
        return
    structured_llm = llm.with_structured_output(TeachingStepList)
    prompt = prompts.UPDATE_TEACHING_STEPS_PROMPT.format(teaching_step_list=teaching_step_list.model_dump_json())
    temp_messages = messages + [HumanMessage(prompt)]
    print(f"messages for update_teaching_steps:\n{temp_messages}")
    response = structured_llm.invoke(temp_messages)
    teaching_step_list.concept = response.concept
    teaching_step_list.steps = response.steps
    print_teaching_steps(response)

def get_expert_teaching_steps_v1(concept: str) -> str:
    """Gets expert-curated checklist for teaching a student the given concept."""
    global TEACHING_STEPS
    prompt = prompts.GUIDED_DISCOVERY_STEPS_PROMPT_V2.format(concept=concept)
    structured_llm = llm.with_structured_output(TeachingStepList)
    response = structured_llm.invoke(prompt)
    TEACHING_STEPS.concept = response.concept
    TEACHING_STEPS.steps = response.steps
    str_response = response.model_dump_json()
    extra_instructions = "NOTICE: Do not show the steps to the student, keep this as your internal knowledge for reference only. Instead, guide the student through the steps one by one. Make sure they can answer the question in each step before moving on to the next. Now use the set_problem_statement to create a concreate coding problem."
    return str_response + "\n" + extra_instructions

def get_expert_teaching_steps_v2(concept: str) -> str:
    """Gets expert-curated checklist for teaching a student the given concept."""
    global TEACHING_STEPS
    messages = prompts.TEACHING_STEPS_HISTORY + [HumanMessage(content=f"How would you teach {concept}? Make sure to include a step that assign a practice problem to the student by calling the set_problem_statement tool.")]
    structured_llm = llm.with_structured_output(TeachingStepList)
    response = structured_llm.invoke(messages)
    TEACHING_STEPS.concept = response.concept
    TEACHING_STEPS.steps = response.steps
    str_response = response.model_dump_json()
    print_teaching_steps(response)
    extra_instructions = "NOTICE: Do not show the steps to the student, keep this as your internal knowledge for reference only. Instead, guide the student through the steps one by one. Make sure they finish the step before moving on to the next."
    return str_response + "\n" + extra_instructions

@tool
def get_expert_teaching_steps(concept: str) -> str:
    """Gets expert-curated checklist for teaching a student the given concept."""
    return get_expert_teaching_steps_v2(concept)

@tool
def set_problem_statement(title: str, description: str, test_case: str = "", ascii_visualization: str = "") -> str:
    """Sets the problem statement, test case, and visualization in the problem section. Use this when introducing a new problem to the student."""
    global problem_statement
    print("Visualization: ")
    print(ascii_visualization)
    problem_statement = {
        "title": title,
        "description": description,
        "test_case": test_case,
        "visualization": ascii_visualization
    }
    return f"Problem '{title}' has been set."

@tool
def get_notebook_section() -> str:
    """Gets the current content of the notebook section where the student writes code, draw pictures, or write notes. Call this tool if the content from the diff is unclear"""
    global notebook_section_content
    return notebook_section_content or ""

@tool
def get_problem_statement() -> str:
    """Gets the current problem statement, test case, and visualization."""
    global problem_statement
    return f"Title: {problem_statement['title']}\nDescription: {problem_statement['description']}\nTest Case: {problem_statement['test_case']}\nVisualization: {problem_statement['visualization']}"

tool_name_map = {
    "get_expert_teaching_steps": get_expert_teaching_steps,
    "set_problem_statement": set_problem_statement,
    "get_notebook_section": get_notebook_section,
    "get_problem_statement": get_problem_statement
}
tools = list(tool_name_map.values())
llm_with_tools = llm.bind_tools(tools)

STARTING_MESSAGES = [
    SystemMessage(content=dedent("""
        You are a tutor who wants to help students learn concepts by guiding them to derive the concept on their own. 
        You are an expert at giving constructive feedback. That means:
        - Timely correction: You always give corrections to misunderstandings and errors right after the student makes them.
        - Supportive framing: Feedback focuses on improvement rather than judgment.
        Consult the expert with get_expert_teaching_steps before teaching any concept. If you want to give an assignment, use the set_problem_statement tool to set the problem statement.""")),
    AIMessage(content="Greetings! What concept would you like to explore today?")
]

messages = STARTING_MESSAGES.copy()

problem_statement = {"title": "", "description": "", "test_case": "", "visualization": ""}
notebook_section_content = ""
last_seen_notebook_content = ""

def print_messages(messages):
    print("Messages: ")
    for message in messages:
        print(message.type)
        print(message)

class API:
    def send_message(self, user_input):
        global notebook_section_content, last_seen_notebook_content, TEACHING_STEPS
        
        if messages and isinstance(messages[-1], SystemMessage) and messages[-1].content == CODE_UPDATE_MESSAGE:
            old_lines = (last_seen_notebook_content or "").splitlines(keepends=True)
            new_lines = (notebook_section_content or "").splitlines(keepends=True)
            diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="notebook", tofile="notebook", lineterm=""))
            diff_str = "".join(diff)
            if diff_str:
                messages.append(SystemMessage(f"Notebook changes:\n{diff_str}"))
                last_seen_notebook_content = notebook_section_content
        num_human_messages = len([message for message in messages if isinstance(message, HumanMessage)])
        if num_human_messages % 3 == 1:
            messages.append(SystemMessage(dedent("""
                Reminder: If there are key ideas or take-home messages, write the important part of the message in **bold**. Examples of good bold messages: Kinetic energy is the energy an object has **due to its motion**. An engine is a machine that **converts energy into mechanical work**.
            """).strip()))
        if (num_human_messages + 1) % 5 == 0:
            update_teaching_steps(TEACHING_STEPS, messages)
            messages.append(SystemMessage(f"Teaching steps updated: {TEACHING_STEPS.model_dump_json()}"))

        messages.append(HumanMessage(user_input))
        print_messages(messages)
        ai_msg = llm_with_tools.invoke(messages)
        print(f"ai\n{ai_msg}")
        messages.append(ai_msg)
        tool_calls = [tool_call for tool_call in ai_msg.tool_calls]
        if tool_calls:
            tool_index = 0
            while tool_index < len(tool_calls):
                tool_call = tool_calls[tool_index]
                selected_tool = tool_name_map[tool_call["name"].lower()]
                print(f"Calling tool: {tool_call['name'].lower()} with args: {tool_call['args']}")
                tool_output = selected_tool.invoke(tool_call["args"])
                print(f"tool\n{tool_output}")
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
                tool_index += 1
                if tool_index == len(tool_calls):
                    response = llm_with_tools.invoke(messages)
                    print(f"ai\n{response}")
                    messages.append(response)
                    if response.tool_calls:
                        for tool_call in response.tool_calls: tool_calls.append(tool_call)
                    else:
                        return response.content
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
    
    def set_notebook_section(self, content):
        global notebook_section_content, messages
        if notebook_section_content != content:
            notebook_section_content = content
            if not messages or not isinstance(messages[-1], SystemMessage) or messages[-1].content != CODE_UPDATE_MESSAGE:
                messages.append(SystemMessage(CODE_UPDATE_MESSAGE))
        return "Code updated"
    
    def get_notebook_section(self):
        global notebook_section_content
        return notebook_section_content

    def new_session(self):
        global messages, problem_statement, notebook_section_content, last_seen_notebook_content, TEACHING_STEPS
        messages = STARTING_MESSAGES.copy()
        problem_statement = {"title": "", "description": "", "test_case": "", "visualization": ""}
        notebook_section_content = ""
        last_seen_notebook_content = ""
        TEACHING_STEPS = TeachingStepList(concept="", steps=[])
        return "Session cleared"

if __name__ == '__main__':
    api = API()
    html_path = os.path.join(os.path.dirname(__file__), 'web', 'index.html')
    window = webview.create_window('Goosetor', html_path, js_api=api, width=1200, height=700)
    webview.start(debug=False)


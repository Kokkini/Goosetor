This tutoring software is for teaching concepts in algorithms and data structures. It should have a frontend with the following sections:
- Chat section: for the tutor to chat with the user.
- Problem statement section: for the LLM tutor to write the problem statement, a concrete test case and visualization.(like on LeetCode)
- Coding section: for the user to write code to solve the problem. For the MVP version, there is no need to compile and run the code, the LLM tutor will check the code and give comments, just like a human tutor checking code writen on paper.
- With each new concept, the tutor will give a problem and guide the student on how to solve it. This will motivate the concept and allow the student to remember it for a long time.
This software should be easy to distribute and very cheap (even free) to host. The user should come with their own OpenAI API key.

# CONTEXT ENGINEERING
The agent will have the following tools:
- get_coding_section
- get_coding_section_diff: get the difference between the current content of the coding section and the last time that the LLM sees the coding section
- get_problem_statement
- set_problem_statement
- get_guided_discovery_steps
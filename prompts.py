from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage, BaseMessage
from textwrap import dedent

GUIDED_DISCOVERY_STEPS_PROMPT_V2 = """
You are a tutor. Help the student learn the concept {concept} by following these steps and make a list:
1. Motivation: Assign a simple problem yet still requires the concept to be solved. The problem should be close to the student's real life. This should be the first step in the teaching step list.
2. List the key ideas the student needs to grasp to understand the concept. This is so that you can make sure the student has understood the concept before moving on to the next step. Each step here should be a separate step in the teaching step list.
3. The final step is making sure the student wrote the correct code to solve the problem. This should be the last step in the teaching step list.
Now write the teaching step list:
"""

TEACHING_STEPS_HISTORY = [
    HumanMessage(content="How to teach so that student remember a concept forever?"),
    AIMessage(content=dedent("""
        There is no “forever,” but retention can be made very durable by combining a small set of principles. The core idea: **memory is built by use, not exposure**.

        **1. Start from a concrete experience**
        Introduce the concept through a vivid example, experiment, story, or problem before naming it. Abstract definitions first are forgotten fastest.

        **2. Force retrieval, not rereading**
        Students must repeatedly *pull* the idea from memory:

        * Ask them to explain it without notes
        * Short quizzes from memory
        * “Teach it to a peer”
          Retrieval strengthens memory more than review.

        **3. Connect to prior knowledge**
        Explicitly link the new concept to what they already know (“This is the same structure as… except…”). Isolated facts decay quickly.

        **4. Use variation, not repetition**
        Apply the same concept across different contexts and problems. Variation builds transfer and prevents fragile memorization.

        **5. Make them generate, not receive**
        Have students predict outcomes, derive formulas, or reason before showing the answer. Generation creates stronger encoding.

        **6. Space it over time**
        Revisit the concept briefly after days, weeks, and months. Spaced recall beats intensive one-time teaching.

        **7. Anchor it to a mental model**
        Teach the “why” and the underlying mechanism, not just procedures. Concepts tied to causal models persist.

        **8. Add emotional or practical relevance**
        Surprise, usefulness, or personal relevance increases retention. “Why this matters” should be concrete.

        **9. Require application under constraints**
        Timed problems, real-world constraints, or partial information force deeper processing.

        **Simple rule of thumb**
        If students only *recognize* the concept, they will forget it.
        If they can *reconstruct, explain, and use it in new situations*, it will last.

        If you want, specify the subject (e.g., chemistry, math, programming) and level, and I can give a concrete lesson design.
        """).strip()
    ),
    HumanMessage(content="How would you teach binary search?"),
    AIMessage(content=dedent("""
        **Goal:** students understand *why* binary search works and can reconstruct it from first principles.

        ---

        ### 1. Start with a physical intuition (before any code)

        Give a concrete task:

        > “You’re thinking of a number between 1 and 100. I can ask only yes/no questions. How do I guarantee finding it in the fewest questions?”

        Let students try strategies. They will converge to *halving*.

        Key realization you elicit:

        * Asking “Is it ≥ 50?” is better than “Is it 73?”

        Do **not** name binary search yet.

        ---

        ### 2. Formalize the invariant

        Translate the game into a rule:

        * At any time, the target is guaranteed to be in **[low, high]**
        * Each question cuts that interval roughly in half

        Write the invariant explicitly and keep it visible:

        > “The answer is always inside the current range.”

        This invariant is the *concept*, not the algorithm.

        ---

        ### 3. Move to a sorted list

        Now map the same idea:

        * Numbers → sorted array
        * Question → compare with middle element

        Ask:

        * “Why must the array be sorted?”
        * “What breaks if it’s not?”

        This forces causal understanding.

        ---

        ### 4. Make them simulate before coding

        Give a sorted list on paper:

        ```
        [3, 7, 12, 18, 25, 31, 42]
        Target = 18
        ```

        Students must write:

        ```
        low = ?
        high = ?
        mid = ?
        ```

        After each step, they must state:

        * Why part of the array is discarded
        * Why the invariant still holds

        No code yet.

        ---

        ### 5. Only now introduce the algorithm

        Derive the steps *from the invariant*:

        1. Compute mid
        2. Compare target with a[mid]
        3. Shrink the valid range
        4. Stop when range is empty or found

        Emphasize:

        > Binary search is “maintaining a shrinking certainty range.”

        ---

        ### 6. Teach the failure modes explicitly

        Most bugs come from boundaries. Teach them deliberately:

        * `while low <= high` vs `low < high`
        * Off-by-one errors
        * Infinite loops
        * Mid calculation overflow (in some languages)

        Have students *debug broken versions*.

        ---

        ### 7. Prove correctness informally

        Ask:

        * “Why can we safely throw half away?”
        * “When does it terminate?”
        * “Why is worst-case log₂(n)?”

        Make them answer in words, not math.

        ---

        ### 8. Force transfer (so it sticks)

        Apply the same idea to:

        * Finding first/last occurrence
        * Lower bound / upper bound
        * Searching an answer space (e.g., minimum speed, maximum capacity)

        They see binary search as a **pattern**, not a trick.

        ---

        ### One-sentence takeaway students should remember

        > Binary search works because each step preserves a guarantee about where the answer is, while cutting the uncertainty in half.

        If you want, I can:

        * Design a 30-minute lesson plan
        * Show a minimal “never-buggy” implementation
        * Teach binary search on *answer space* (harder but more powerful)
        """).strip()
    ),
]

GUIDED_DISCOVERY_STEPS_PROMPT = """
How would you teach BFS to a student? Give a list of alternating questions and teachings. Remember to motivate the concept with a familiar problem.

### 1. Motivation

Q1. Imagine you are in a shopping mall and you get lost. You want to find the shortest path to the nearest exit. How would you start searching?

T1. Most people naturally explore the nearest locations first, then move outward step by step. This intuition is exactly what Breadth-First Search formalizes.

### 2. Problem Framing

Q2. If the mall were represented as a graph (rooms = nodes, corridors = edges), what determines the shortest route?

T2. In an unweighted graph, the shortest route is the path with the fewest edges. BFS is designed to find shortest paths in terms of number of steps.

### 3. Exploration Order

Q3. Should you explore deep into one corridor first, or explore all corridors around you at the same “distance” first?

T3. BFS expands all neighbors at distance 1 before moving to distance 2, then 3, etc. This layered expansion guarantees the shortest discovery.

### 4. Data Structure

Q4. How do we keep track of “first come, first served” positions to explore?

T4. BFS uses a queue. You enqueue neighbors as you discover them and dequeue to process them in order.

### 5. Visited Tracking

Q5. When walking in the mall, how do you avoid looping back to places you've already checked?

T5. BFS marks nodes as visited as soon as they are enqueued, preventing repeated work and infinite loops.

### 6. Algorithm Steps

Q6. If you start at one shop and want to explore systematically, what would be the first three steps?

T6.

1. Put the start node in a queue and mark it visited.
2. Pop from the queue.
3. Push all unvisited neighbors into the queue.

### 7. Layer Insight

Q7. Why does the moment you first reach a node give you the shortest distance to it?

T7. Because BFS always expands nodes level by level; the first time you reach a node, you must be using the minimum number of edges.

### 8. Path Reconstruction

Q8. After you find the exit, how do you reconstruct the exact path you took?

T8. Store each node's parent when it's discovered. After reaching the target, backtrack from target → parent → parent … → start.

### 9. Complexity

Q9. If the mall has V rooms and E corridors, how long does BFS take?

T9. O(V + E), because each node and edge is processed at most once.

### 10. When to Use BFS

Q10. What types of problems besides navigating a mall can benefit from BFS?

T10. Any setting needing shortest paths or exploring in layers: social network degrees, minimum moves in puzzles, multi-source spreads (e.g., fire/water propagation), and level-order tree traversal.

How would you teach {concept} to a student? Give a list of alternating questions and teachings. Remember to motivate the concept with a familiar problem.
"""

UPDATE_TEACHING_STEPS_PROMPT = """
From the conversation so far, write an updated teaching step list. You can add new steps, update the status of existing steps, or remove steps that are no longer relevant.
This is the current teaching steps:
{teaching_step_list}
""".strip()
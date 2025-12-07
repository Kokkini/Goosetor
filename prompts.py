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
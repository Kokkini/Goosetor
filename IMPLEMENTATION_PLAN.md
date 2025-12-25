# Implementation Plan: Context Engineering Tools

## Overview
Implement the context engineering tools specified in DESIGN.md to allow the LLM tutor to interact with the coding section and problem statement.

## Current Status
- ✅ `set_problem_statement` - Already implemented
- ✅ `get_guided_discovery_steps` - Already implemented
- ❌ `get_coding_section` - Not implemented
- ❌ `get_coding_section_diff` - Not implemented
- ⚠️ `get_problem_statement` - Exists as API method but not as LLM tool

## Implementation Tasks

### 1. Frontend: Add Coding Section
**File**: `web/index.html`

- Add a coding section to the right panel (split vertically: problem on top, coding below)
- Use a simple `<textarea>` element (no syntax highlighting, no language assumption)
- Add line numbers display (can be implemented with CSS counter or a separate div)
- Style it consistently with the existing UI
- The coding section should be editable by the user
- Start with empty content

### 2. Backend: Add Coding Section State Management
**File**: `app.py`

- Add global variable `coding_section_content` to store current code (initialize as empty string)
- Add global variable `last_seen_coding_content` to track what LLM last saw (initialize as empty string)
- Add API method `get_coding_section()` to expose current content to frontend
- Add API method `set_coding_section(content)` to update from frontend
  - When content changes, trigger automatic notification mechanism (see task 6)

### 3. Backend: Implement `get_coding_section` Tool
**File**: `app.py`

```python
@tool
def get_coding_section() -> str:
    """Gets the current content of the coding section where the student writes code."""
    global coding_section_content
    return coding_section_content or ""
```

- Add to `tool_name_map`
- Bind to LLM

### 4. Backend: Implement `get_coding_section_diff` Tool
**File**: `app.py`

```python
@tool
def get_coding_section_diff() -> str:
    """Gets the difference between the current coding section content and the last time the LLM saw it. Returns empty string if no changes."""
    global coding_section_content, last_seen_coding_content
    # Use difflib.unified_diff() to generate git diff format
    # Update last_seen_coding_content after returning diff
    # Return git diff format string
```

**Implementation Details**:
- Use `difflib.unified_diff()` to generate git diff format
- Split content into lines for comparison
- Update `last_seen_coding_content` after returning diff
- Return empty string if no changes detected
- Format should match standard git diff output (with `---`, `+++`, `@@` markers)

### 5. Backend: Implement `get_problem_statement` Tool
**File**: `app.py`

```python
@tool
def get_problem_statement() -> str:
    """Gets the current problem statement, test case, and visualization."""
    global problem_statement
    return f"Title: {problem_statement['title']}\nDescription: {problem_statement['description']}\nTest Case: {problem_statement['test_case']}\nVisualization: {problem_statement['visualization']}"
```

- Add to `tool_name_map`
- Bind to LLM

### 6. Backend: Automatic Code Change Notification
**File**: `app.py`

- Modify `set_coding_section()` API method to:
  - Compare new content with current `coding_section_content`
  - If content changed:
    - Update `coding_section_content`
    - Check if last message in `messages` is "User updated the code section"
    - If not, append `HumanMessage("User updated the code section")` to `messages`
- Modify `send_message()` method to:
  - Before sending to LLM, check if last message is "User updated the code section"
  - If yes:
    - Compute diff between `coding_section_content` and `last_seen_coding_content`
    - Append diff as a `HumanMessage` to `messages` (e.g., "Code changes:\n{diff}")
    - Update `last_seen_coding_content` to current `coding_section_content`

### 7. Frontend: Connect Coding Section to Backend
**File**: `web/index.html`

- Add event listener to coding section textarea (on `input` or `change` event)
- On change, call `api.set_coding_section(content)` to sync with backend
- Debounce the API calls (e.g., 300ms) to avoid excessive calls while typing

### 8. Update System Prompt
**File**: `app.py`

- Update system message to inform LLM about new tools:
  - `get_coding_section`: Gets the full current code
  - `get_coding_section_diff`: Gets changes since last check (git diff format)
  - `get_problem_statement`: Gets current problem details
- Note that code changes are automatically notified in chat history
- Guide LLM to review code when notified of changes and provide feedback

## Technical Considerations

### Diff Algorithm
- Use `difflib.unified_diff()` to generate git diff format
- Split content into lines: `old_content.splitlines(keepends=True)` and `new_content.splitlines(keepends=True)`
- Format output to match standard git diff:
  ```
  --- a/code
  +++ b/code
  @@ -1,3 +1,4 @@
   line1
  +new line
   line2
  ```
- Return empty string if no differences found

### Automatic Notification Flow
1. User types in coding section → frontend calls `set_coding_section()`
2. Backend detects change → appends "User updated the code section" to messages (if not already last message)
3. User sends chat message → `send_message()` checks if last message is notification
4. If yes → compute diff, append to messages, update `last_seen_coding_content`
5. Send full message history to LLM (including diff)

### State Persistence
- Current implementation uses global variables (fine for MVP)
- No persistence needed (session-based)
- `coding_section_content` starts as empty string
- `last_seen_coding_content` starts as empty string

### Performance
- Diff computation should be fast for typical code sizes
- Debounce frontend API calls to reduce backend load
- Consider caching if needed (not critical for MVP)

## Testing Checklist
- [ ] Coding section appears in UI with textarea and line numbers
- [ ] User can type code in coding section
- [ ] Code syncs to backend on change
- [ ] `get_coding_section` returns current code
- [ ] `get_coding_section_diff` shows git diff format correctly
- [ ] `get_problem_statement` returns current problem
- [ ] LLM can call all tools successfully
- [ ] Diff updates `last_seen_coding_content` correctly
- [ ] Automatic notification: "User updated the code section" appears in chat when code changes
- [ ] Diff is automatically appended to chat history before LLM generation when notification exists
- [ ] Multiple rapid code changes don't create duplicate notifications
- [ ] Coding section starts empty

## Decisions Made

1. **Coding Section UI**:
   - Simple textarea (no syntax highlighting)
   - No programming language assumption
   - Line numbers displayed

2. **Diff Granularity**:
   - Git diff format using `difflib.unified_diff()`
   - Line-level changes

3. **When to Check Code**:
   - Automatic notification: When code changes, append "User updated the code section" to chat (if not already last message)
   - Before LLM generation: If last message is notification, append diff to chat history
   - No manual triggering needed

4. **Coding Section Initial State**:
   - Starts empty
   - LLM cannot set initial code (not needed for this stage)

5. **Multiple Files/Code Blocks**:
   - Single code block is sufficient for MVP

6. **Code Validation**:
   - No syntax validation needed
   - No specific error handling needed


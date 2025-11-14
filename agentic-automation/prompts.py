"""
Prompt templates grouped by responsibility (task, action, elements, verification).
"""


class TaskPrompts:
    system = """You are an expert web automation assistant. 
Your job is to understand user tasks and break them down into actionable steps.
Analyze the task and create a step-by-step plan."""

    @staticmethod
    def build(user_task: str, page_summary: str) -> str:
        return f"""User wants to: {user_task}

Current page state:
{page_summary}

Break down this task into specific steps. For each step, specify:
1. What action to take (click, type, navigate, wait, etc.)
2. What element or target to interact with
3. What value to use (if applicable)

Respond in JSON format:
{{
    "steps": [
        {{
            "step_number": 1,
            "action": "navigate|click|type|select|wait|verify",
            "target_description": "description of what to interact with",
            "value": "value to use (if applicable)",
            "reasoning": "why this step is needed"
        }}
    ],
    "expected_outcome": "what should happen after completing all steps"
}}"""


class ElementPrompts:
    system = """You are an expert at understanding web page structure.
Given a user's intent and a list of page elements, identify which element(s) match the intent.
Be precise and consider context, text content, and element types."""

    @staticmethod
    def build(intent: str, elements: list) -> str:
        elements_str = "\n".join([
            f"{i+1}. {elem['type']}: {elem['description']}"
            for i, elem in enumerate(elements)
        ])
        return f"""User intent: {intent}

Available elements on the page:
{elements_str}

Which element(s) match this intent? Consider:
- Text content
- Element type (button, link, input, etc.)
- Context and nearby elements
- Element attributes (id, class)

Respond in JSON format:
{{
    "matched_elements": [
        {{
            "index": 0,
            "confidence": 0.95,
            "reasoning": "why this element matches",
            "selector_strategy": "how to find it (id, xpath, text, etc.)",
            "selector_value": "actual selector value"
        }}
    ],
    "best_match": 0,
    "alternative_approaches": ["if best match fails, try these"]
}}"""


class ActionPrompts:
    system = """You are an expert web automation planner.
Given a task and current page state, determine the next action to take.
Consider what elements are available and what the user wants to accomplish."""

    @staticmethod
    def build(current_step: dict, page_summary: str, previous_results: list = None) -> str:
        results_str = ""
        if previous_results:
            results_str = "\nPrevious step results:\n"
            for r in previous_results:
                results_str += f"  - {r}\n"

        return f"""Current step to execute:
Action: {current_step.get('action', 'unknown')}
Target: {current_step.get('target_description', 'unknown')}
Value: {current_step.get('value', 'N/A')}
Reasoning: {current_step.get('reasoning', 'N/A')}

Current page state:
{page_summary}
{results_str}

Determine the specific Selenium action to take. Consider:
- What element selector to use
- What value to input (if typing)
- What to wait for (if waiting)
- How to verify success

IMPORTANT: If clicking a button that might open a modal (like "Add to Cart"), the system will automatically handle the modal confirmation. You don't need to plan for clicking buttons inside modals - just click the initial button.

Respond in JSON format:
{{
    "action": "click|type|select|navigate|wait|verify",
    "selector_type": "id|class|xpath|text|css",
    "selector_value": "actual selector",
    "value": "value to use (if applicable)",
    "wait_for": "what to wait for after action",
    "verification": "how to verify success"
}}"""


class VerificationPrompts:
    @staticmethod
    def build(task: str, page_summary: str) -> str:
        return f"""Original task: {task}

Current page state:
{page_summary}

Has the task been completed successfully? Check:
- Is the expected outcome visible?
- Are there any error messages?
- Is the page in the expected state?

Respond in JSON format:
{{
    "completed": true|false,
    "success": true|false,
    "evidence": "what indicates success or failure",
    "next_steps": ["if not complete, what to do next"]
}}"""
"""
Prompt templates for LLM interactions.

Contains reusable prompt templates for different agentic automation tasks.
"""

# System prompt for task understanding
TASK_UNDERSTANDING_SYSTEM = """You are an expert web automation assistant. 
Your job is to understand user tasks and break them down into actionable steps.
Analyze the task and create a step-by-step plan."""

# System prompt for element finding
ELEMENT_FINDING_SYSTEM = """You are an expert at understanding web page structure.
Given a user's intent and a list of page elements, identify which element(s) match the intent.
Be precise and consider context, text content, and element types."""

# System prompt for action planning
ACTION_PLANNING_SYSTEM = """You are an expert web automation planner.
Given a task and current page state, determine the next action to take.
Consider what elements are available and what the user wants to accomplish."""


def create_task_understanding_prompt(user_task: str, page_summary: str) -> str:
    """
    Create prompt for understanding user task.
    
    Args:
        user_task: Natural language task description
        page_summary: Summary of current page state
        
    Returns:
        Formatted prompt string
    """
    return f"""User wants to: {user_task}

Current page state:
{page_summary}

Break down this task into specific steps. For each step, specify:
1. What action to take (click, type, navigate, wait, etc.)
2. What element or target to interact with
3. What value to use (if applicable)

Respond in JSON format:
{{
    "steps": [
        {{
            "step_number": 1,
            "action": "navigate|click|type|select|wait|verify",
            "target_description": "description of what to interact with",
            "value": "value to use (if applicable)",
            "reasoning": "why this step is needed"
        }}
    ],
    "expected_outcome": "what should happen after completing all steps"
}}"""


def create_element_finding_prompt(intent: str, elements: list) -> str:
    """
    Create prompt for finding elements by intent.
    
    Args:
        intent: What the user wants to do (e.g., "click add to cart button")
        elements: List of element descriptions from page analyzer
        
    Returns:
        Formatted prompt string
    """
    elements_str = "\n".join([
        f"{i+1}. {elem['type']}: {elem['description']}"
        for i, elem in enumerate(elements)
    ])
    
    return f"""User intent: {intent}

Available elements on the page:
{elements_str}

Which element(s) match this intent? Consider:
- Text content
- Element type (button, link, input, etc.)
- Context and nearby elements
- Element attributes (id, class)

Respond in JSON format:
{{
    "matched_elements": [
        {{
            "index": 0,
            "confidence": 0.95,
            "reasoning": "why this element matches",
            "selector_strategy": "how to find it (id, xpath, text, etc.)",
            "selector_value": "actual selector value"
        }}
    ],
    "best_match": 0,
    "alternative_approaches": ["if best match fails, try these"]
}}"""


def create_action_planning_prompt(current_step: dict, page_summary: str, 
                                  previous_results: list = None) -> str:
    """
    Create prompt for planning next action.
    
    Args:
        current_step: Current step from task breakdown
        page_summary: Current page state
        previous_results: Results from previous steps (optional)
        
    Returns:
        Formatted prompt string
    """
    results_str = ""
    if previous_results:
        results_str = "\nPrevious step results:\n"
        for r in previous_results:
            results_str += f"  - {r}\n"
    
    return f"""Current step to execute:
Action: {current_step.get('action', 'unknown')}
Target: {current_step.get('target_description', 'unknown')}
Value: {current_step.get('value', 'N/A')}
Reasoning: {current_step.get('reasoning', 'N/A')}

Current page state:
{page_summary}
{results_str}

Determine the specific Selenium action to take. Consider:
- What element selector to use
- What value to input (if typing)
- What to wait for (if waiting)
- How to verify success

IMPORTANT: If clicking a button that might open a modal (like "Add to Cart"), the system will automatically handle the modal confirmation. You don't need to plan for clicking buttons inside modals - just click the initial button.

Respond in JSON format:
{{
    "action": "click|type|select|navigate|wait|verify",
    "selector_type": "id|class|xpath|text|css",
    "selector_value": "actual selector",
    "value": "value to use (if applicable)",
    "wait_for": "what to wait for after action",
    "verification": "how to verify success"
}}"""


def create_verification_prompt(task: str, page_summary: str) -> str:
    """
    Create prompt for verifying task completion.
    
    Args:
        task: Original user task
        page_summary: Current page state
        
    Returns:
        Formatted prompt string
    """
    return f"""Original task: {task}

Current page state:
{page_summary}

Has the task been completed successfully? Check:
- Is the expected outcome visible?
- Are there any error messages?
- Is the page in the expected state?

Respond in JSON format:
{{
    "completed": true|false,
    "success": true|false,
    "evidence": "what indicates success or failure",
    "next_steps": ["if not complete, what to do next"]
}}"""


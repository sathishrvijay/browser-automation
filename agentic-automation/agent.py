"""
Main Agent - Orchestrates the full agentic automation flow.

Coordinates page analysis, element finding, action planning, and execution.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Any, List, Optional

# Handle both relative and absolute imports
try:
    from .llm_client import LLMClient
    from .page_analyzer import PageAnalyzer
    from .element_finder import ElementFinder
    from .action_executor import ActionExecutor
    from .prompts import (
        create_task_understanding_prompt,
        create_action_planning_prompt,
        create_verification_prompt,
        TASK_UNDERSTANDING_SYSTEM,
        ACTION_PLANNING_SYSTEM
    )
except ImportError:
    # Fallback for direct module loading
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from llm_client import LLMClient
    from page_analyzer import PageAnalyzer
    from element_finder import ElementFinder
    from action_executor import ActionExecutor
    from prompts import (
        create_task_understanding_prompt,
        create_action_planning_prompt,
        create_verification_prompt,
        TASK_UNDERSTANDING_SYSTEM,
        ACTION_PLANNING_SYSTEM
    )


class AgenticAgent:
    """Main agent that orchestrates agentic automation."""
    
    def __init__(self, driver: WebDriver, llm_client: LLMClient, verbose: bool = True):
        """
        Initialize agentic agent.
        
        Args:
            driver: Selenium WebDriver instance
            llm_client: LLM client for understanding and planning
            verbose: Whether to print detailed logs
        """
        self.driver = driver
        self.llm_client = llm_client
        self.verbose = verbose
        self.page_analyzer = PageAnalyzer(driver, verbose=verbose)
        self.element_finder = ElementFinder(driver, llm_client, verbose=verbose)
        self.action_executor = ActionExecutor(driver, verbose=verbose)
        self.execution_history: List[Dict[str, Any]] = []
    
    def execute(self, task: str) -> Dict[str, Any]:
        """
        Execute a natural language task.
        
        Args:
            task: Natural language description of what to do
                (e.g., "Add 1 laptop to the cart for checkout")
        
        Returns:
            Dictionary with execution result:
                - success: bool
                - message: str
                - steps_completed: int
                - final_state: dict
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Task: {task}")
            print(f"{'='*60}\n")
        
        try:
            # Step 1: Understand task and create plan
            if self.verbose:
                print("[AGENT] Step 1: Understanding task and creating plan...")
            plan = self._understand_task(task)
            if not plan or 'steps' not in plan:
                return {
                    "success": False,
                    "message": "Failed to create execution plan"
                }
            
            if self.verbose:
                print(f"[AGENT] Created plan with {len(plan['steps'])} steps")
                print(f"[AGENT] Expected outcome: {plan.get('expected_outcome', 'N/A')}")
                print("\n[AGENT] Execution Plan:")
                for i, step in enumerate(plan['steps'], 1):
                    print(f"  {i}. {step.get('action', 'unknown')}: {step.get('target_description', 'N/A')}")
                    if self.verbose and step.get('reasoning'):
                        print(f"     Reasoning: {step.get('reasoning')}")
                print()
            
            # Step 2: Execute each step
            completed_steps = 0
            for i, step in enumerate(plan['steps'], 1):
                if self.verbose:
                    print(f"\n[AGENT] Step {i}/{len(plan['steps'])}: {step.get('action', 'unknown')} - {step.get('target_description', 'N/A')}")
                
                # Get current page state
                if self.verbose:
                    print(f"[AGENT] Analyzing current page...")
                page_summary = self.page_analyzer.get_page_summary()
                
                # Plan specific action
                if self.verbose:
                    print(f"[AGENT] Planning specific Selenium action...")
                action_plan = self._plan_action(step, page_summary)
                if not action_plan:
                    if self.verbose:
                        print(f"  ⚠️  Could not plan action for step {i}")
                    continue
                
                if self.verbose:
                    print(f"[AGENT] Action plan: {action_plan.get('action', 'unknown')} using {action_plan.get('selector_type', 'unknown')}={action_plan.get('selector_value', 'N/A')}")
                    if action_plan.get('value'):
                        print(f"[AGENT] Value: {action_plan.get('value')}")
                
                # Execute action
                if self.verbose:
                    print(f"[AGENT] Executing Selenium action...")
                result = self.action_executor.execute_action(action_plan)
                self.execution_history.append({
                    "step": i,
                    "step_description": step,
                    "action_plan": action_plan,
                    "result": result
                })
                
                if result.get('success'):
                    completed_steps += 1
                    if self.verbose:
                        print(f"  ✅ {result.get('message', 'Success')}")
                else:
                    if self.verbose:
                        print(f"  ❌ {result.get('message', 'Failed')}")
                    # Try to continue anyway
                
                # Brief pause between steps
                import time
                time.sleep(0.5)
            
            # Step 3: Verify completion
            if self.verbose:
                print(f"\n[AGENT] Verifying task completion...")
            final_page_summary = self.page_analyzer.get_page_summary()
            verification = self._verify_completion(task, final_page_summary)
            
            if self.verbose:
                print(f"[AGENT] Verification result: {verification.get('completed', False)} - {verification.get('evidence', 'N/A')}")
            
            return {
                "success": verification.get('completed', False) and verification.get('success', False),
                "message": verification.get('evidence', 'Task completed'),
                "steps_completed": completed_steps,
                "total_steps": len(plan['steps']),
                "final_state": {
                    "url": self.driver.current_url,
                    "title": self.driver.title,
                    "verification": verification
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during execution: {str(e)}",
                "steps_completed": completed_steps if 'completed_steps' in locals() else 0
            }
    
    def _understand_task(self, task: str) -> Optional[Dict[str, Any]]:
        """Understand task and create execution plan."""
        page_summary = self.page_analyzer.get_page_summary()
        prompt = create_task_understanding_prompt(task, page_summary)
        
        if self.verbose:
            print(f"[AGENT] Sending task understanding prompt to LLM...")
            print(f"[AGENT] Page summary length: {len(page_summary)} chars")
        
        try:
            plan = self.llm_client.complete_json(
                prompt,
                system_prompt=TASK_UNDERSTANDING_SYSTEM,
                temperature=0.3
            )
            return plan
        except Exception as e:
            if self.verbose:
                print(f"[AGENT] Error understanding task: {e}")
            return None
    
    def _plan_action(self, step: Dict[str, Any], page_summary: str) -> Optional[Dict[str, Any]]:
        """Plan specific action for a step."""
        previous_results = [
            h['result'].get('message', '') 
            for h in self.execution_history[-3:]  # Last 3 results
        ]
        
        prompt = create_action_planning_prompt(step, page_summary, previous_results)
        
        if self.verbose:
            print(f"[AGENT] Sending action planning prompt to LLM...")
            if previous_results:
                print(f"[AGENT] Previous results context: {previous_results}")
        
        try:
            action_plan = self.llm_client.complete_json(
                prompt,
                system_prompt=ACTION_PLANNING_SYSTEM,
                temperature=0.2
            )
            return action_plan
        except Exception as e:
            if self.verbose:
                print(f"[AGENT] Error planning action: {e}")
            return None
    
    def _verify_completion(self, task: str, page_summary: str) -> Dict[str, Any]:
        """Verify if task was completed successfully."""
        prompt = create_verification_prompt(task, page_summary)
        
        try:
            verification = self.llm_client.complete_json(
                prompt,
                temperature=0.2
            )
            return verification
        except Exception as e:
            if self.verbose:
                print(f"Error verifying completion: {e}")
            return {"completed": False, "success": False, "evidence": str(e)}


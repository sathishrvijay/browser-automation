"""
Main Agent - Orchestrates the full agentic automation flow.

Coordinates page analysis, element finding, action planning, and execution.
"""

import time
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, Any, List, Optional

# Handle both relative and absolute imports
try:
    from .config import LLM_CONFIG, AGENT_BEHAVIOR, SELENIUM_CONFIG
    from .llm_client import LLMClient
    from .page_analyzer import PageAnalyzer
    from .element_finder import ElementFinder
    from .action_executor import ActionExecutor
    from .prompts import TaskPrompts, ActionPrompts, VerificationPrompts
    from .types import ActionPlan, StepResult
    from .utils import get_logger
except ImportError:
    # Fallback for direct module loading
    import sys
    import os
    import importlib.util
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load local modules explicitly to avoid conflicts with stdlib
    def _load_local_module(name, filename, unique_name=None):
        unique_name = unique_name or name
        spec = importlib.util.spec_from_file_location(unique_name, os.path.join(current_dir, filename))
        module = importlib.util.module_from_spec(spec)
        sys.modules[unique_name] = module
        spec.loader.exec_module(module)
        return module
    
    # Load modules in dependency order
    # Use unique names for modules that conflict with stdlib
    config_module = _load_local_module("config", "config.py")
    utils_module = _load_local_module("utils", "utils.py")
    types_module = _load_local_module("types", "types.py", "agentic_types")
    prompts_module = _load_local_module("prompts", "prompts.py")
    llm_client_module = _load_local_module("llm_client", "llm_client.py")
    page_analyzer_module = _load_local_module("page_analyzer", "page_analyzer.py")
    action_executor_module = _load_local_module("action_executor", "action_executor.py")
    element_finder_module = _load_local_module("element_finder", "element_finder.py")
    
    LLM_CONFIG = config_module.LLM_CONFIG  # type: ignore
    AGENT_BEHAVIOR = config_module.AGENT_BEHAVIOR  # type: ignore
    SELENIUM_CONFIG = config_module.SELENIUM_CONFIG  # type: ignore
    LLMClient = llm_client_module.LLMClient  # type: ignore
    PageAnalyzer = page_analyzer_module.PageAnalyzer  # type: ignore
    ElementFinder = element_finder_module.ElementFinder  # type: ignore
    ActionExecutor = action_executor_module.ActionExecutor  # type: ignore
    TaskPrompts = prompts_module.TaskPrompts  # type: ignore
    ActionPrompts = prompts_module.ActionPrompts  # type: ignore
    VerificationPrompts = prompts_module.VerificationPrompts  # type: ignore
    ActionPlan = types_module.ActionPlan  # type: ignore
    StepResult = types_module.StepResult  # type: ignore
    get_logger = utils_module.get_logger  # type: ignore


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
        self.logger = get_logger("AGENT", enabled=verbose)
        self.page_analyzer = PageAnalyzer(driver, verbose=verbose)
        self.element_finder = ElementFinder(driver, llm_client, verbose=verbose)
        self.action_executor = ActionExecutor(driver, verbose=verbose)
        self.execution_history: List[StepResult] = []
        self._action_sleep = SELENIUM_CONFIG.action_sleep
        self.timing_data: Dict[str, float] = {}
    
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
            self.logger.info(f"{'='*60}")
            self.logger.info(f"Task: {task}")
            self.logger.info(f"{'='*60}")
        
        # Initialize timing
        self.timing_data = {}
        overall_start = time.time()
        
        try:
            # Step 1: Understand task and create plan
            self.logger.info("Step 1: Understanding task and creating plan...")
            understand_start = time.time()
            plan = self._understand_task(task)
            self.timing_data["task_understanding"] = time.time() - understand_start
            if not plan or 'steps' not in plan:
                return {
                    "success": False,
                    "message": "Failed to create execution plan"
                }
            
            self.logger.info(f"Created plan with {len(plan['steps'])} steps")
            self.logger.info(f"Expected outcome: {plan.get('expected_outcome', 'N/A')}")
            for i, step in enumerate(plan['steps'], 1):
                details = f"{step.get('action', 'unknown')} - {step.get('target_description', 'N/A')}"
                self.logger.info(f"Plan step {i}: {details}")
            
            # Step 2: Execute each step
            completed_steps = 0
            step_timings: List[Dict[str, float]] = []
            
            for i, step in enumerate(plan['steps'], 1):
                step_start = time.time()
                step_timing = {"step_number": i}
                
                self.logger.info(f"\nStep {i}/{len(plan['steps'])}: {step.get('action', 'unknown')} - {step.get('target_description', 'N/A')}")
                
                # Get current page state
                page_analysis_start = time.time()
                page_summary = self.page_analyzer.get_page_summary()
                step_timing["page_analysis"] = time.time() - page_analysis_start
                
                # Plan specific action
                action_planning_start = time.time()
                action_plan = self._plan_action(step, page_summary)
                step_timing["action_planning"] = time.time() - action_planning_start
                
                if not action_plan:
                    self.logger.warn("Could not plan action for this step")
                    step_timing["total"] = time.time() - step_start
                    step_timings.append(step_timing)
                    continue
                
                self.logger.info(
                    f"Action plan: {action_plan.action} via {action_plan.selector_type or 'n/a'}={action_plan.selector_value}"
                )
                if action_plan.value:
                    self.logger.info(f"Value: {action_plan.value}")
                
                # Execute action
                action_execution_start = time.time()
                result = self.action_executor.execute_action(action_plan)
                step_timing["action_execution"] = time.time() - action_execution_start
                step_timing["total"] = time.time() - step_start
                
                self.execution_history.append(
                    StepResult(
                        step_number=i,
                        description=step,
                        action_plan=action_plan,
                        success=result.get("success", False),
                        message=result.get("message", ""),
                        timing=step_timing
                    )
                )
                
                step_timings.append(step_timing)
                
                if result.get('success'):
                    completed_steps += 1
                    self.logger.info(f"✅ {result.get('message', 'Success')}")
                else:
                    self.logger.warn(f"❌ {result.get('message', 'Failed')}")
                    # Try to continue anyway
                
                # Brief pause between steps
                time.sleep(self._action_sleep)
            
            self.timing_data["step_executions"] = step_timings
            
            # Step 3: Verify completion
            verification_start = time.time()
            final_page_summary = self.page_analyzer.get_page_summary()
            verification = self._verify_completion(task, final_page_summary)
            self.timing_data["verification"] = time.time() - verification_start
            
            self.timing_data["total"] = time.time() - overall_start
            
            self.logger.info(
                f"Verification result: {verification.get('completed', False)} - {verification.get('evidence', 'N/A')}"
            )
            
            # Print timing summary
            self._print_timing_summary()
            
            return {
                "success": verification.get('completed', False) and verification.get('success', False),
                "message": verification.get('evidence', 'Task completed'),
                "steps_completed": completed_steps,
                "total_steps": len(plan['steps']),
                "timing": self.timing_data,
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
        prompt = TaskPrompts.build(task, page_summary)
        
        self.logger.info("Sending task understanding prompt to LLM...")
        
        try:
            plan = self.llm_client.complete_json(
                prompt,
                system_prompt=TaskPrompts.system,
                temperature=LLM_CONFIG.temperature_task
            )
            return plan
        except Exception as e:
            self.logger.error(f"Error understanding task: {e}")
            return None
    
    def _plan_action(self, step: Dict[str, Any], page_summary: str) -> Optional[ActionPlan]:
        """Plan specific action for a step."""
        heuristic = self._heuristic_action(step)
        if heuristic:
            heuristic.metadata["source"] = "heuristic"
            self.logger.info(f"Using heuristic action for step: {heuristic}")
            return heuristic
        
        previous_results = [h.message for h in self.execution_history[-3:]]
        
        prompt = ActionPrompts.build(step, page_summary, previous_results)
        
        self.logger.info("Sending action planning prompt to LLM...")
        if previous_results:
            self.logger.info(f"Previous results context: {previous_results}")
        
        try:
            plan_dict = self.llm_client.complete_json(
                prompt,
                system_prompt=ActionPrompts.system,
                temperature=LLM_CONFIG.temperature_action
            )
            return ActionPlan.from_dict(plan_dict)
        except Exception as e:
            self.logger.error(f"Error planning action: {e}")
            return None
    
    def _verify_completion(self, task: str, page_summary: str) -> Dict[str, Any]:
        """Verify if task was completed successfully."""
        prompt = VerificationPrompts.build(task, page_summary)
        
        try:
            verification = self.llm_client.complete_json(
                prompt,
                temperature=LLM_CONFIG.temperature_verify
            )
            return verification
        except Exception as e:
            self.logger.error(f"Error verifying completion: {e}")
            return {"completed": False, "success": False, "evidence": str(e)}

    def _heuristic_action(self, step: Dict[str, Any]) -> Optional[ActionPlan]:
        """Return a simple action plan without LLM for trivial steps."""
        action = (step.get("action") or "").strip().lower()
        target = (step.get("target_description") or "").lower()
        value = step.get("value")

        if action == "wait":
            wait_for = "page load"
            for keyword in AGENT_BEHAVIOR.heuristic_wait_keywords:
                if keyword in target:
                    wait_for = keyword
                    break
            return ActionPlan(action="wait", wait_for=wait_for, metadata={"reason": "heuristic_wait"})

        if action == "navigate" and value:
            return ActionPlan(
                action="navigate",
                selector_type="url",
                selector_value=value,
                value=value,
                metadata={"reason": "heuristic_navigate"}
            )

        return None
    
    def _print_timing_summary(self):
        """Print a summary of timing data for all steps."""
        if not self.timing_data:
            return
        
        self.logger.info("\n" + "="*60)
        self.logger.info("TIMING SUMMARY")
        self.logger.info("="*60)
        
        # Overall timing
        if "total" in self.timing_data:
            self.logger.info(f"Total execution time: {self.timing_data['total']:.2f}s")
        
        # Task understanding
        if "task_understanding" in self.timing_data:
            self.logger.info(f"Task understanding: {self.timing_data['task_understanding']:.2f}s")
        
        # Step-by-step timing
        if "step_executions" in self.timing_data:
            self.logger.info("\nStep-by-step timing:")
            total_step_time = 0.0
            for step_timing in self.timing_data["step_executions"]:
                step_num = step_timing.get("step_number", "?")
                total = step_timing.get("total", 0.0)
                page_analysis = step_timing.get("page_analysis", 0.0)
                action_planning = step_timing.get("action_planning", 0.0)
                action_execution = step_timing.get("action_execution", 0.0)
                
                total_step_time += total
                
                self.logger.info(f"  Step {step_num}:")
                self.logger.info(f"    Total: {total:.2f}s")
                if page_analysis > 0:
                    self.logger.info(f"      - Page analysis: {page_analysis:.2f}s")
                if action_planning > 0:
                    self.logger.info(f"      - Action planning: {action_planning:.2f}s")
                if action_execution > 0:
                    self.logger.info(f"      - Action execution: {action_execution:.2f}s")
            
            self.logger.info(f"\nTotal step execution time: {total_step_time:.2f}s")
        
        # Verification timing
        if "verification" in self.timing_data:
            self.logger.info(f"Verification: {self.timing_data['verification']:.2f}s")
        
        # Breakdown summary
        if "total" in self.timing_data:
            total_time = self.timing_data["total"]
            self.logger.info("\nTime breakdown:")
            if "task_understanding" in self.timing_data:
                pct = (self.timing_data["task_understanding"] / total_time) * 100
                self.logger.info(f"  Task understanding: {pct:.1f}%")
            
            if "step_executions" in self.timing_data:
                step_time = sum(s.get("total", 0) for s in self.timing_data["step_executions"])
                pct = (step_time / total_time) * 100
                self.logger.info(f"  Step execution: {pct:.1f}%")
            
            if "verification" in self.timing_data:
                pct = (self.timing_data["verification"] / total_time) * 100
                self.logger.info(f"  Verification: {pct:.1f}%")
        
        self.logger.info("="*60 + "\n")


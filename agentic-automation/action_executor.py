"""
Action Executor - Executes Selenium actions based on LLM decisions.

Translates high-level actions into Selenium commands with consistent logging.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from typing import Dict, Any, Optional, Union
import time

try:
    from .config import SELENIUM_CONFIG
    from .types import ActionPlan
    from .utils import get_logger
except ImportError:
    import sys
    import os
    import importlib.util
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Load local modules explicitly to avoid conflicts with stdlib
    def _load_local_module(name, filename, unique_name=None):
        unique_name = unique_name or name
        spec = importlib.util.spec_from_file_location(unique_name, os.path.join(current_dir, filename))
        module = importlib.util.module_from_spec(spec)
        sys.modules[unique_name] = module
        spec.loader.exec_module(module)
        return module
    
    config_module = _load_local_module("config", "config.py")
    types_module = _load_local_module("types", "types.py", "agentic_types")
    utils_module = _load_local_module("utils", "utils.py")
    
    SELENIUM_CONFIG = config_module.SELENIUM_CONFIG  # type: ignore
    ActionPlan = types_module.ActionPlan  # type: ignore
    get_logger = utils_module.get_logger  # type: ignore


class ActionExecutor:
    """Executes Selenium actions based on action plans."""

    def __init__(self, driver: WebDriver, wait_timeout: Optional[int] = None, verbose: bool = False):
        self.driver = driver
        self.wait_timeout = wait_timeout or SELENIUM_CONFIG.page_load_timeout
        self.wait = WebDriverWait(driver, self.wait_timeout)
        self.logger = get_logger("ACTION_EXECUTOR", enabled=verbose)

    def execute_action(self, action_plan: Union[ActionPlan, Dict[str, Any]]) -> Dict[str, Any]:
        if isinstance(action_plan, dict):
            action_plan = ActionPlan.from_dict(action_plan)

        action = (action_plan.action or "").lower()
        handler = {
            "click": self._execute_click,
            "type": self._execute_type,
            "select": self._execute_select,
            "navigate": self._execute_navigate,
            "wait": self._execute_wait,
            "verify": self._execute_verify,
        }.get(action)

        if not handler:
            return {"success": False, "message": f"Unknown action: {action}"}

        try:
            result = handler(action_plan)
            result["action_plan"] = action_plan.to_dict()
            return result
        except Exception as exc:
            self.logger.error(f"Error executing action {action}: {exc}")
            return {"success": False, "message": f"Error executing action: {exc}"}

    def _execute_click(self, plan: ActionPlan) -> Dict[str, Any]:
        element = self._find_element(plan)
        if not element:
            return {"success": False, "message": "Element not found"}

        try:
            modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal.show, .modal[style*='display: block']")
            if modals:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                except Exception as js_error:
                    self.logger.warn(f"JS click failed on modal overlay: {js_error}")
            else:
                try:
                    self.wait.until(EC.element_to_be_clickable(element))
                except Exception:
                    pass
                element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

        time.sleep(SELENIUM_CONFIG.action_sleep)
        modal_result = self._handle_modal_if_present()

        if plan.wait_for:
            self._wait_for_condition(plan.wait_for)

        return {
            "success": True,
            "message": f"Clicked element: {plan.selector_value or 'unknown'}"
                       + (" and handled modal" if modal_result else ""),
            "element": element
        }

    def _execute_type(self, plan: ActionPlan) -> Dict[str, Any]:
        element = self._find_element(plan)
        if not element:
            return {"success": False, "message": "Input element not found"}

        value = plan.value or ""
        element.clear()
        element.send_keys(str(value))
        return {"success": True, "message": f"Typed '{value}' into element", "element": element}

    def _execute_select(self, plan: ActionPlan) -> Dict[str, Any]:
        element = self._find_element(plan)
        if not element:
            return {"success": False, "message": "Select element not found"}

        value = plan.value or ""
        select = Select(element)
        try:
            select.select_by_visible_text(value)
        except Exception:
            try:
                select.select_by_value(value)
            except Exception:
                return {"success": False, "message": f"Could not select '{value}'"}
        return {"success": True, "message": f"Selected '{value}' in dropdown", "element": element}

    def _execute_navigate(self, plan: ActionPlan) -> Dict[str, Any]:
        url = plan.value or plan.selector_value or ""
        if not url:
            return {"success": False, "message": "No URL provided"}
        self.driver.get(url)
        time.sleep(SELENIUM_CONFIG.action_sleep)
        return {"success": True, "message": f"Navigated to {url}", "url": url}

    def _execute_wait(self, plan: ActionPlan) -> Dict[str, Any]:
        wait_for = plan.wait_for or plan.value or ""
        if wait_for:
            self._wait_for_condition(wait_for)
        return {"success": True, "message": f"Waited for: {wait_for}"}

    def _execute_verify(self, plan: ActionPlan) -> Dict[str, Any]:
        verification = plan.metadata.get("verification") if plan.metadata else None
        verification = verification or plan.value or ""
        element = self._find_element(plan)
        if element and element.is_displayed():
            return {"success": True, "message": f"Verified: {verification}", "element": element}
        return {"success": False, "message": f"Verification failed: {verification}"}

    def _find_element(self, plan: ActionPlan) -> Optional[WebElement]:
        selector_type = (plan.selector_type or "").lower()
        selector_value = plan.selector_value or ""
        if not selector_value:
            return None

        try:
            if selector_type == "id":
                return self.driver.find_element(By.ID, selector_value)
            if selector_type == "class":
                return self.driver.find_element(By.CLASS_NAME, selector_value)
            if selector_type == "xpath":
                return self.driver.find_element(By.XPATH, selector_value)
            if selector_type == "css":
                return self.driver.find_element(By.CSS_SELECTOR, selector_value)
            if selector_type in ("text", "link_text"):
                try:
                    return self.driver.find_element(By.LINK_TEXT, selector_value)
                except Exception:
                    try:
                        return self.driver.find_element(By.PARTIAL_LINK_TEXT, selector_value)
                    except Exception:
                        xpath = f"//*[contains(text(), '{selector_value}')]"
                        return self.driver.find_element(By.XPATH, xpath)
            if selector_type == "link":
                try:
                    return self.driver.find_element(By.LINK_TEXT, selector_value)
                except Exception:
                    return self.driver.find_element(By.PARTIAL_LINK_TEXT, selector_value)
            return self.driver.find_element(By.XPATH, selector_value)
        except Exception as exc:
            self.logger.warn(f"Element lookup failed ({selector_type}={selector_value}): {exc}")
            return None

    def _handle_modal_if_present(self) -> Optional[Dict[str, Any]]:
        try:
            modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal.show, .modal[style*='display: block'], .modal[class*='show']")
            if not modals:
                modals = [m for m in self.driver.find_elements(By.CSS_SELECTOR, ".modal") if m.is_displayed()]
            if not modals:
                return None

            modal = modals[0]
            confirmation_texts = ["Add to Cart", "Confirm", "OK", "Yes", "Submit",
                                  "Save", "Proceed", "Continue", "Agree", "Accept"]
            try:
                modal_content = modal.find_element(By.CLASS_NAME, "modal-content")
            except Exception:
                modal_content = modal

            buttons = modal_content.find_elements(By.TAG_NAME, "button")
            confirmation_button = None
            for btn in buttons:
                text = btn.text.strip()
                if any(term.lower() in text.lower() for term in confirmation_texts):
                    confirmation_button = btn
                    if "add to cart" in text.lower():
                        break

            if not confirmation_button:
                self.logger.warn("Modal detected but no confirmation button found")
                return None

            try:
                self.wait.until(EC.element_to_be_clickable(confirmation_button))
                confirmation_button.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", confirmation_button)

            time.sleep(SELENIUM_CONFIG.action_sleep)
            return {"success": True, "message": f"Clicked modal confirmation: {confirmation_button.text}"}
        except Exception as exc:
            self.logger.error(f"Error handling modal: {exc}")
            return None

    def _wait_for_condition(self, condition: str):
        try:
            condition_lower = condition.lower()
            if "modal" in condition_lower:
                time.sleep(SELENIUM_CONFIG.action_sleep)
            elif "page" in condition_lower or "load" in condition_lower:
                time.sleep(max(2, SELENIUM_CONFIG.action_sleep))
            else:
                time.sleep(SELENIUM_CONFIG.action_sleep)
        except Exception:
            pass


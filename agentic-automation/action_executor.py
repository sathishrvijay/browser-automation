"""
Action Executor - Executes Selenium actions based on LLM decisions.

Translates high-level actions into Selenium commands.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from typing import Dict, Any, Optional
import time


class ActionExecutor:
    """Executes Selenium actions based on action plans."""
    
    def __init__(self, driver: WebDriver, wait_timeout: int = 15, verbose: bool = False):
        """
        Initialize action executor.
        
        Args:
            driver: Selenium WebDriver instance
            wait_timeout: Default timeout for waits (seconds)
            verbose: Whether to print verbose logs
        """
        self.driver = driver
        self.wait_timeout = wait_timeout
        self.wait = WebDriverWait(driver, wait_timeout)
        self.verbose = verbose
    
    def execute_action(self, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action based on action plan from LLM.
        
        Args:
            action_plan: Dictionary with action details:
                - action: "click|type|select|navigate|wait|verify"
                - selector_type: "id|class|xpath|text|css"
                - selector_value: actual selector
                - value: value to use (if applicable)
                - wait_for: what to wait for after action
                - verification: how to verify success
        
        Returns:
            Dictionary with execution result:
                - success: bool
                - message: str
                - element: WebElement (if found)
        """
        action = action_plan.get('action', '').lower()
        
        try:
            if action == 'click':
                return self._execute_click(action_plan)
            elif action == 'type':
                return self._execute_type(action_plan)
            elif action == 'select':
                return self._execute_select(action_plan)
            elif action == 'navigate':
                return self._execute_navigate(action_plan)
            elif action == 'wait':
                return self._execute_wait(action_plan)
            elif action == 'verify':
                return self._execute_verify(action_plan)
            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {action}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}"
            }
    
    def _execute_click(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute click action."""
        if self.verbose:
            print(f"[ACTION_EXECUTOR] Finding element to click...")
        element = self._find_element(plan)
        if not element:
            if self.verbose:
                print(f"[ACTION_EXECUTOR] ❌ Element not found")
            return {"success": False, "message": "Element not found"}
        
        if self.verbose:
            print(f"[ACTION_EXECUTOR] Element found: {element.tag_name}")
            print(f"[ACTION_EXECUTOR] Element text: {element.text[:50] if element.text else 'N/A'}")
        
        # Check if modal is blocking - if so, close it first or use JavaScript
        try:
            # Check for blocking modals
            modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal.show, .modal[style*='display: block']")
            if modals:
                if self.verbose:
                    print(f"[ACTION_EXECUTOR] ⚠️  Modal detected, attempting to close or use JavaScript click")
                # Try JavaScript click to bypass modal overlay
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    if self.verbose:
                        print(f"[ACTION_EXECUTOR] Used JavaScript click to bypass modal")
                except:
                    # If JS click fails, try regular click
                    pass
            else:
                # Wait for element to be clickable
                try:
                    self.wait.until(EC.element_to_be_clickable(element))
                except:
                    pass
                
                element.click()
                if self.verbose:
                    print(f"[ACTION_EXECUTOR] Clicked element using Selenium")
        except Exception as e:
            # Fallback to JavaScript click
            if self.verbose:
                print(f"[ACTION_EXECUTOR] Regular click failed, trying JavaScript: {e}")
            try:
                self.driver.execute_script("arguments[0].click();", element)
                if self.verbose:
                    print(f"[ACTION_EXECUTOR] ✅ Clicked using JavaScript")
            except Exception as js_e:
                if self.verbose:
                    print(f"[ACTION_EXECUTOR] ❌ JavaScript click also failed: {js_e}")
                return {"success": False, "message": f"Click failed: {str(js_e)}"}
        
        # After clicking, check if a modal appeared and handle it
        import time
        time.sleep(0.5)  # Brief wait for modal to appear
        
        modal_result = self._handle_modal_if_present()
        if modal_result:
            if self.verbose:
                print(f"[ACTION_EXECUTOR] Modal handled: {modal_result.get('message', 'N/A')}")
        
        # Wait for any specified condition
        if plan.get('wait_for'):
            if self.verbose:
                print(f"[ACTION_EXECUTOR] Waiting for: {plan.get('wait_for')}")
            self._wait_for_condition(plan['wait_for'])
        
        return {
            "success": True,
            "message": f"Clicked element: {plan.get('selector_value', 'unknown')}" + 
                      (f" and handled modal" if modal_result else ""),
            "element": element
        }
    
    def _execute_type(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute type/input action."""
        if self.verbose:
            print(f"[ACTION_EXECUTOR] Finding input element...")
        element = self._find_element(plan)
        if not element:
            if self.verbose:
                print(f"[ACTION_EXECUTOR] ❌ Input element not found")
            return {"success": False, "message": "Input element not found"}
        
        value = plan.get('value', '')
        if self.verbose:
            print(f"[ACTION_EXECUTOR] Typing '{value}' into element")
        element.clear()
        element.send_keys(str(value))
        
        if self.verbose:
            print(f"[ACTION_EXECUTOR] ✅ Typed value")
        
        return {
            "success": True,
            "message": f"Typed '{value}' into element",
            "element": element
        }
    
    def _execute_select(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute select/dropdown action."""
        element = self._find_element(plan)
        if not element:
            return {"success": False, "message": "Select element not found"}
        
        value = plan.get('value', '')
        select = Select(element)
        
        # Try to select by visible text first
        try:
            select.select_by_visible_text(value)
        except:
            try:
                select.select_by_value(value)
            except:
                return {"success": False, "message": f"Could not select '{value}'"}
        
        return {
            "success": True,
            "message": f"Selected '{value}' in dropdown",
            "element": element
        }
    
    def _execute_navigate(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute navigation action."""
        url = plan.get('value') or plan.get('selector_value', '')
        if not url:
            return {"success": False, "message": "No URL provided"}
        
        self.driver.get(url)
        time.sleep(1)  # Brief wait for page load
        
        return {
            "success": True,
            "message": f"Navigated to {url}",
            "url": url
        }
    
    def _execute_wait(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wait action."""
        wait_for = plan.get('wait_for') or plan.get('value', '')
        if wait_for:
            self._wait_for_condition(wait_for)
        
        return {
            "success": True,
            "message": f"Waited for: {wait_for}"
        }
    
    def _execute_verify(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute verification action."""
        verification = plan.get('verification') or plan.get('value', '')
        element = self._find_element(plan)
        
        if element and element.is_displayed():
            return {
                "success": True,
                "message": f"Verified: {verification}",
                "element": element
            }
        else:
            return {
                "success": False,
                "message": f"Verification failed: {verification}"
            }
    
    def _find_element(self, plan: Dict[str, Any]) -> Optional[WebElement]:
        """Find element using selector from plan."""
        selector_type = plan.get('selector_type', '').lower()
        selector_value = plan.get('selector_value', '')
        
        if not selector_value:
            if self.verbose:
                print(f"[ACTION_EXECUTOR] No selector value provided")
            return None
        
        if self.verbose:
            print(f"[ACTION_EXECUTOR] Finding element: {selector_type}={selector_value}")
        
        try:
            if selector_type == 'id':
                element = self.driver.find_element(By.ID, selector_value)
            elif selector_type == 'class':
                element = self.driver.find_element(By.CLASS_NAME, selector_value)
            elif selector_type == 'xpath':
                element = self.driver.find_element(By.XPATH, selector_value)
            elif selector_type == 'css':
                element = self.driver.find_element(By.CSS_SELECTOR, selector_value)
            elif selector_type == 'text' or selector_type == 'link_text':
                # Find by text content - try link first, then any element
                try:
                    element = self.driver.find_element(By.LINK_TEXT, selector_value)
                except:
                    # Fallback to partial link text or XPath
                    try:
                        element = self.driver.find_element(By.PARTIAL_LINK_TEXT, selector_value)
                    except:
                        element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{selector_value}')]")
            elif selector_type == 'link':
                # Try link text
                try:
                    element = self.driver.find_element(By.LINK_TEXT, selector_value)
                except:
                    element = self.driver.find_element(By.PARTIAL_LINK_TEXT, selector_value)
            else:
                # Try XPath as fallback
                element = self.driver.find_element(By.XPATH, selector_value)
            
            if self.verbose and element:
                print(f"[ACTION_EXECUTOR] ✅ Element found: {element.tag_name}")
            return element
        except Exception as e:
            if self.verbose:
                print(f"[ACTION_EXECUTOR] ❌ Element not found: {e}")
            return None
    
    def _handle_modal_if_present(self) -> Optional[Dict[str, Any]]:
        """
        Check if a modal appeared after an action and handle it.
        
        Returns:
            Dictionary with result if modal was handled, None otherwise
        """
        try:
            # Check for visible modals
            modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal.show, .modal[style*='display: block'], .modal[class*='show']")
            
            if not modals:
                # Also check for modals with display: block in inline style
                modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal")
                modals = [m for m in modals if m.is_displayed()]
            
            if modals:
                modal = modals[0]  # Handle first visible modal
                if self.verbose:
                    print(f"[ACTION_EXECUTOR] ⚠️  Modal detected after click, looking for confirmation button...")
                
                # Look for confirmation buttons inside the modal
                # Common confirmation button texts
                confirmation_texts = [
                    "Add to Cart", "Confirm", "OK", "Yes", "Submit", 
                    "Save", "Proceed", "Continue", "Agree", "Accept"
                ]
                
                # Try to find confirmation button in modal
                modal_content = None
                try:
                    modal_content = modal.find_element(By.CLASS_NAME, "modal-content")
                except:
                    modal_content = modal
                
                if modal_content:
                    # Look for buttons with confirmation text
                    buttons = modal_content.find_elements(By.TAG_NAME, "button")
                    confirmation_button = None
                    
                    for btn in buttons:
                        btn_text = btn.text.strip()
                        if any(confirm_text.lower() in btn_text.lower() for confirm_text in confirmation_texts):
                            # Prefer "Add to Cart" if it's an add to cart modal
                            if "add to cart" in btn_text.lower():
                                confirmation_button = btn
                                break
                            elif not confirmation_button:  # Take first match otherwise
                                confirmation_button = btn
                    
                    if confirmation_button:
                        if self.verbose:
                            print(f"[ACTION_EXECUTOR] Found confirmation button: '{confirmation_button.text}'")
                        
                        # Click the confirmation button
                        try:
                            # Wait for button to be clickable
                            self.wait.until(EC.element_to_be_clickable(confirmation_button))
                            confirmation_button.click()
                            if self.verbose:
                                print(f"[ACTION_EXECUTOR] ✅ Clicked modal confirmation button")
                            
                            # Wait a bit for modal to close
                            time.sleep(0.5)
                            
                            return {
                                "success": True,
                                "message": f"Clicked modal confirmation: {confirmation_button.text}"
                            }
                        except Exception as e:
                            # Try JavaScript click as fallback
                            try:
                                self.driver.execute_script("arguments[0].click();", confirmation_button)
                                if self.verbose:
                                    print(f"[ACTION_EXECUTOR] ✅ Clicked modal confirmation using JavaScript")
                                time.sleep(0.5)
                                return {
                                    "success": True,
                                    "message": f"Clicked modal confirmation (JS): {confirmation_button.text}"
                                }
                            except Exception as js_e:
                                if self.verbose:
                                    print(f"[ACTION_EXECUTOR] ❌ Failed to click modal button: {js_e}")
                                return None
                    else:
                        if self.verbose:
                            print(f"[ACTION_EXECUTOR] ⚠️  Modal detected but no confirmation button found")
                            print(f"[ACTION_EXECUTOR] Available buttons: {[b.text for b in buttons]}")
                else:
                    if self.verbose:
                        print(f"[ACTION_EXECUTOR] ⚠️  Modal detected but couldn't find modal-content")
            
            return None
        except Exception as e:
            if self.verbose:
                print(f"[ACTION_EXECUTOR] Error checking for modal: {e}")
            return None
    
    def _wait_for_condition(self, condition: str):
        """Wait for a condition to be met."""
        try:
            if 'modal' in condition.lower():
                # Wait for modal to appear or disappear
                time.sleep(1)
            elif 'page' in condition.lower() or 'load' in condition.lower():
                # Wait for page load
                time.sleep(2)
            else:
                # Generic wait
                time.sleep(1)
        except:
            pass


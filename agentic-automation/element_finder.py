"""
Element Finder - Uses LLM to find elements by semantic meaning.

Dynamically locates page elements based on user intent rather than hardcoded selectors.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from typing import List, Dict, Any, Optional

# Handle both relative and absolute imports
try:
    from .page_analyzer import PageAnalyzer
    from .llm_client import LLMClient
    from .prompts import ElementPrompts
    from .utils import get_logger
except ImportError:
    # Fallback for direct module loading
    import sys
    import os
    import importlib.util
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load local modules explicitly to avoid conflicts
    def _load_local_module(name, filename):
        spec = importlib.util.spec_from_file_location(name, os.path.join(current_dir, filename))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    
    page_analyzer_module = _load_local_module("page_analyzer", "page_analyzer.py")
    llm_client_module = _load_local_module("llm_client", "llm_client.py")
    prompts_module = _load_local_module("prompts", "prompts.py")
    utils_module = _load_local_module("utils", "utils.py")
    
    PageAnalyzer = page_analyzer_module.PageAnalyzer  # type: ignore
    LLMClient = llm_client_module.LLMClient  # type: ignore
    ElementPrompts = prompts_module.ElementPrompts  # type: ignore
    get_logger = utils_module.get_logger  # type: ignore


class ElementFinder:
    """Finds elements on a page using semantic understanding."""
    
    def __init__(self, driver: WebDriver, llm_client: LLMClient, verbose: bool = False):
        """
        Initialize element finder.
        
        Args:
            driver: Selenium WebDriver instance
            llm_client: LLM client for semantic matching
            verbose: Whether to print verbose logs
        """
        self.driver = driver
        self.llm_client = llm_client
        self.verbose = verbose
        self.logger = get_logger("ELEMENT_FINDER", enabled=verbose)
        self.page_analyzer = PageAnalyzer(driver, verbose=verbose)
    
    def find_element_by_intent(self, intent: str, element_type: Optional[str] = None) -> Any:
        """
        Find an element based on user intent.
        
        Args:
            intent: What the user wants to do (e.g., "add to cart button")
            element_type: Optional filter for element type (button, input, link, etc.)
            
        Returns:
            Selenium WebElement or None
        """
        self.logger.info(f"Finding element by intent: '{intent}'")
        
        # Analyze current page
        analysis = self.page_analyzer.analyze()
        
        # Filter by element type if specified
        elements = analysis['elements']
        if element_type:
            elements = [e for e in elements if element_type in e['type']]
            self.logger.info(f"Filtered to {len(elements)} {element_type} elements")
        
        if not elements:
            self.logger.warn("No elements available for matching")
            return None
        
        # Use LLM to find matching element
        prompt = ElementPrompts.build(intent, elements)
        self.logger.info("Sending element finding prompt to LLM...")
        
        try:
            result = self.llm_client.complete_json(
                prompt,
                system_prompt=ElementPrompts.system,
                temperature=0.2
            )
            
            # Get best match
            matched_elements = result.get('matched_elements', [])
            if not matched_elements:
                self.logger.warn("LLM found no matching elements")
                return None
            
            best_match_idx = result.get('best_match', 0)
            match = matched_elements[best_match_idx]
            
            self.logger.info(
                f"Best match: {match.get('selector_strategy')}={match.get('selector_value')} "
                f"(confidence {match.get('confidence', 'N/A')})"
            )
            
            # Find element using selector strategy
            element = self._find_element_by_selector(
                match['selector_strategy'],
                match['selector_value'],
                match.get('index')
            )
            
            if element:
                self.logger.info("✅ Element found")
            else:
                self.logger.warn("❌ Element not found with selector from LLM")
            
            return element
        except Exception as e:
            self.logger.error(f"Error finding element: {e}")
            return None
    
    def find_elements_by_intent(self, intent: str, element_type: Optional[str] = None) -> List[Any]:
        """
        Find multiple elements based on user intent.
        
        Args:
            intent: What the user wants to find (e.g., "all product cards")
            element_type: Optional filter for element type
            
        Returns:
            List of Selenium WebElements
        """
        analysis = self.page_analyzer.analyze()
        elements = analysis['elements']
        
        if element_type:
            elements = [e for e in elements if element_type in e['type']]
        
        if not elements:
            return []
        
        prompt = ElementPrompts.build(intent, elements)
        try:
            result = self.llm_client.complete_json(
                prompt,
                system_prompt=ElementPrompts.system,
                temperature=0.2
            )
            
            matched_elements = result.get('matched_elements', [])
            found_elements = []
            
            for match in matched_elements:
                elem = self._find_element_by_selector(
                    match['selector_strategy'],
                    match['selector_value'],
                    match.get('index')
                )
                if elem:
                    found_elements.append(elem)
            
            return found_elements
        except Exception as e:
            self.logger.error(f"Error finding elements: {e}")
            return []
    
    def _find_element_by_selector(self, strategy: str, value: str, index: Optional[int] = None) -> Any:
        """
        Find element using specified selector strategy.
        
        Args:
            strategy: Selector type (id, class, xpath, text, css)
            value: Selector value
            index: Optional index if multiple matches
            
        Returns:
            Selenium WebElement or None
        """
        try:
            if strategy == "id" and value:
                return self.driver.find_element(By.ID, value)
            
            elif strategy == "class" and value:
                elements = self.driver.find_elements(By.CLASS_NAME, value)
                if index is not None and index < len(elements):
                    return elements[index]
                return elements[0] if elements else None
            
            elif strategy == "xpath" and value:
                return self.driver.find_element(By.XPATH, value)
            
            elif strategy == "text":
                # Find by text content
                xpath = f"//*[contains(text(), '{value}')]"
                elements = self.driver.find_elements(By.XPATH, xpath)
                if index is not None and index < len(elements):
                    return elements[index]
                return elements[0] if elements else None
            
            elif strategy == "css" and value:
                return self.driver.find_element(By.CSS_SELECTOR, value)
            
            else:
                # Fallback: try to find by text containing the value
                xpath = f"//*[contains(text(), '{value}')]"
                elements = self.driver.find_elements(By.XPATH, xpath)
                if elements:
                    return elements[0] if index is None else elements[index]
                
        except Exception as e:
            self.logger.error(f"Error using selector {strategy}={value}: {e}")
        
        return None


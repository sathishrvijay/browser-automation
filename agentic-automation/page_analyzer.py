"""
Page Analyzer - Extracts page structure and interactive elements.

Analyzes web pages to create a simplified representation for LLM understanding.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from typing import List, Dict, Any
import json


class PageAnalyzer:
    """Analyzes web pages and extracts interactive elements."""
    
    def __init__(self, driver: WebDriver, verbose: bool = False):
        """
        Initialize page analyzer.
        
        Args:
            driver: Selenium WebDriver instance
            verbose: Whether to print verbose logs
        """
        self.driver = driver
        self.verbose = verbose
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze current page and extract structure.
        
        Returns:
            Dictionary with page information:
            - url: Current page URL
            - title: Page title
            - elements: List of interactive elements
            - structure: Simplified page structure
        """
        if self.verbose:
            print(f"[PAGE_ANALYZER] Analyzing page: {self.driver.current_url}")
        
        elements = self._extract_interactive_elements()
        
        if self.verbose:
            print(f"[PAGE_ANALYZER] Found {len(elements)} interactive elements")
            for elem in elements[:5]:  # Show first 5
                print(f"  - {elem['type']}: {elem.get('description', 'N/A')[:60]}")
            if len(elements) > 5:
                print(f"  ... and {len(elements) - 5} more")
        
        return {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "elements": elements,
            "structure": self._extract_structure()
        }
    
    def _extract_interactive_elements(self) -> List[Dict[str, Any]]:
        """Extract all interactive elements from the page."""
        elements = []
        
        # Find all interactive elements (including those in modals)
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        links = self.driver.find_elements(By.TAG_NAME, "a")
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        
        # Check for modals and include their elements
        try:
            modals = self.driver.find_elements(By.CSS_SELECTOR, ".modal")
            visible_modals = [m for m in modals if m.is_displayed()]
            if visible_modals and self.verbose:
                print(f"[PAGE_ANALYZER] Found {len(visible_modals)} visible modal(s)")
        except:
            pass
        
        # Process buttons
        for i, btn in enumerate(buttons):
            try:
                if btn.is_displayed():
                    elements.append({
                        "type": "button",
                        "index": i,
                        "text": btn.text.strip(),
                        "id": btn.get_attribute("id") or "",
                        "class": btn.get_attribute("class") or "",
                        "onclick": btn.get_attribute("onclick") or "",
                        "description": self._describe_element(btn)
                    })
            except:
                pass
        
        # Process inputs
        for i, inp in enumerate(inputs):
            try:
                if inp.is_displayed():
                    input_type = inp.get_attribute("type") or "text"
                    elements.append({
                        "type": f"input_{input_type}",
                        "index": i,
                        "id": inp.get_attribute("id") or "",
                        "name": inp.get_attribute("name") or "",
                        "placeholder": inp.get_attribute("placeholder") or "",
                        "value": inp.get_attribute("value") or "",
                        "label": self._find_label(inp),
                        "description": self._describe_element(inp)
                    })
            except:
                pass
        
        # Process links
        for i, link in enumerate(links):
            try:
                if link.is_displayed():
                    href = link.get_attribute("href") or ""
                    elements.append({
                        "type": "link",
                        "index": i,
                        "text": link.text.strip(),
                        "href": href,
                        "id": link.get_attribute("id") or "",
                        "class": link.get_attribute("class") or "",
                        "description": self._describe_element(link)
                    })
            except:
                pass
        
        # Process selects
        for i, sel in enumerate(selects):
            try:
                if sel.is_displayed():
                    elements.append({
                        "type": "select",
                        "index": i,
                        "id": sel.get_attribute("id") or "",
                        "name": sel.get_attribute("name") or "",
                        "options": [opt.text for opt in sel.find_elements(By.TAG_NAME, "option")],
                        "label": self._find_label(sel),
                        "description": self._describe_element(sel)
                    })
            except:
                pass
        
        return elements
    
    def _extract_structure(self) -> Dict[str, Any]:
        """Extract simplified page structure."""
        try:
            # Get main content areas
            structure = {
                "headings": [],
                "sections": []
            }
            
            # Extract headings
            for level in range(1, 7):
                headings = self.driver.find_elements(By.TAG_NAME, f"h{level}")
                for h in headings:
                    try:
                        if h.is_displayed():
                            structure["headings"].append({
                                "level": level,
                                "text": h.text.strip()
                            })
                    except:
                        pass
            
            return structure
        except:
            return {}
    
    def _describe_element(self, element) -> str:
        """Create a human-readable description of an element."""
        try:
            description_parts = []
            
            # Get text content
            text = element.text.strip()
            if text:
                description_parts.append(f"text: '{text}'")
            
            # Get nearby context (parent or sibling text)
            try:
                parent = element.find_element(By.XPATH, "..")
                parent_text = parent.text.strip()[:100]
                if parent_text and parent_text != text:
                    description_parts.append(f"context: '{parent_text[:50]}...'")
            except:
                pass
            
            # Get attributes
            element_id = element.get_attribute("id")
            element_class = element.get_attribute("class")
            
            if element_id:
                description_parts.append(f"id: {element_id}")
            if element_class:
                description_parts.append(f"class: {element_class[:50]}")
            
            return " | ".join(description_parts) if description_parts else "interactive element"
        except:
            return "interactive element"
    
    def _find_label(self, element) -> str:
        """Find associated label for input/select element."""
        try:
            element_id = element.get_attribute("id")
            if element_id:
                label = self.driver.find_element(By.XPATH, f"//label[@for='{element_id}']")
                return label.text.strip()
        except:
            pass
        
        try:
            # Try to find label as parent or previous sibling
            label = element.find_element(By.XPATH, "./preceding-sibling::label[1]")
            return label.text.strip()
        except:
            pass
        
        return ""
    
    def get_page_summary(self) -> str:
        """
        Get a text summary of the page for LLM consumption.
        
        Returns:
            Formatted string describing the page
        """
        analysis = self.analyze()
        
        summary = f"Page: {analysis['title']}\n"
        summary += f"URL: {analysis['url']}\n\n"
        
        if analysis['structure']['headings']:
            summary += "Headings:\n"
            for h in analysis['structure']['headings']:
                summary += f"  {'#' * h['level']} {h['text']}\n"
            summary += "\n"
        
        summary += f"Interactive Elements ({len(analysis['elements'])}):\n"
        for elem in analysis['elements']:
            summary += f"  - {elem['type']}: {elem['description']}\n"
        
        return summary


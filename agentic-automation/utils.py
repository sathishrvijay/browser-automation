"""
Utility functions for agentic automation.
"""

from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional
import time


def wait_for_page_load(driver: WebDriver, timeout: int = 10):
    """Wait for page to finish loading."""
    time.sleep(1)  # Brief initial wait
    # Additional wait can be added based on specific conditions


def get_element_text_safe(element) -> str:
    """Safely get text from an element."""
    try:
        return element.text.strip()
    except:
        return ""


def safe_find_element(driver: WebDriver, by, value) -> Optional[any]:
    """Safely find an element, returning None if not found."""
    try:
        return driver.find_element(by, value)
    except:
        return None


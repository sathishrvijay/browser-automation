"""
Utility helpers for agentic automation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import time

from selenium.webdriver.remote.webdriver import WebDriver

try:
    from .config import LOGGING_CONFIG
except ImportError:
    import sys
    import os
    import importlib.util
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load local config module explicitly to avoid conflicts
    spec = importlib.util.spec_from_file_location("config", os.path.join(current_dir, "config.py"))
    config_module = importlib.util.module_from_spec(spec)
    sys.modules["config"] = config_module
    spec.loader.exec_module(config_module)
    LOGGING_CONFIG = config_module.LOGGING_CONFIG  # type: ignore


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


@dataclass
class Logger:
    """Simple stdout logger used across modules."""

    name: str
    enabled: bool = True
    show_time: bool = LOGGING_CONFIG.show_timestamp

    def _log(self, level: str, message: str):
        if not (LOGGING_CONFIG.enabled and self.enabled):
            return
        parts = []
        if self.show_time:
            parts.append(datetime.now().strftime("%H:%M:%S"))
        parts.append(f"[{self.name}]")
        parts.append(level.upper())
        print(" ".join(parts), message)

    def info(self, message: str):
        self._log("info", message)

    def warn(self, message: str):
        self._log("warn", message)

    def error(self, message: str):
        self._log("error", message)


def get_logger(name: str, enabled: bool = True) -> Logger:
    return Logger(name=name, enabled=enabled)


"""
LLM Client for agentic automation.

Handles API calls to LLM providers (OpenAI, Anthropic, etc.)
"""

import os
from typing import Optional, Dict, Any
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


try:
    from .config import LLM_CONFIG
    from .utils import get_logger
except ImportError:
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
    
    config_module = _load_local_module("config", "config.py")
    utils_module = _load_local_module("utils", "utils.py")
    
    LLM_CONFIG = config_module.LLM_CONFIG  # type: ignore
    get_logger = utils_module.get_logger  # type: ignore


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None, 
                 api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider ("openai", "anthropic", etc.)
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: API key (if None, reads from environment)
            verbose: Whether to print verbose logs
        """
        self.provider = provider or LLM_CONFIG.provider
        self.model = model or LLM_CONFIG.model
        self.logger = get_logger("LLM", enabled=verbose)
        
        if provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Run: pip install openai")
            
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
            
            self.client = OpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def complete(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.3, max_tokens: int = 2000) -> str:
        """
        Get completion from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (0-1, lower = more deterministic)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        self.logger.info(f"Calling {self.model} (temp={temperature})")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            result = response.choices[0].message.content
            
            self.logger.info(f"LLM response preview: {result[:120]}...")
            
            return result
        except Exception as e:
            self.logger.error(f"LLM API error: {e}")
            raise RuntimeError(f"LLM API error: {str(e)}")
    
    def complete_json(self, prompt: str, system_prompt: Optional[str] = None,
                      temperature: float = 0.1) -> Dict[str, Any]:
        """
        Get JSON response from LLM.
        
        Args:
            prompt: User prompt requesting JSON
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (lower for more deterministic JSON)
            
        Returns:
            Parsed JSON dictionary
        """
        json_prompt = prompt + "\n\nRespond with valid JSON only, no additional text."
        response = self.complete(json_prompt, system_prompt, temperature=temperature)
        
        # Try to extract JSON from response
        try:
            # Look for JSON in code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            parsed = json.loads(json_str)
            
            self.logger.info(f"Parsed JSON preview: {str(parsed)[:120]}...")
            
            return parsed
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}. Raw response: {response[:200]}")
            raise ValueError(f"Failed to parse JSON from LLM response: {response[:200]}... Error: {e}")


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


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4", 
                 api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider ("openai", "anthropic", etc.)
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: API key (if None, reads from environment)
            verbose: Whether to print verbose logs
        """
        self.provider = provider
        self.model = model
        self.verbose = verbose
        
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
        
        if self.verbose:
            print(f"\n[LLM] Calling {self.model}...")
            if system_prompt:
                print(f"[LLM] System prompt: {system_prompt[:100]}...")
            print(f"[LLM] User prompt: {prompt[:200]}...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            result = response.choices[0].message.content
            
            if self.verbose:
                print(f"[LLM] Response: {result[:200]}...")
            
            return result
        except Exception as e:
            if self.verbose:
                print(f"[LLM] Error: {e}")
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
            
            if self.verbose:
                print(f"[LLM] Parsed JSON: {str(parsed)[:200]}...")
            
            return parsed
        except json.JSONDecodeError as e:
            if self.verbose:
                print(f"[LLM] JSON parse error: {e}")
                print(f"[LLM] Raw response: {response[:500]}")
            raise ValueError(f"Failed to parse JSON from LLM response: {response[:200]}... Error: {e}")


"""
Example usage: Add 1 laptop to cart using agentic automation.

This demonstrates how to use the agentic automation system with natural language.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
import argparse

# Add agentic-automation directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
agentic_dir = os.path.dirname(current_dir)  # agentic-automation directory
sys.path.insert(0, agentic_dir)

# Import modules using importlib to handle hyphenated folder name
import importlib.util

def load_module(module_name, file_path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    # Add to sys.modules so other modules can import it
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load modules in dependency order
config_module = load_module("config", os.path.join(agentic_dir, "config.py"))
prompts_module = load_module("prompts", os.path.join(agentic_dir, "prompts.py"))
llm_module = load_module("llm_client", os.path.join(agentic_dir, "llm_client.py"))
page_analyzer_module = load_module("page_analyzer", os.path.join(agentic_dir, "page_analyzer.py"))
action_executor_module = load_module("action_executor", os.path.join(agentic_dir, "action_executor.py"))
element_finder_module = load_module("element_finder", os.path.join(agentic_dir, "element_finder.py"))
agent_module = load_module("agent", os.path.join(agentic_dir, "agent.py"))

# Extract classes
AgenticAgent = agent_module.AgenticAgent
LLMClient = llm_module.LLMClient
SELENIUM_CONFIG = config_module.SELENIUM_CONFIG
LLM_CONFIG = config_module.LLM_CONFIG


def setup_driver():
    """Initialize Chrome WebDriver."""
    service = Service(ChromeDriverManager().install())
    options = Options()
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'normal'
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(SELENIUM_CONFIG.page_load_timeout)
    driver.implicitly_wait(SELENIUM_CONFIG.implicit_wait)
    
    return driver


def main():
    """Main example: Add 1 laptop to cart."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Agentic automation example")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    args = parser.parse_args()
    
    driver = None
    
    try:
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set it with: export OPENAI_API_KEY='your-key-here'")
            return
        
        print("Setting up browser and agent...")
        driver = setup_driver()
        
        # Initialize LLM client
        llm_client = LLMClient(provider=LLM_CONFIG.provider, model=LLM_CONFIG.model, verbose=args.verbose)
        
        # Initialize agent
        agent = AgenticAgent(driver, llm_client, verbose=args.verbose)
        
        # Navigate to product catalog
        print("\nNavigating to product catalog...")
        driver.get("http://localhost:8001/index.html")
        import time
        time.sleep(2)  # Wait for page to load
        
        # Execute task using natural language
        task = "Add 1 laptop to the cart for checkout"
        result = agent.execute(task)
        
        # Print results
        print("\n" + "="*60)
        print("EXECUTION RESULTS")
        print("="*60)
        print(f"Success: {result['success']}")
        print(f"Message: {result['message']}")
        print(f"Steps completed: {result['steps_completed']}/{result.get('total_steps', '?')}")
        print(f"Final URL: {result['final_state']['url']}")
        print(f"Final page: {result['final_state']['title']}")
        
        if result['success']:
            print("\n✅ Task completed successfully!")
        else:
            print("\n❌ Task did not complete successfully.")
            print("Check the logs above for details.")
        
        # Keep browser open for a few seconds to see result
        print("\nKeeping browser open for 5 seconds...")
        time.sleep(5)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()


if __name__ == "__main__":
    main()


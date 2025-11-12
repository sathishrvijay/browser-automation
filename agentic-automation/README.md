# Agentic Automation System

A general-purpose LLM-powered browser automation system that executes natural language instructions on any website without hardcoded selectors or prior knowledge of page structure.

## Goal

Enable browser automation using only natural language. Instead of writing code like `driver.find_element(By.ID, "addToCart").click()`, simply say **"Add 1 laptop to the cart for checkout"** and the system will:
- Understand the task
- Analyze the page dynamically
- Find elements by semantic meaning
- Execute actions automatically
- Verify completion

## Quick Start

### 1. Set Up API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 2. Start the Test Website

In a separate terminal:
```bash
cd ../websites/product-catalog
source ../../bauto-venv/bin/activate
python server.py
```

### 3. Run the Example

```bash
cd examples
source ../../bauto-venv/bin/activate

# Run with verbose logging
python product_catalog_example.py --verbose

# Or run quietly
python product_catalog_example.py
```

## How It Works

1. **Task Understanding**: LLM breaks down natural language into actionable steps
2. **Page Analysis**: System extracts all interactive elements and page structure
3. **Element Finding**: LLM matches user intent to page elements semantically
4. **Action Execution**: Selenium actions are executed based on LLM decisions
5. **Verification**: System confirms task completion

## Architecture

- **`agent.py`** - Main orchestrator
- **`llm_client.py`** - OpenAI API integration
- **`page_analyzer.py`** - Page structure extraction
- **`element_finder.py`** - Semantic element finding
- **`action_executor.py`** - Selenium action execution
- **`prompts.py`** - LLM prompt templates

## Example Usage

```python
from selenium import webdriver
from agentic_automation.agent import AgenticAgent
from agentic_automation.llm_client import LLMClient

driver = webdriver.Chrome()
llm_client = LLMClient(provider="openai", model="gpt-4")
agent = AgenticAgent(driver, llm_client, verbose=True)

driver.get("http://localhost:8001/index.html")
result = agent.execute("Add 1 laptop to the cart for checkout")

print(f"Success: {result['success']}")
```

## Key Features

- ✅ **No hardcoded selectors** - Works on any website
- ✅ **Natural language** - Plain English instructions
- ✅ **Automatic modal handling** - Detects and handles popups
- ✅ **Self-verifying** - Confirms task completion
- ✅ **Verbose logging** - See exactly what's happening with `--verbose`

## Performance Note

The system makes multiple LLM API calls (one per step), which adds latency (~30-60 seconds for complex tasks). This is expected for a proof-of-concept. Production optimizations would include:
- Batch planning (plan multiple steps at once)
- Caching page analysis
- Skipping LLM calls for simple actions

## Requirements

- Python 3.7+
- OpenAI API key
- Dependencies: `selenium`, `webdriver-manager`, `openai` (see `../requirements.txt`)


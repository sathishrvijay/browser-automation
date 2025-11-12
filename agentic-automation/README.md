# Agentic Automation System

A general-purpose LLM-powered browser automation system that can execute natural language instructions on any website without hardcoded selectors or prior knowledge of page structure.

## Overview

This system uses Large Language Models (LLMs) to:
- Understand natural language tasks
- Dynamically analyze web pages
- Find elements by semantic meaning (not hardcoded selectors)
- Plan and execute actions
- Verify task completion

## Architecture

### Core Components

1. **LLM Client** (`llm_client.py`) - Handles API calls to LLM providers (OpenAI, etc.)
2. **Page Analyzer** (`page_analyzer.py`) - Extracts page structure and interactive elements
3. **Element Finder** (`element_finder.py`) - Uses LLM to find elements by semantic meaning
4. **Action Executor** (`action_executor.py`) - Executes Selenium actions based on LLM decisions
5. **Main Agent** (`agent.py`) - Orchestrates the full automation flow

### Flow

```
User Instruction → LLM Understanding → Page Analysis → Element Discovery → 
Action Planning → Selenium Execution → Verification → Result
```

## Setup

### 1. Install Dependencies

```bash
source ../bauto-venv/bin/activate
pip install -r ../requirements.txt
```

### 2. Set Up API Key

You'll need an OpenAI API key:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

### 3. Start the Test Website

In a separate terminal:
```bash
cd ../websites/product-catalog
source ../../bauto-venv/bin/activate
python server.py
```

## Usage

### Basic Example

```python
from selenium import webdriver
from agentic_automation.agent import AgenticAgent
from agentic_automation.llm_client import LLMClient

# Setup driver
driver = webdriver.Chrome()

# Initialize LLM client
llm_client = LLMClient(provider="openai", model="gpt-4")

# Initialize agent
agent = AgenticAgent(driver, llm_client)

# Navigate to website
driver.get("http://localhost:8001/index.html")

# Execute task using natural language
result = agent.execute("Add 1 laptop to the cart for checkout")

print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
```

### Run Example Script

```bash
cd examples
source ../../bauto-venv/bin/activate
python product_catalog_example.py
```

## How It Works

### 1. Task Understanding

The LLM analyzes the natural language task and breaks it down into steps:
- "Add 1 laptop to cart" →
  1. Find product listing page
  2. Identify laptop product
  3. Click on laptop
  4. Find add to cart button
  5. Set quantity to 1
  6. Confirm add to cart
  7. Verify item added

### 2. Page Analysis

The system extracts:
- All interactive elements (buttons, inputs, links)
- Element descriptions (text, context, attributes)
- Page structure (headings, sections)

### 3. Element Finding

Instead of hardcoded selectors like `By.ID("addToCart")`, the LLM finds elements by meaning:
- "button to add product to cart" → matches element with text "Add to Cart"
- "product card for laptop" → matches card containing "Laptop" text

### 4. Action Execution

The LLM plans specific Selenium actions:
- Selector strategy (ID, XPath, text, etc.)
- Action type (click, type, select, navigate)
- Values to use
- What to wait for

### 5. Verification

The system verifies task completion by checking:
- Expected outcomes are visible
- No error messages
- Page is in expected state

## Key Features

- **No Hardcoded Selectors**: Works on any website without prior knowledge
- **Natural Language**: Use plain English to describe tasks
- **Adaptive**: Handles different page layouts and structures
- **Self-Verifying**: Checks if actions succeeded
- **Error Handling**: Gracefully handles failures and retries

## Limitations

- Requires LLM API access (OpenAI API key)
- May be slower than hardcoded automation (LLM calls add latency)
- May need refinement for complex edge cases
- API costs depend on usage

## Example Tasks

- "Add 1 laptop to the cart for checkout"
- "Fill out the contact form with name John Doe and email john@example.com"
- "Search for headphones and add the first result to cart"
- "Navigate to the cart page and remove all items"

## Troubleshooting

- **API Key Error**: Make sure `OPENAI_API_KEY` is set
- **Element Not Found**: The LLM might need better context - check page analysis output
- **Task Failed**: Review the execution history to see which step failed
- **Import Errors**: Make sure you're in the virtual environment and dependencies are installed

## Future Enhancements

- Support for vision models (screenshot analysis)
- Multi-step task memory
- Better error recovery
- Support for multiple LLM providers
- Cost optimization strategies


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

### Overall Flow

```mermaid
graph TD
    A["User Instruction<br/>Add 1 laptop to cart"] --> B[Agent: Understand Task]
    B --> C[LLM: Break into Steps]
    C --> D[Step 1: Click View Details]
    D --> E[Page Analyzer: Extract Elements]
    E --> F[LLM: Plan Action]
    F --> G[Action Executor: Execute]
    G --> H{Modal Detected?}
    H -->|Yes| I[Auto-handle Modal]
    H -->|No| J[Continue]
    I --> J
    J --> K{More Steps?}
    K -->|Yes| D
    K -->|No| L[LLM: Verify Completion]
    L --> M[Return Result]
    
    style A fill:#e1f5ff
    style M fill:#d4edda
    style H fill:#fff3cd
    style I fill:#fff3cd
```

### Task Understanding Flow

```mermaid
graph LR
    A[Natural Language Task] --> B[Page Analyzer]
    B --> C[Extract Page Elements<br/>Buttons, Links, Inputs]
    C --> D[Create Page Summary]
    D --> E[LLM: Task Understanding Prompt]
    E --> F[LLM Response: JSON Plan]
    F --> G[Parse Steps Array]
    G --> H[Execution Plan<br/>Step 1: click View Details<br/>Step 2: wait page load<br/>Step 3: click Add to Cart<br/>...]
    
    style A fill:#e1f5ff
    style H fill:#d4edda
    style E fill:#fff3cd
```

### Element Finding Flow

```mermaid
graph TD
    A["User Intent<br/>Add to Cart button"] --> B[Page Analyzer]
    B --> C[Extract All Elements]
    C --> D["Create Element Descriptions<br/>Type: button<br/>Text: Add to Cart<br/>Context: near product price"]
    D --> E[LLM: Element Finding Prompt]
    E --> F[LLM: Match Intent to Elements]
    F --> G{Match Found?}
    G -->|Yes| H["Return Best Match<br/>selector_strategy: text<br/>selector_value: Add to Cart"]
    G -->|No| I[Try Alternative Approaches]
    I --> J{Alternatives?}
    J -->|Yes| F
    J -->|No| K[Return None]
    H --> L[Action Executor Uses Selector]
    
    style A fill:#e1f5ff
    style H fill:#d4edda
    style E fill:#fff3cd
    style K fill:#f8d7da
```

### Action Execution Flow

```mermaid
graph TD
    A["Action Plan<br/>action: click<br/>selector: Add to Cart"] --> B[Find Element]
    B --> C{Element Found?}
    C -->|No| D[Return Error]
    C -->|Yes| E[Wait for Clickable]
    E --> F[Execute Click]
    F --> G[Wait 0.5s]
    G --> H{Modal Detected?}
    H -->|Yes| I[Find Modal Content]
    I --> J["Search for Confirmation Buttons<br/>Add to Cart, Confirm, OK, etc."]
    J --> K{Button Found?}
    K -->|Yes| L[Click Confirmation]
    K -->|No| M[Log Warning]
    L --> N[Wait for Modal Close]
    H -->|No| O[Continue]
    M --> O
    N --> O
    O --> P["Wait for Condition<br/>if specified"]
    P --> Q[Return Success]
    
    style A fill:#e1f5ff
    style Q fill:#d4edda
    style H fill:#fff3cd
    style I fill:#fff3cd
    style D fill:#f8d7da
```

### Complete Step Execution Sequence

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant PageAnalyzer
    participant LLM
    participant ActionExecutor
    participant Browser
    
    User->>Agent: Execute(Add 1 laptop to cart)
    Agent->>PageAnalyzer: Analyze current page
    PageAnalyzer->>Browser: Extract DOM elements
    Browser-->>PageAnalyzer: Elements list
    PageAnalyzer-->>Agent: Page summary
    
    Agent->>LLM: Task understanding prompt
    LLM-->>Agent: Execution plan (7 steps)
    
    loop For each step
        Agent->>PageAnalyzer: Get page state
        PageAnalyzer-->>Agent: Current elements
        Agent->>LLM: Action planning prompt
        LLM-->>Agent: Action plan (selector, action)
        Agent->>ActionExecutor: Execute action plan
        ActionExecutor->>Browser: Find element
        Browser-->>ActionExecutor: Element found
        ActionExecutor->>Browser: Click element
        Browser-->>ActionExecutor: Clicked
        
        alt Modal appears
            ActionExecutor->>Browser: Detect modal
            Browser-->>ActionExecutor: Modal visible
            ActionExecutor->>Browser: Find confirmation button
            Browser-->>ActionExecutor: Button found
            ActionExecutor->>Browser: Click confirmation
            Browser-->>ActionExecutor: Modal closed
        end
        
        ActionExecutor-->>Agent: Step completed
    end
    
    Agent->>PageAnalyzer: Final page analysis
    PageAnalyzer-->>Agent: Final state
    Agent->>LLM: Verification prompt
    LLM-->>Agent: Task completed
    Agent-->>User: Success result
```

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


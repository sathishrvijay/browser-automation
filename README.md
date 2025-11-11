# Browser Automation

A project for exploring agentic browser task automation using Selenium. This repository contains test websites and automation scripts organized in a scalable folder structure.

## Project Structure

```
browser-automation/
├── websites/              # Test websites and web pages
│   ├── simple-form/      # Simple form test page
│   └── product-catalog/  # Product catalog with shopping cart
├── automations/          # Selenium automation scripts
│   ├── simple-form/     # Automation for simple-form website
│   └── product-catalog/ # Automation for product-catalog website
├── bauto-venv/          # Python virtual environment (created during setup)
├── requirements.txt      # Python dependencies
└── README.md
```

This structure allows for easy expansion:
- Add more websites in `websites/` (e.g., `websites/complex-app/`)
- Add corresponding automations in `automations/` (e.g., `automations/complex-app/`)

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser installed
- pip (Python package manager)

## Setup

1. **Clone or navigate to this repository:**
   ```bash
   cd browser-automation
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python3 -m venv bauto-venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source bauto-venv/bin/activate
   # On Windows:
   # bauto-venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `selenium`: Browser automation framework
   - `webdriver-manager`: Automatic ChromeDriver management

   **Note:** Make sure your virtual environment is activated (you should see `(bauto-venv)` in your terminal prompt) before installing dependencies.

## Getting Started

Each automation has its own README with specific instructions. For example:
- See `automations/simple-form/README.md` for the simple-form automation
- See `automations/product-catalog/README.md` for the product-catalog automation (multi-page, modals, tabs, shopping cart)

## Next Steps

For agentic browser automation with LLMs:

1. **Extend the automation scripts** to handle more complex scenarios
2. **Create an LLM integration layer** that:
   - Takes natural language instructions
   - Converts them to Selenium actions
   - Executes the automation
   - Reports results back
3. **Add more test websites** with different complexities
4. **Implement error handling** and retry logic
5. **Add logging and monitoring** for automation runs

## Troubleshooting

- **Import errors**: Make sure your virtual environment is activated and you've installed all requirements: `pip install -r requirements.txt`
- **ChromeDriver issues**: The `webdriver-manager` package should automatically handle ChromeDriver installation. If you encounter issues, ensure Chrome is up to date.

## Resources

- [Selenium Python Documentation](https://selenium-python.readthedocs.io/)
- [Selenium WebDriver API](https://www.selenium.dev/documentation/webdriver/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/)

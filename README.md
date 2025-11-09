# Browser Automation

A project for exploring agentic browser task automation using Selenium. This repository contains test websites and automation scripts organized in a scalable folder structure.

## Project Structure

```
browser-automation/
├── websites/              # Test websites and web pages
│   └── simple-form/      # Simple form test page
├── automations/          # Selenium automation scripts
│   └── simple-form/     # Automation for simple-form website
│       └── example_automation.py
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

## Quick Test

To quickly test the simple-form automation:

**Terminal 1 - Start server:**
```bash
source bauto-venv/bin/activate
cd websites/simple-form && python server.py
```

**Terminal 2 - Run automation:**
```bash
source bauto-venv/bin/activate
cd automations/simple-form && python example_automation.py
```

Expected result: Chrome opens, form fills automatically, submits, shows alert with form data, then closes.

## Usage

### Step 1: Activate Virtual Environment

**Important:** Always activate the virtual environment before running any scripts:

```bash
# From the project root directory
source bauto-venv/bin/activate
```

You should see `(bauto-venv)` in your terminal prompt, indicating the virtual environment is active.

### Step 2: Start the Web Server

Open **Terminal 1** and start the web server:

```bash
# Make sure virtual environment is activated
source bauto-venv/bin/activate

# Navigate to website directory and start server
cd websites/simple-form
python server.py
```

The server will start at `http://localhost:8000/`. You should see:
```
Server running at http://localhost:8000/
Serving files from: /path/to/websites/simple-form
Press Ctrl+C to stop the server
```

**Optional:** You can verify the page is working by opening `http://localhost:8000/test_page.html` in your browser manually.

### Step 3: Run the Automation Script

Open **Terminal 2** (keep Terminal 1 running the server) and run the automation:

```bash
# Make sure virtual environment is activated
source bauto-venv/bin/activate

# Navigate to automation directory and run script
cd automations/simple-form
python example_automation.py
```

The script will:
1. Open Chrome browser automatically
2. Navigate to the test page
3. Fill in the form fields
4. Submit the form
5. Close the browser

## What the Example Demonstrates

The `example_automation.py` script showcases various Selenium actions:

- **Finding elements** by ID, name, and CSS selectors
- **Filling text inputs** using `send_keys()`
- **Selecting dropdown options** using Selenium's `Select` class
- **Clicking radio buttons** using `click()`
- **Submitting forms** by clicking the submit button
- **Handling alerts** and waiting for elements to load

## Test Page Elements

The `test_page.html` includes:
- **Text inputs**: Name and Email fields
- **Dropdown**: Country selection
- **Radio buttons**: Preferred contact method (Email, Phone, SMS)
- **Submit button**: Form submission

All elements have clear IDs and names for easy Selenium targeting.

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

- **ChromeDriver issues**: The `webdriver-manager` package should automatically handle ChromeDriver installation. If you encounter issues, ensure Chrome is up to date.
- **Port already in use**: If port 8000 is busy, modify `PORT` in `server.py` to use a different port, and update `TEST_PAGE_URL` in the automation script accordingly.
- **Import errors**: Make sure your virtual environment is activated and you've installed all requirements: `pip install -r requirements.txt`

## Resources

- [Selenium Python Documentation](https://selenium-python.readthedocs.io/)
- [Selenium WebDriver API](https://www.selenium.dev/documentation/webdriver/)
- [ChromeDriver Downloads](https://chromedriver.chromium.org/)

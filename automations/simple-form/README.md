# Simple Form Automation

Automation script for the simple-form test website. This demonstrates basic Selenium browser automation with form filling, dropdown selection, and form submission.

## Quick Test

To quickly test the simple-form automation:

**Terminal 1 - Start server:**
```bash
source ../../bauto-venv/bin/activate
cd ../../websites/simple-form && python server.py
```

**Terminal 2 - Run automation:**
```bash
source ../../bauto-venv/bin/activate
cd automations/simple-form && python example_automation.py
```

Expected result: Chrome opens, form fills automatically, submits, shows alert with form data, then closes.

## Usage

### Step 1: Start the Web Server

Open **Terminal 1** and start the web server:

```bash
# Make sure virtual environment is activated
source ../../bauto-venv/bin/activate

# Navigate to website directory and start server
cd ../../websites/simple-form
python server.py
```

The server will start at `http://localhost:8000/`. You should see:
```
Server running at http://localhost:8000/
Serving files from: /path/to/websites/simple-form
Press Ctrl+C to stop the server
```

**Optional:** You can verify the page is working by opening `http://localhost:8000/test_page.html` in your browser manually.

### Step 2: Run the Automation Script

Open **Terminal 2** (keep Terminal 1 running the server) and run the automation:

```bash
# Make sure virtual environment is activated
source ../../bauto-venv/bin/activate

# Navigate to automation directory and run script
cd automations/simple-form
python example_automation.py
```

The script will:
1. Open Chrome browser automatically
2. Navigate to the test page
3. Fill in the form fields:
   - Name (text input)
   - Email (text input)
   - Country (dropdown)
   - Contact method (radio button)
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

## Troubleshooting

- **ChromeDriver issues**: The `webdriver-manager` package should automatically handle ChromeDriver installation. If you encounter issues, ensure Chrome is up to date.
- **Port already in use**: If port 8000 is busy, modify `PORT` in `websites/simple-form/server.py` to use a different port, and update `TEST_PAGE_URL` in `example_automation.py` accordingly.
- **Page not loading**: Make sure the server is running in Terminal 1 before running the automation script.
- **Import errors**: Make sure your virtual environment is activated and you've installed all requirements: `pip install -r ../../requirements.txt`


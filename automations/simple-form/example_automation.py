#!/usr/bin/env python3
"""
Basic Selenium automation example for the simple-form test page.
This script demonstrates various Selenium actions:
- Opening a webpage
- Finding elements by different selectors
- Filling text inputs
- Selecting dropdown options
- Clicking radio buttons
- Submitting forms
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL of the test page (assuming server is running)
TEST_PAGE_URL = "http://localhost:8000/test_page.html"

def setup_driver():
    """Initialize and return a Chrome WebDriver instance."""
    # Use webdriver-manager to automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # Add Chrome options to prevent hanging and improve reliability
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Set page load strategy to avoid hanging on slow pages
    # 'normal' waits for full page load, 'eager' waits for DOMContentLoaded
    options.page_load_strategy = 'normal'
    
    # Uncomment the next line to run in headless mode (no browser window)
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # Set timeouts to prevent indefinite waiting
    driver.set_page_load_timeout(30)  # Maximum time to wait for page load
    driver.implicitly_wait(10)  # Implicit wait for finding elements
    
    return driver

def main():
    """Main automation function."""
    driver = None
    try:
        # Initialize the WebDriver
        print("Setting up Chrome WebDriver...")
        driver = setup_driver()
        print("✅ WebDriver initialized")
        
        # Small delay to let browser fully initialize
        time.sleep(1)
        
        # Navigate to the test page
        print(f"Opening test page: {TEST_PAGE_URL}")
        print("Waiting for page to load...")
        
        try:
            driver.get(TEST_PAGE_URL)
            print(f"Page URL after navigation: {driver.current_url}")
            print(f"Page title: {driver.title}")
        except Exception as e:
            print(f"Warning during page load: {e}")
            print("Continuing anyway...")
        
        # Wait for the page to load with explicit wait
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "testForm")))
            print("✅ Page loaded successfully! Form element found.")
        except Exception as e:
            print(f"❌ Timeout waiting for form element: {e}")
            print(f"Current page source length: {len(driver.page_source)}")
            print(f"Current URL: {driver.current_url}")
            raise
        
        # Example 1: Fill text input by ID
        print("\n--- Example 1: Filling text input (Name) ---")
        name_input = driver.find_element(By.ID, "nameInput")
        name_input.clear()
        name_input.send_keys("John Doe")
        print(f"Entered name: {name_input.get_attribute('value')}")
        
        # Example 2: Fill text input by name attribute
        print("\n--- Example 2: Filling text input (Email) ---")
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys("john.doe@example.com")
        print(f"Entered email: {email_input.get_attribute('value')}")
        
        # Example 3: Select dropdown option
        print("\n--- Example 3: Selecting dropdown option (Country) ---")
        country_select = Select(driver.find_element(By.ID, "countrySelect"))
        country_select.select_by_visible_text("United States")
        selected_option = country_select.first_selected_option
        print(f"Selected country: {selected_option.text} (value: {selected_option.get_attribute('value')})")
        
        # Example 4: Click radio button
        print("\n--- Example 4: Clicking radio button (Contact Method) ---")
        phone_radio = driver.find_element(By.ID, "contactPhone")
        phone_radio.click()
        print(f"Selected contact method: {phone_radio.get_attribute('value')}")
        print(f"Radio button is selected: {phone_radio.is_selected()}")
        
        # Wait a moment to see the form filled
        print("\nWaiting 2 seconds before submission...")
        time.sleep(2)
        
        # Example 5: Click submit button
        print("\n--- Example 5: Clicking submit button ---")
        submit_button = driver.find_element(By.ID, "submitButton")
        submit_button.click()
        print("Form submitted!")
        
        # Wait for alert to appear (if form has JavaScript alert)
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"\nAlert message: {alert_text}")
            alert.accept()
        except:
            print("No alert detected (this is okay)")
        
        # Wait a moment before closing
        print("\nWaiting 3 seconds before closing browser...")
        time.sleep(3)
        
        print("\n✅ Automation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Always close the browser
        if driver:
            print("\nClosing browser...")
            driver.quit()

if __name__ == "__main__":
    main()


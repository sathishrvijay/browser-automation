#!/usr/bin/env python3
"""
Product Catalog automation example demonstrating:
- Multi-page navigation
- Finding elements in different DOM sections (header, main content)
- Modal handling (add to cart modal)
- Tab switching (product detail tabs)
- Dynamic content waits (cart count updates)
- Cart operations (add, update quantity, remove)
- State verification
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL of the product catalog (assuming server is running)
BASE_URL = "http://localhost:8001"

def setup_driver():
    """Initialize and return a Chrome WebDriver instance."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    
    # Chrome options for reliability
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'normal'
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    return driver

def wait_for_cart_count(driver, expected_count):
    """Wait for cart count in header to update."""
    wait = WebDriverWait(driver, 10)
    cart_count_element = wait.until(
        EC.presence_of_element_located((By.ID, "cartCount"))
    )
    wait.until(lambda d: cart_count_element.text == str(expected_count))
    return cart_count_element.text

def print_step_header(step_num, description):
    """Print a formatted step header."""
    print("=" * 60)
    print(f"STEP {step_num}: {description}")
    print("=" * 60)

def step1_navigate_to_listing(driver, wait):
    """Step 1: Navigate to product listing page."""
    print_step_header(1, "Navigate to Product Listing Page")
    listing_url = f"{BASE_URL}/index.html"
    print(f"Opening: {listing_url}")
    driver.get(listing_url)
    
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-grid")))
    print(f"✅ Page loaded: {driver.title}")
    print(f"Current URL: {driver.current_url}\n")
    
    # Verify cart count is 0
    cart_count = driver.find_element(By.ID, "cartCount").text
    print(f"Initial cart count: {cart_count}")
    assert cart_count == "0", "Cart should be empty initially"

def step2_find_products(driver):
    """Step 2: Find products in DOM (multiple elements)."""
    print("\n", end="")
    print_step_header(2, "Find Products in Product Grid")
    product_cards = driver.find_elements(By.CLASS_NAME, "product-card")
    print(f"Found {len(product_cards)} products")
    
    for i, card in enumerate(product_cards, 1):
        product_name = card.find_element(By.TAG_NAME, "h3").text
        product_price = card.find_element(By.CLASS_NAME, "price").text
        print(f"  Product {i}: {product_name} - {product_price}")
    
    return product_cards

def step3_navigate_to_detail(driver, wait, product_cards):
    """Step 3: Click first product to navigate to detail page."""
    print("\n", end="")
    print_step_header(3, "Navigate to Product Detail Page")
    first_product_link = product_cards[0].find_element(By.CLASS_NAME, "btn-primary")
    product_name = product_cards[0].find_element(By.TAG_NAME, "h3").text
    print(f"Clicking on: {product_name}")
    first_product_link.click()
    
    # Wait for detail page to load
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-detail")))
    print(f"✅ Navigated to detail page: {driver.current_url}")
    print(f"Page title: {driver.title}\n")

def step4_switch_tabs(driver):
    """Step 4: Switch tabs on product detail page."""
    print_step_header(4, "Switch Tabs on Product Detail Page")
    
    # Find tabs
    tabs = driver.find_elements(By.CLASS_NAME, "tab-btn")
    print(f"Found {len(tabs)} tabs")
    
    # Click Reviews tab
    reviews_tab = None
    for tab in tabs:
        if tab.text == "Reviews":
            reviews_tab = tab
            break
    
    if reviews_tab:
        print("Clicking 'Reviews' tab...")
        reviews_tab.click()
        time.sleep(0.5)  # Wait for tab content to switch
        
        # Verify Reviews tab is active
        assert "active" in reviews_tab.get_attribute("class"), "Reviews tab should be active"
        print("✅ Reviews tab is now active")
        
        # Verify Reviews content is visible
        reviews_content = driver.find_element(By.ID, "spec-1")
        assert reviews_content.is_displayed(), "Reviews content should be visible"
        print("✅ Reviews content is visible")
    
    # Click Description tab back
    desc_tab = None
    for tab in tabs:
        if tab.text == "Description":
            desc_tab = tab
            break
    
    if desc_tab:
        print("Clicking 'Description' tab...")
        desc_tab.click()
        time.sleep(0.5)
        print("✅ Description tab is now active\n")

def step5_add_to_cart_modal(driver, wait):
    """Step 5: Add product to cart (handle modal)."""
    print_step_header(5, "Add Product to Cart (Modal Handling)")
    
    # Click Add to Cart button - wait for it to be clickable
    add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Cart')]")))
    print("Clicking 'Add to Cart' button...")
    add_to_cart_btn.click()
    
    # Wait for modal to appear
    wait.until(EC.visibility_of_element_located((By.ID, "addToCartModal")))
    modal = driver.find_element(By.ID, "addToCartModal")
    assert "show" in modal.get_attribute("class"), "Modal should be visible"
    print("✅ Modal opened")
    
    # Verify modal content
    modal_product_name = driver.find_element(By.ID, "modalProductName").text
    print(f"Modal shows: {modal_product_name}")
    
    # Change quantity in modal
    quantity_input = driver.find_element(By.ID, "quantity")
    quantity_input.clear()
    quantity_input.send_keys("2")
    print("Set quantity to 2")
    
    # Confirm add to cart - find button inside the modal specifically
    modal_content = driver.find_element(By.CLASS_NAME, "modal-content")
    confirm_btn = modal_content.find_element(By.XPATH, ".//button[contains(text(), 'Add to Cart')]")
    confirm_btn.click()
    
    # Wait for modal to close
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-content")))
    print("✅ Modal closed")
    
    # Wait for cart count to update
    cart_count = wait_for_cart_count(driver, 2)
    print(f"✅ Cart count updated to: {cart_count}\n")

def step6_add_second_product(driver, wait):
    """Step 6: Navigate back to listing, add second product."""
    print_step_header(6, "Navigate Back and Add Second Product")
    
    # Click back link
    back_link = driver.find_element(By.CLASS_NAME, "back-link")
    back_link.click()
    
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-grid")))
    print("✅ Back to listing page")
    
    # Click second product
    product_cards = driver.find_elements(By.CLASS_NAME, "product-card")
    second_product_link = product_cards[1].find_element(By.CLASS_NAME, "btn-primary")
    second_product_name = product_cards[1].find_element(By.TAG_NAME, "h3").text
    print(f"Clicking on: {second_product_name}")
    second_product_link.click()
    
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-detail")))
    print("✅ On second product detail page")
    
    # Wait for the specific product detail div to be visible (product-2 for Headphones)
    # The JavaScript shows/hides product divs based on URL parameter
    wait.until(EC.visibility_of_element_located((By.ID, "product-2")))
    print("✅ Product 2 detail is visible")
    
    # Add to cart (quantity 1) - wait for button to be clickable within visible product-2
    add_to_cart_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//div[@id='product-2']//button[contains(text(), 'Add to Cart')]")
    ))
    add_to_cart_btn.click()
    
    wait.until(EC.visibility_of_element_located((By.ID, "addToCartModal")))
    # Find button inside the modal specifically
    modal_content = driver.find_element(By.CLASS_NAME, "modal-content")
    confirm_btn = modal_content.find_element(By.XPATH, ".//button[contains(text(), 'Add to Cart')]")
    confirm_btn.click()
    
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-content")))
    cart_count = wait_for_cart_count(driver, 3)  # 2 + 1 = 3
    print(f"✅ Cart count updated to: {cart_count}\n")

def step7_navigate_to_cart(driver, wait):
    """Step 7: Navigate to cart page."""
    print_step_header(7, "Navigate to Shopping Cart Page")
    
    cart_link = driver.find_element(By.CLASS_NAME, "cart-link")
    cart_link.click()
    
    wait.until(EC.presence_of_element_located((By.ID, "cartItems")))
    print(f"✅ On cart page: {driver.current_url}")
    
    # Verify cart items are displayed
    cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
    print(f"Found {len(cart_items)} items in cart")
    
    return cart_items

def step8_update_quantity(driver, wait, cart_items):
    """Step 8: Update quantity in cart."""
    print("\n", end="")
    print_step_header(8, "Update Quantity in Cart")
    
    if cart_items:
        # Get product ID from first cart item before it becomes stale
        first_item_product_id = cart_items[0].get_attribute("data-product-id")
        
        # Find quantity input for first item using product ID and get current value
        quantity_input = driver.find_element(
            By.XPATH, f"//div[@data-product-id='{first_item_product_id}']//input[@class='cart-quantity-input']"
        )
        current_qty = quantity_input.get_attribute("value")
        print(f"Current quantity: {current_qty}")
        
        # Use JavaScript to set value and trigger change event to avoid stale element issues
        driver.execute_script("""
            var input = arguments[0];
            input.value = arguments[1];
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, quantity_input, "3")
        print("Set quantity to 3")
        
        # Wait for cart to re-render (renderCart() is called by onchange)
        time.sleep(0.5)  # Small delay for re-render
        
        # Re-find cart total after re-render
        cart_total = wait.until(EC.presence_of_element_located((By.ID, "cartTotal")))
        print(f"✅ Cart total updated: {cart_total.text}")

def step9_remove_item(driver):
    """Step 9: Remove an item from cart."""
    print("\n", end="")
    print_step_header(9, "Remove Item from Cart")
    
    # Find remove button for last item
    cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
    if len(cart_items) > 1:
        remove_btn = cart_items[-1].find_element(By.CLASS_NAME, "remove-btn")
        item_name = cart_items[-1].find_element(By.TAG_NAME, "h3").text
        print(f"Removing: {item_name}")
        remove_btn.click()
        
        time.sleep(1)  # Wait for removal
        
        # Verify item removed
        updated_cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
        print(f"✅ Items remaining: {len(updated_cart_items)}")
        
        # Verify cart count updated
        cart_count = driver.find_element(By.ID, "cartCount").text
        print(f"✅ Cart count: {cart_count}")

def step10_verify_final_state(driver):
    """Step 10: Verify final cart state."""
    print("\n", end="")
    print_step_header(10, "Verify Final Cart State")
    
    cart_total = driver.find_element(By.ID, "cartTotal").text
    print(f"Final cart total: {cart_total}")
    
    cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
    print(f"Final item count: {len(cart_items)}")
    
    for i, item in enumerate(cart_items, 1):
        name = item.find_element(By.TAG_NAME, "h3").text
        qty = item.find_element(By.CLASS_NAME, "cart-quantity-input").get_attribute("value")
        print(f"  Item {i}: {name} (Qty: {qty})")
    
    print("\n" + "=" * 60)
    print("✅ Automation completed successfully!")
    print("=" * 60)

def main():
    """Main automation function."""
    driver = None
    try:
        print("Setting up Chrome WebDriver...")
        driver = setup_driver()
        print("✅ WebDriver initialized\n")
        
        time.sleep(1)
        
        wait = WebDriverWait(driver, 15)
        
        # Execute all steps
        step1_navigate_to_listing(driver, wait)
        product_cards = step2_find_products(driver)
        step3_navigate_to_detail(driver, wait, product_cards)
        step4_switch_tabs(driver)
        step5_add_to_cart_modal(driver, wait)
        step6_add_second_product(driver, wait)
        cart_items = step7_navigate_to_cart(driver, wait)
        step8_update_quantity(driver, wait, cart_items)
        step9_remove_item(driver)
        step10_verify_final_state(driver)
        
        time.sleep(3)  # Pause to see final state
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()

if __name__ == "__main__":
    main()

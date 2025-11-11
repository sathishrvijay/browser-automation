# Product Catalog Automation

Automation script for the product catalog website. This demonstrates advanced Selenium interactions including multi-page navigation, modal handling, tab switching, and shopping cart operations.

## Quick Test

**Terminal 1 - Start server:**
```bash
source ../../bauto-venv/bin/activate
cd ../../websites/product-catalog && python server.py
```

**Terminal 2 - Run automation:**
```bash
source ../../bauto-venv/bin/activate
cd automations/product-catalog && python example_automation.py
```

Expected result: Chrome opens, navigates through pages, adds products to cart, updates quantities, removes items, and verifies cart state.

## What This Demonstrates

The `example_automation.py` script showcases:

- **Multi-page navigation**: Navigate between listing → detail → cart pages
- **Finding elements in different DOM sections**: Header (cart icon), main content (products)
- **Modal handling**: Wait for modal, interact with quantity input, confirm action
- **Tab switching**: Click tabs on product detail page, verify content changes
- **Dynamic waits**: Wait for cart count updates in header after actions
- **Multiple elements**: Find all product cards, iterate through items
- **Cart operations**: Add items, update quantities, remove items
- **State verification**: Check cart count, verify items and totals
- **Handling stale elements**: Using JavaScript execution to avoid stale element references when DOM re-renders
- **Element visibility waits**: Waiting for specific product divs to be visible before interaction

## Application Features

- **2 Products**: Laptop ($999.99) and Headphones ($149.99)
- **3 Pages**: Product listing, Product detail, Shopping cart
- **Modals**: Add to cart confirmation with quantity selection
- **Tabs**: Product detail tabs (Description, Reviews)
- **Dynamic Content**: Cart count updates in header across all pages
- **State Management**: Cart persists using localStorage
- **Cart Updates**: Cart totals automatically update when quantities change

## Troubleshooting

- **Port conflicts**: Server runs on port 8001 (different from simple-form's 8000)
- **Modal not appearing**: Make sure you wait for modal visibility before interacting
- **Cart count not updating**: Use explicit waits for cart count element updates
- **Page not loading**: Ensure server is running before starting automation

## Important Implementation Notes

### Modal Button Selection
When interacting with modals, always find buttons within the modal container to avoid clicking the wrong element:
```python
modal_content = driver.find_element(By.CLASS_NAME, "modal-content")
confirm_btn = modal_content.find_element(By.XPATH, ".//button[contains(text(), 'Add to Cart')]")
```

### Product Visibility
Product detail pages show/hide product divs based on URL parameters. Always wait for the specific product div to be visible:
```python
wait.until(EC.visibility_of_element_located((By.ID, "product-2")))
```

### Stale Element References
When updating cart quantities, the DOM re-renders which can cause stale element references. The automation uses JavaScript execution to avoid this:
```python
driver.execute_script("""
    var input = arguments[0];
    input.value = arguments[1];
    input.dispatchEvent(new Event('change', { bubbles: true }));
""", quantity_input, "3")
```

### Element Clickability
Always wait for elements to be clickable, not just present, especially after navigation:
```python
add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "...")))
```


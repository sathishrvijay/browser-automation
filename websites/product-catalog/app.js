// Product data
const products = {
    1: { id: 1, name: 'Laptop', price: 999.99 },
    2: { id: 2, name: 'Headphones', price: 149.99 }
};

// Cart management
function getCart() {
    const cartJson = localStorage.getItem('cart');
    return cartJson ? JSON.parse(cartJson) : [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function addToCart(productId, quantity) {
    const cart = getCart();
    const product = products[productId];
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: productId,
            name: product.name,
            price: product.price,
            quantity: quantity
        });
    }
    
    saveCart(cart);
    updateCartCount();
    return cart;
}

function removeFromCart(productId) {
    const cart = getCart().filter(item => item.id !== productId);
    saveCart(cart);
    updateCartCount();
    return cart;
}

function updateCartQuantity(productId, quantity) {
    const cart = getCart();
    const item = cart.find(item => item.id === productId);
    if (item) {
        if (quantity <= 0) {
            const updatedCart = removeFromCart(productId);
            // Re-render cart if on cart page
            if (window.location.pathname.includes('cart.html')) {
                renderCart();
            }
            return updatedCart;
        }
        item.quantity = quantity;
        saveCart(cart);
        updateCartCount();
        
        // Re-render cart if on cart page to update item totals and cart total
        if (window.location.pathname.includes('cart.html')) {
            renderCart();
        }
    }
    return cart;
}

function getCartTotal() {
    const cart = getCart();
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

function updateCartCount() {
    const cart = getCart();
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartCountElements = document.querySelectorAll('#cartCount');
    cartCountElements.forEach(el => el.textContent = count);
}

// Modal management
let currentModalProduct = null;

function openAddToCartModal(productId, productName, productPrice) {
    currentModalProduct = { id: productId, name: productName, price: productPrice };
    document.getElementById('modalProductName').textContent = `${productName} - $${productPrice.toFixed(2)}`;
    document.getElementById('quantity').value = 1;
    document.getElementById('addToCartModal').classList.add('show');
}

function closeAddToCartModal() {
    document.getElementById('addToCartModal').classList.remove('show');
    currentModalProduct = null;
}

function confirmAddToCart() {
    if (currentModalProduct) {
        const quantity = parseInt(document.getElementById('quantity').value) || 1;
        addToCart(currentModalProduct.id, quantity);
        closeAddToCartModal();
        
        // Show success message
        alert(`Added ${quantity} ${currentModalProduct.name}(s) to cart!`);
        
        // If on cart page, refresh it
        if (window.location.pathname.includes('cart.html')) {
            renderCart();
        }
    }
}

// Tab switching
function switchTab(showId, hideId) {
    document.getElementById(showId).classList.add('active');
    document.getElementById(hideId).classList.remove('active');
    
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(btn => {
        if (btn.textContent === 'Description' && showId.startsWith('desc')) {
            btn.classList.add('active');
        } else if (btn.textContent === 'Description') {
            btn.classList.remove('active');
        }
        if (btn.textContent === 'Reviews' && showId.startsWith('spec')) {
            btn.classList.add('active');
        } else if (btn.textContent === 'Reviews') {
            btn.classList.remove('active');
        }
    });
}

// Cart rendering
function renderCart() {
    const cart = getCart();
    const cartItemsDiv = document.getElementById('cartItems');
    const cartSummary = document.getElementById('cartSummary');
    
    if (cart.length === 0) {
        cartItemsDiv.innerHTML = '<p id="emptyCart" class="empty-cart">Your cart is empty.</p>';
        if (cartSummary) cartSummary.style.display = 'none';
        return;
    }
    
    if (cartSummary) cartSummary.style.display = 'block';
    
    cartItemsDiv.innerHTML = cart.map(item => `
        <div class="cart-item" data-product-id="${item.id}">
            <div class="cart-item-info">
                <h3>${item.name}</h3>
                <p>$${item.price.toFixed(2)} each</p>
            </div>
            <div class="cart-item-controls">
                <div class="quantity-control">
                    <label>Qty:</label>
                    <input type="number" 
                           value="${item.quantity}" 
                           min="1" 
                           onchange="updateCartQuantity(${item.id}, parseInt(this.value))"
                           class="cart-quantity-input">
                </div>
                <button class="remove-btn" onclick="removeFromCart(${item.id}); renderCart(); updateCartCount();">
                    Remove
                </button>
            </div>
            <div class="cart-item-total">
                <strong>$${(item.price * item.quantity).toFixed(2)}</strong>
            </div>
        </div>
    `).join('');
    
    if (cartSummary) {
        document.getElementById('cartTotal').textContent = `$${getCartTotal().toFixed(2)}`;
    }
}

function checkout() {
    const cart = getCart();
    if (cart.length === 0) {
        alert('Your cart is empty!');
        return;
    }
    
    const total = getCartTotal();
    alert(`Checkout complete!\n\nTotal: $${total.toFixed(2)}\n\nThank you for your purchase!`);
    
    // Clear cart
    saveCart([]);
    updateCartCount();
    renderCart();
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('addToCartModal');
    if (event.target === modal) {
        closeAddToCartModal();
    }
}


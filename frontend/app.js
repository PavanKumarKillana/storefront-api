// Configuration
const API_URL = 'http://127.0.0.1:8000/store';
let currentCartId = localStorage.getItem('cartId');

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
    if (!currentCartId) {
        await createNewCart();
    } else {
        await fetchCartDetails();
    }
    loadProducts();
});

// Create an anonymous cart via POST
async function createNewCart() {
    try {
        const response = await fetch(`${API_URL}/carts/`, { method: 'POST' });
        const data = await response.json();
        currentCartId = data.id;
        localStorage.setItem('cartId', currentCartId); // Save cart UUID to browser storage
        updateCartUI(0, 0);
    } catch (err) { 
        console.error("Error creating cart:", err); 
    }
}

// Fetch existing cart details
async function fetchCartDetails() {
    try {
        const response = await fetch(`${API_URL}/carts/${currentCartId}/`);
        if(response.status === 404) {
             // If Django deleted our old cart, we clear storage and make a new one
             localStorage.removeItem('cartId');
             currentCartId = null;
             await createNewCart();
             return;
        }
        const cart = await response.json();
        
        // Sum total quantity from nested items
        const totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);
        updateCartUI(totalItems, cart.total_price);
    } catch (err) { 
        console.error("Error fetching cart:", err); 
    }
}

// Load products from GET /store/products/
async function loadProducts() {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '<div class="loading">Loading products from Django API...</div>';
    
    try {
        const response = await fetch(`${API_URL}/products/`);
        const data = await response.json();
        
        // DRF may wrap data in a 'results' array if pagination is enabled
        const products = data.results ? data.results : data;
        
        grid.innerHTML = ''; // Clear loading
        
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'card';
            
            // Check if product has an image, otherwise leave blank or add placeholder
            let imageHtml = '';
            if (product.images && product.images.length > 0) {
                // DRF provides the absolute URL (e.g. http://127.0.0.1:8000/media/store/images/...)
                imageHtml = `<img src="${product.images[0].image}" class="product-image" alt="${product.title}">`;
            }

            card.innerHTML = `
                ${imageHtml}
                <div style="padding: 15px;">
                    <div class="card-title">${product.title}</div>
                    <div class="card-price">$${product.unit_price}</div>
                </div>
                <button class="add-btn" onclick="addToCart(${product.id})">Add 1 to Cart +</button>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        grid.innerHTML = '<h3 style="color:#e74c3c;">💥 Connection Refused. Make sure your Django Server is running!</h3>';
        console.error("Error loading products:", error);
    }
}

// Add item to cart via POST /store/carts/{id}/items/
async function addToCart(productId) {
    try {
        const response = await fetch(`${API_URL}/carts/${currentCartId}/items/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ 
                product_id: productId, 
                quantity: 1 
            })
        });
        
        if (response.ok) {
            // Trigger UI update
            await fetchCartDetails(); 
            alert('Item successfully added to Django Cart!');
        } else {
            const errorData = await response.json();
            alert('Failed to add item: ' + JSON.stringify(errorData));
        }
    } catch (error) { 
        console.error("Error adding to cart:", error); 
    }
}

// Update DOM elements
function updateCartUI(count, total) {
    document.getElementById('cart-count').innerText = `🛒 Cart (${count})`;
    document.getElementById('cart-total').innerText = `$${Number(total).toFixed(2)}`;
}

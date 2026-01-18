/**
 * Product Recommendation Agent - Frontend JavaScript
 */

const API_BASE = 'http://localhost:5000/api';
let currentUser = null;
let allProducts = [];
let allCategories = [];

// Initialize application
document.addEventListener('DOMContentLoaded', async () => {
    await loadUsers();
    await loadCategories();
    await loadProducts();

    // Set up event listeners
    document.getElementById('userSelect').addEventListener('change', onUserChange);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchProducts();
    });
});

// Load users
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const data = await response.json();

        const userSelect = document.getElementById('userSelect');
        userSelect.innerHTML = data.users.map(user =>
            `<option value="${user.id}">${user.name}</option>`
        ).join('');

        // Set first user as current
        if (data.users.length > 0) {
            currentUser = data.users[0].id;
            userSelect.value = currentUser;
            await loadRecommendations();
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const data = await response.json();
        allCategories = data.categories;

        const categoryFilter = document.getElementById('categoryFilter');
        categoryFilter.innerHTML = '<option value="">All Categories</option>' +
            data.categories.map(cat =>
                `<option value="${cat}">${cat}</option>`
            ).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load all products
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE}/products`);
        const data = await response.json();
        allProducts = data.products;
        displayProducts(data.products, 'productsGrid');
    } catch (error) {
        console.error('Error loading products:', error);
        showError('productsGrid', 'Failed to load products');
    }
}

// Load recommendations
async function loadRecommendations() {
    if (!currentUser) return;

    try {
        const response = await fetch(`${API_BASE}/recommendations/${currentUser}?limit=8`);
        const data = await response.json();

        if (data.recommendations.length === 0) {
            showEmptyState('recommendationsGrid', 'No recommendations yet. Browse products to get personalized suggestions!');
        } else {
            displayProducts(data.recommendations, 'recommendationsGrid');
        }
    } catch (error) {
        console.error('Error loading recommendations:', error);
        showError('recommendationsGrid', 'Failed to load recommendations');
    }
}

// Display products in grid
function displayProducts(products, gridId) {
    const grid = document.getElementById(gridId);

    if (products.length === 0) {
        showEmptyState(gridId, 'No products found matching your criteria');
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card" onclick="showProductDetail(${product.id})">
            <img src="${product.image_url}" alt="${product.name}" class="product-image" 
                 onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500'">
            <div class="product-info">
                <div class="product-category">${product.category}</div>
                <h3 class="product-name">${product.name}</h3>
                <div class="product-brand">${product.brand || 'Generic'}</div>
                <div class="product-rating">
                    <span class="stars">${renderStars(product.rating)}</span>
                    <span class="rating-count">(${product.num_ratings})</span>
                </div>
                <div class="product-price">$${product.price.toFixed(2)}</div>
                <div class="product-actions">
                    <button class="btn btn-primary btn-small" onclick="event.stopPropagation(); addToCart(${product.id})">
                        🛒 Add to Cart
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="event.stopPropagation(); showProductDetail(${product.id})">
                        👁️ View
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Render star rating
function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return '★'.repeat(fullStars) +
        (hasHalfStar ? '⯨' : '') +
        '☆'.repeat(emptyStars);
}

// Show product detail modal
async function showProductDetail(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        const product = await response.json();

        // Track view in history
        if (currentUser) {
            trackUserAction(productId, 'view');
        }

        const modal = document.getElementById('productModal');
        const modalBody = document.getElementById('modalBody');
        document.getElementById('modalProductName').textContent = product.name;

        modalBody.innerHTML = `
            <div class="product-detail-grid">
                <div>
                    <img src="${product.image_url}" alt="${product.name}" class="product-detail-image"
                         onerror="this.src='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500'">
                </div>
                <div>
                    <div class="product-category">${product.category}</div>
                    <h3 class="product-name">${product.name}</h3>
                    <div class="product-brand">${product.brand || 'Generic'}</div>
                    <div class="product-rating">
                        <span class="stars">${renderStars(product.rating)}</span>
                        <span class="rating-count">(${product.num_ratings} ratings)</span>
                    </div>
                    <div class="product-price">$${product.price.toFixed(2)}</div>
                    <p style="color: var(--text-secondary); margin: var(--spacing-md) 0;">
                        ${product.description}
                    </p>
                    <h4 style="margin-top: var(--spacing-md);">Features:</h4>
                    <ul class="product-features">
                        ${product.features.map(feature => `<li>${feature}</li>`).join('')}
                    </ul>
                    <div style="margin-top: var(--spacing-md);">
                        <button class="btn btn-primary" onclick="addToCart(${product.id})">
                            🛒 Add to Cart
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="rating-section">
                <h3>Rate this product</h3>
                <div class="star-rating" id="starRating">
                    ${[1, 2, 3, 4, 5].map(star =>
            `<span class="star" data-rating="${star}" onclick="rateProduct(${product.id}, ${star})">★</span>`
        ).join('')}
                </div>
                <p style="color: var(--text-muted); font-size: 0.875rem; margin-top: var(--spacing-xs);">
                    Click to rate this product
                </p>
            </div>
        `;

        modal.classList.add('active');

        // Add hover effect to stars
        const stars = document.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('mouseenter', function () {
                const rating = parseInt(this.dataset.rating);
                highlightStars(rating);
            });
        });

        document.getElementById('starRating').addEventListener('mouseleave', () => {
            highlightStars(0);
        });

    } catch (error) {
        console.error('Error loading product details:', error);
        alert('Failed to load product details');
    }
}

// Highlight stars
function highlightStars(rating) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

// Rate product
async function rateProduct(productId, rating) {
    if (!currentUser) {
        alert('Please select a user to rate products');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/ratings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: currentUser,
                product_id: productId,
                rating: rating
            })
        });

        if (response.ok) {
            alert(`Thank you for rating this product ${rating} stars!`);
            closeModal();
            // Reload products and recommendations to reflect new rating
            await loadProducts();
            await loadRecommendations();
        }
    } catch (error) {
        console.error('Error rating product:', error);
        alert('Failed to submit rating');
    }
}

// Track user action
async function trackUserAction(productId, actionType) {
    if (!currentUser) return;

    try {
        await fetch(`${API_BASE}/history/${currentUser}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                action_type: actionType
            })
        });
    } catch (error) {
        console.error('Error tracking action:', error);
    }
}

// Add to cart (simulated)
async function addToCart(productId) {
    if (currentUser) {
        await trackUserAction(productId, 'add_to_cart');
    }

    // Show feedback
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '✓ Added!';
    btn.style.background = 'linear-gradient(135deg, #10b981, #059669)';

    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = '';
    }, 2000);
}

// Close modal
function closeModal() {
    document.getElementById('productModal').classList.remove('active');
}

// Close modal on outside click
document.getElementById('productModal').addEventListener('click', (e) => {
    if (e.target.id === 'productModal') {
        closeModal();
    }
});

// User change handler
async function onUserChange(e) {
    currentUser = parseInt(e.target.value);
    await loadRecommendations();
}

// Search products
async function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value;
    await applyFilters();
}

// Apply filters
async function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value;
    const category = document.getElementById('categoryFilter').value;
    const sortBy = document.getElementById('sortBy').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;

    const params = new URLSearchParams();
    if (searchTerm) params.append('search', searchTerm);
    if (category) params.append('category', category);
    if (sortBy) params.append('sort_by', sortBy);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);

    try {
        const response = await fetch(`${API_BASE}/products?${params}`);
        const data = await response.json();
        displayProducts(data.products, 'productsGrid');
    } catch (error) {
        console.error('Error filtering products:', error);
        showError('productsGrid', 'Failed to filter products');
    }
}

// Clear filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('sortBy').value = 'name';
    document.getElementById('minPrice').value = '';
    document.getElementById('maxPrice').value = '';
    loadProducts();
}

// Show empty state
function showEmptyState(gridId, message) {
    const grid = document.getElementById(gridId);
    grid.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">📦</div>
            <p>${message}</p>
        </div>
    `;
}

// Show error
function showError(gridId, message) {
    const grid = document.getElementById(gridId);
    grid.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <p>${message}</p>
        </div>
    `;
}

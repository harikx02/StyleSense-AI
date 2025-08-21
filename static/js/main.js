// Amazon Fashion Recommender JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Search functionality
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="q"]');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
                showAlert('Please enter a search term', 'warning');
            }
        });
    }

    // Image lazy loading and error handling
    const images = document.querySelectorAll('img[data-src]');
    if (images.length > 0) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Product card animations
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 50}ms`;
        card.classList.add('fade-in');
    });

    // Search suggestions (if we had an API)
    const searchInputs = document.querySelectorAll('input[name="q"]');
    searchInputs.forEach(input => {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            const query = this.value.trim();
            
            if (query.length > 2) {
                timeout = setTimeout(() => {
                    // Could implement search suggestions here
                    console.log('Search suggestions for:', query);
                }, 300);
            }
        });
    });

    // Add to cart simulation
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn:contains("Cart")') || e.target.closest('.btn:contains("Cart")')) {
            e.preventDefault();
            showAlert('Item added to cart! (Demo functionality)', 'success');
            
            // Add animation effect
            const btn = e.target.closest('.btn');
            btn.classList.add('btn-success');
            btn.innerHTML = '<i class="fas fa-check"></i> Added!';
            
            setTimeout(() => {
                btn.classList.remove('btn-success');
                btn.innerHTML = '<i class="fas fa-cart-plus"></i> Cart';
            }, 2000);
        }
    });

    // Wishlist simulation
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn:contains("Wishlist")') || e.target.matches('.btn:contains("Save")') || 
            e.target.closest('.btn:contains("Wishlist")') || e.target.closest('.btn:contains("Save")')) {
            e.preventDefault();
            const btn = e.target.closest('.btn');
            
            if (btn.classList.contains('btn-danger')) {
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-outline-danger');
                btn.innerHTML = '<i class="far fa-heart"></i> Save';
                showAlert('Removed from wishlist', 'info');
            } else {
                btn.classList.remove('btn-outline-danger');
                btn.classList.add('btn-danger');
                btn.innerHTML = '<i class="fas fa-heart"></i> Saved';
                showAlert('Added to wishlist! (Demo functionality)', 'success');
            }
        }
    });

    // Loading states for buttons
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn[data-loading]');
        if (btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="loading"></span> Loading...';
            btn.disabled = true;
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 1500);
        }
    });

    // Filter animations
    const filterItems = document.querySelectorAll('.list-group-item');
    filterItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });

    // Scroll to top button
    const scrollTopBtn = createScrollTopButton();
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.style.display = 'block';
            scrollTopBtn.style.opacity = '1';
        } else {
            scrollTopBtn.style.opacity = '0';
            setTimeout(() => {
                if (window.pageYOffset <= 300) {
                    scrollTopBtn.style.display = 'none';
                }
            }, 300);
        }
    });

    // Price formatting
    const priceElements = document.querySelectorAll('.price');
    priceElements.forEach(el => {
        const price = parseFloat(el.textContent.replace(/[^\d.]/g, ''));
        if (!isNaN(price)) {
            el.textContent = `${price.toFixed(2)}`;
        }
    });

    // Rating stars interaction
    const ratingStars = document.querySelectorAll('.rating-stars .fa-star');
    ratingStars.forEach((star, index) => {
        star.addEventListener('mouseenter', function() {
            // Highlight stars up to this one
            for (let i = 0; i <= index; i++) {
                ratingStars[i].classList.add('text-warning');
            }
        });
        
        star.addEventListener('mouseleave', function() {
            // Reset to original state
            ratingStars.forEach(s => s.classList.remove('text-warning'));
        });
    });

    // Search filters collapse on mobile
    const filterToggle = document.querySelector('#filterToggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            const filtersCol = document.querySelector('.filters-column');
            filtersCol.classList.toggle('show');
        });
    }

    // Product image zoom
    const productImages = document.querySelectorAll('.product-image-large img');
    productImages.forEach(img => {
        img.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;
            
            this.style.transformOrigin = `${x}% ${y}%`;
            this.style.transform = 'scale(1.5)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.transformOrigin = 'center center';
        });
    });
});

// Utility Functions
function showAlert(message, type = 'info', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, duration);
}

function createScrollTopButton() {
    const btn = document.createElement('button');
    btn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    btn.className = 'btn btn-primary rounded-circle position-fixed';
    btn.style.cssText = `
        bottom: 20px; 
        right: 20px; 
        z-index: 999; 
        display: none; 
        width: 50px; 
        height: 50px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    btn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(btn);
    return btn;
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API Helper Functions
async function fetchRecommendations(productId) {
    try {
        const response = await fetch(`/api/recommendations/${productId}`);
        if (!response.ok) throw new Error('Failed to fetch recommendations');
        return await response.json();
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        return { success: false, error: error.message };
    }
}

async function searchProducts(query, limit = 12) {
    try {
        const url = new URL('/api/search', window.location.origin);
        url.searchParams.set('q', query);
        url.searchParams.set('limit', limit);
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Search failed');
        return await response.json();
    } catch (error) {
        console.error('Error searching products:', error);
        return { success: false, error: error.message };
    }
}

// Performance monitoring
function trackPageLoad() {
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        
        // Could send to analytics
        if (loadTime > 3000) {
            console.warn('Page load time is high:', loadTime);
        }
    });
}

trackPageLoad();
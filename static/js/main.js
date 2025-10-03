/**
 * 🚀 Elite FnO Trading Platform - Enhanced JavaScript
 * Main interactive functionality and mobile optimizations
 */

class EliteFnOApp {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth <= 1024 && window.innerWidth > 768;
        this.touchStartY = 0;
        this.touchEndY = 0;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initScrollReveal();
        this.initMobileNavigation();
        this.initPriceUpdates();
        this.initNotificationSystem();
        this.setupTouchGestures();
        this.optimizeForMobile();
        
        // Initialize after DOM is fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupAnimations();
            });
        } else {
            this.setupAnimations();
        }
    }

    setupEventListeners() {
        // Window resize handler
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));

        // Scroll handler for animations
        window.addEventListener('scroll', this.throttle(() => {
            this.handleScroll();
        }, 16));

        // Error handling
        window.addEventListener('error', this.handleError.bind(this));
        window.addEventListener('unhandledrejection', this.handlePromiseError.bind(this));
    }

    setupAnimations() {
        // GSAP animations if available
        if (typeof gsap !== 'undefined') {
            this.initGSAPAnimations();
        } else {
            this.initFallbackAnimations();
        }
    }

    initGSAPAnimations() {
        // Hero section animation
        const heroTimeline = gsap.timeline();
        
        heroTimeline
            .from('.hero-title', {
                y: 50,
                opacity: 0,
                duration: 1,
                ease: 'power3.out'
            })
            .from('.hero-subtitle', {
                y: 30,
                opacity: 0,
                duration: 0.8,
                ease: 'power3.out'
            }, '-=0.5')
            .from('.btn-primary', {
                y: 20,
                opacity: 0,
                scale: 0.9,
                duration: 0.6,
                ease: 'back.out(1.7)'
            }, '-=0.3');

        // Card animations on scroll
        gsap.registerPlugin(ScrollTrigger);
        
        gsap.utils.toArray('.glass-card').forEach((card, index) => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    end: 'bottom 15%',
                    toggleActions: 'play none none reverse'
                },
                y: 50,
                opacity: 0,
                duration: 0.6,
                delay: index * 0.1,
                ease: 'power3.out'
            });
        });
    }

    initFallbackAnimations() {
        // CSS-based animations fallback
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -10% 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                }
            });
        }, observerOptions);

        // Observe all scroll-reveal elements
        document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right')
            .forEach(el => observer.observe(el));
    }

    initScrollReveal() {
        // Custom scroll reveal implementation
        const revealElements = document.querySelectorAll('[data-reveal]');
        
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const delay = element.dataset.delay || 0;
                    
                    setTimeout(() => {
                        element.classList.add('animate-fadeInUp');
                    }, delay);
                    
                    revealObserver.unobserve(element);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -5% 0px'
        });

        revealElements.forEach(el => revealObserver.observe(el));
    }

    initMobileNavigation() {
        const mobileMenuButton = document.querySelector('.mobile-menu-button');
        const mobileMenu = document.querySelector('.mobile-menu');
        const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                this.toggleMobileMenu();
            });

            // Close menu when clicking overlay
            if (mobileMenuOverlay) {
                mobileMenuOverlay.addEventListener('click', () => {
                    this.closeMobileMenu();
                });
            }

            // Close menu when clicking nav links
            mobileMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    this.closeMobileMenu();
                });
            });
        }
    }

    toggleMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
        const body = document.body;

        if (mobileMenu && mobileMenuOverlay) {
            const isOpen = mobileMenu.classList.contains('active');
            
            if (isOpen) {
                this.closeMobileMenu();
            } else {
                mobileMenu.classList.add('active');
                mobileMenuOverlay.classList.add('active');
                body.style.overflow = 'hidden';
            }
        }
    }

    closeMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
        const body = document.body;

        if (mobileMenu && mobileMenuOverlay) {
            mobileMenu.classList.remove('active');
            mobileMenuOverlay.classList.remove('active');
            body.style.overflow = '';
        }
    }

    initPriceUpdates() {
        // Simulate live price updates
        const priceElements = document.querySelectorAll('.live-price');
        
        if (priceElements.length > 0) {
            setInterval(() => {
                priceElements.forEach(element => {
                    this.updatePrice(element);
                });
            }, 3000 + Math.random() * 2000); // Random interval between 3-5 seconds
        }
    }

    updatePrice(element) {
        const currentPrice = parseFloat(element.textContent.replace(/[^\d.-]/g, ''));
        const change = (Math.random() - 0.5) * (currentPrice * 0.02); // Max 2% change
        const newPrice = (currentPrice + change).toFixed(2);
        
        element.textContent = `₹${newPrice}`;
        
        // Add visual feedback
        if (change > 0) {
            element.classList.add('price-up');
            setTimeout(() => element.classList.remove('price-up'), 300);
        } else if (change < 0) {
            element.classList.add('price-down');
            setTimeout(() => element.classList.remove('price-down'), 300);
        }
    }

    initNotificationSystem() {
        this.notifications = [];
        this.createNotificationContainer();
    }

    createNotificationContainer() {
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        const notification = document.createElement('div');
        
        notification.className = `alert alert-${type} notification-enter`;
        notification.style.cssText = `
            pointer-events: auto;
            margin-bottom: 10px;
            min-width: 300px;
        `;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="modal-close" onclick="this.parentElement.remove()">×</button>
        `;

        container.appendChild(notification);

        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('notification-exit');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, duration);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    setupTouchGestures() {
        if (!this.isMobile) return;

        document.addEventListener('touchstart', (e) => {
            this.touchStartY = e.changedTouches[0].screenY;
        });

        document.addEventListener('touchend', (e) => {
            this.touchEndY = e.changedTouches[0].screenY;
            this.handleSwipe();
        });
    }

    handleSwipe() {
        const swipeThreshold = 50;
        const diff = this.touchStartY - this.touchEndY;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe up
                this.handleSwipeUp();
            } else {
                // Swipe down
                this.handleSwipeDown();
            }
        }
    }

    handleSwipeUp() {
        // Implement swipe up functionality
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu && mobileMenu.classList.contains('active')) {
            this.closeMobileMenu();
        }
    }

    handleSwipeDown() {
        // Implement swipe down functionality
        // Could be used for refreshing content
    }

    optimizeForMobile() {
        if (this.isMobile) {
            // Add mobile-specific optimizations
            document.body.classList.add('mobile');
            
            // Optimize touch targets
            this.optimizeTouchTargets();
            
            // Reduce animations for performance
            this.reduceAnimationsForMobile();
            
            // Add pull-to-refresh (if needed)
            this.addPullToRefresh();
        }
    }

    optimizeTouchTargets() {
        const buttons = document.querySelectorAll('button, .btn, a');
        buttons.forEach(button => {
            const rect = button.getBoundingClientRect();
            if (rect.height < 44 || rect.width < 44) {
                button.style.minHeight = '44px';
                button.style.minWidth = '44px';
                button.style.display = 'inline-flex';
                button.style.alignItems = 'center';
                button.style.justifyContent = 'center';
            }
        });
    }

    reduceAnimationsForMobile() {
        // Reduce complex animations on mobile for better performance
        const complexAnimations = document.querySelectorAll('.bg-animated');
        complexAnimations.forEach(element => {
            element.style.animation = 'none';
        });
    }

    addPullToRefresh() {
        let startY = 0;
        let pullDistance = 0;
        const threshold = 80;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY > 0) {
                pullDistance = e.touches[0].clientY - startY;
                if (pullDistance > 0) {
                    e.preventDefault();
                    // Visual feedback for pull to refresh
                    if (pullDistance > threshold) {
                        // Show refresh indicator
                    }
                }
            }
        });

        document.addEventListener('touchend', () => {
            if (pullDistance > threshold) {
                // Trigger refresh
                window.location.reload();
            }
            startY = 0;
            pullDistance = 0;
        });
    }

    handleResize() {
        const newIsMobile = window.innerWidth <= 768;
        const newIsTablet = window.innerWidth <= 1024 && window.innerWidth > 768;

        if (newIsMobile !== this.isMobile || newIsTablet !== this.isTablet) {
            this.isMobile = newIsMobile;
            this.isTablet = newIsTablet;
            
            // Reoptimize for new screen size
            if (this.isMobile) {
                this.optimizeForMobile();
            } else {
                document.body.classList.remove('mobile');
            }
        }
    }

    handleScroll() {
        const scrollY = window.scrollY;
        
        // Navbar background opacity based on scroll
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            const opacity = Math.min(scrollY / 100, 1);
            navbar.style.backgroundColor = `rgba(12, 12, 12, ${0.7 + opacity * 0.3})`;
        }

        // Show/hide scroll to top button
        const scrollButton = document.querySelector('.scroll-to-top');
        if (scrollButton) {
            if (scrollY > 500) {
                scrollButton.classList.add('visible');
            } else {
                scrollButton.classList.remove('visible');
            }
        }
    }

    handleError(event) {
        console.error('JavaScript Error:', event.error);
        this.showNotification('An error occurred. Please refresh the page.', 'error');
    }

    handlePromiseError(event) {
        console.error('Promise Rejection:', event.reason);
        this.showNotification('A network error occurred. Please try again.', 'error');
    }

    // Utility functions
    debounce(func, wait) {
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

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // API Methods
    async fetchData(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            this.showNotification('Failed to load data. Please try again.', 'error');
            throw error;
        }
    }

    // Payment Integration
    initRazorpay(options) {
        if (typeof Razorpay === 'undefined') {
            console.error('Razorpay not loaded');
            return;
        }

        const defaultOptions = {
            handler: (response) => {
                this.handlePaymentSuccess(response);
            },
            modal: {
                ondismiss: () => {
                    this.showNotification('Payment was cancelled', 'warning');
                }
            }
        };

        const rzp = new Razorpay({ ...defaultOptions, ...options });
        rzp.open();
    }

    handlePaymentSuccess(response) {
        this.showNotification('Payment successful!', 'success');
        // Handle successful payment
        console.log('Payment Success:', response);
    }
}

// Initialize the app
const eliteFnOApp = new EliteFnOApp();

// Export for use in other files
window.EliteFnOApp = EliteFnOApp;
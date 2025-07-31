// SecretGPTee Responsive JavaScript Enhancements
// Mobile-first responsive behavior, touch interactions, and adaptive UI elements

// Responsive state management
const ResponsiveState = {
    isMobile: window.innerWidth <= 768,
    isTablet: window.innerWidth > 768 && window.innerWidth <= 1024,
    isDesktop: window.innerWidth > 1024,
    isTouchDevice: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
    orientation: window.innerHeight > window.innerWidth ? 'portrait' : 'landscape',
    previousWidth: window.innerWidth,
    sidebarOpen: false,
    keyboardVisible: false
};

// Responsive utilities
const ResponsiveUtils = {
    // Update responsive state
    updateState() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        ResponsiveState.previousWidth = ResponsiveState.isMobile ? 768 : ResponsiveState.isTablet ? 1024 : width;
        ResponsiveState.isMobile = width <= 768;
        ResponsiveState.isTablet = width > 768 && width <= 1024;
        ResponsiveState.isDesktop = width > 1024;
        ResponsiveState.orientation = height > width ? 'portrait' : 'landscape';
        
        // Update CSS custom properties
        document.documentElement.style.setProperty('--viewport-width', `${width}px`);
        document.documentElement.style.setProperty('--viewport-height', `${height}px`);
        document.documentElement.style.setProperty('--is-mobile', ResponsiveState.isMobile ? '1' : '0');
        document.documentElement.style.setProperty('--is-touch', ResponsiveState.isTouchDevice ? '1' : '0');
    },
    
    // Get current breakpoint
    getCurrentBreakpoint() {
        if (ResponsiveState.isMobile) return 'mobile';
        if (ResponsiveState.isTablet) return 'tablet';
        return 'desktop';
    },
    
    // Check if element is in viewport
    isInViewport(element, threshold = 0) {
        const rect = element.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const windowWidth = window.innerWidth || document.documentElement.clientWidth;
        
        return (
            rect.top >= -threshold &&
            rect.left >= -threshold &&
            rect.bottom <= windowHeight + threshold &&
            rect.right <= windowWidth + threshold
        );
    },
    
    // Debounce function for resize events
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
};

// Mobile navigation and sidebar management
const MobileNavigation = {
    init() {
        this.setupToggleButton();
        this.setupOverlay();
        this.setupSwipeGestures();
        this.setupKeyboardHandling();
    },
    
    setupToggleButton() {
        const toggleBtn = document.getElementById('mobile-menu-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSidebar();
            });
        }
    },
    
    setupOverlay() {
        let overlay = document.getElementById('mobile-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'mobile-overlay';
            overlay.className = 'mobile-overlay';
            document.body.appendChild(overlay);
        }
        
        overlay.addEventListener('click', () => {
            this.closeSidebar();
        });
    },
    
    toggleSidebar() {
        if (ResponsiveState.sidebarOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    },
    
    openSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        const toggleBtn = document.getElementById('mobile-menu-toggle');
        
        if (sidebar) {
            sidebar.classList.add('sidebar-open');
            ResponsiveState.sidebarOpen = true;
            
            // Animate sidebar in
            if (window.AnimationUtils) {
                window.AnimationUtils.animate(sidebar, [
                    { transform: 'translateX(-100%)' },
                    { transform: 'translateX(0)' }
                ], {
                    duration: 300,
                    easing: 'ease-out'
                });
            }
        }
        
        if (overlay) {
            overlay.classList.add('overlay-visible');
            if (window.AnimationUtils) {
                window.AnimationUtils.fadeIn(overlay, { duration: 200 });
            }
        }
        
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', 'true');
            toggleBtn.innerHTML = '<i class="fas fa-times"></i>';
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    },
    
    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobile-overlay');
        const toggleBtn = document.getElementById('mobile-menu-toggle');
        
        if (sidebar) {
            sidebar.classList.remove('sidebar-open');
            ResponsiveState.sidebarOpen = false;
            
            // Animate sidebar out
            if (window.AnimationUtils) {
                window.AnimationUtils.animate(sidebar, [
                    { transform: 'translateX(0)' },
                    { transform: 'translateX(-100%)' }
                ], {
                    duration: 250,
                    easing: 'ease-in'
                });
            }
        }
        
        if (overlay) {
            overlay.classList.remove('overlay-visible');
            if (window.AnimationUtils) {
                window.AnimationUtils.fadeOut(overlay, { duration: 150 });
            }
        }
        
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', 'false');
            toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        }
        
        // Restore body scroll
        document.body.style.overflow = '';
    },
    
    setupSwipeGestures() {
        let startX = 0;
        let currentX = 0;
        let isSwipping = false;
        
        document.addEventListener('touchstart', (e) => {
            if (ResponsiveState.isMobile) {
                startX = e.touches[0].clientX;
                isSwipping = true;
            }
        });
        
        document.addEventListener('touchmove', (e) => {
            if (!isSwipping || !ResponsiveState.isMobile) return;
            
            currentX = e.touches[0].clientX;
            const diffX = currentX - startX;
            
            // Swipe from left edge to open sidebar
            if (startX < 50 && diffX > 50 && !ResponsiveState.sidebarOpen) {
                this.openSidebar();
                isSwipping = false;
            }
            
            // Swipe right to close sidebar when open
            if (ResponsiveState.sidebarOpen && diffX > 100) {
                this.closeSidebar();
                isSwipping = false;
            }
        });
        
        document.addEventListener('touchend', () => {
            isSwipping = false;
        });
    },
    
    setupKeyboardHandling() {
        document.addEventListener('keydown', (e) => {
            if (ResponsiveState.sidebarOpen && e.key === 'Escape') {
                this.closeSidebar();
            }
        });
    }
};

// Touch and gesture enhancements
const TouchEnhancements = {
    init() {
        if (!ResponsiveState.isTouchDevice) return;
        
        this.setupTouchFeedback();
        this.setupScrollEnhancements();
        this.setupPullToRefresh();
    },
    
    setupTouchFeedback() {
        // Add touch feedback to interactive elements
        const touchElements = document.querySelectorAll('button, .btn, .card, .message-wrapper');
        
        touchElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                element.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', (e) => {
                setTimeout(() => {
                    element.classList.remove('touch-active');
                }, 150);
            });
            
            element.addEventListener('touchcancel', (e) => {
                element.classList.remove('touch-active');
            });
        });
    },
    
    setupScrollEnhancements() {
        // Smooth scrolling for touch devices
        const scrollContainers = document.querySelectorAll('.messages-container, .settings-content');
        
        scrollContainers.forEach(container => {
            container.style.webkitOverflowScrolling = 'touch';
            container.style.scrollBehavior = 'smooth';
        });
    },
    
    setupPullToRefresh() {
        const messagesContainer = document.getElementById('messages-container');
        if (!messagesContainer) return;
        
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        let pullDistance = 0;
        
        messagesContainer.addEventListener('touchstart', (e) => {
            if (messagesContainer.scrollTop === 0) {
                startY = e.touches[0].clientY;
                isPulling = false;
            }
        });
        
        messagesContainer.addEventListener('touchmove', (e) => {
            if (messagesContainer.scrollTop > 0) return;
            
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 10) {
                isPulling = true;
                e.preventDefault();
                
                // Visual feedback for pull
                const pullIndicator = this.createPullIndicator();
                const opacity = Math.min(pullDistance / 100, 1);
                pullIndicator.style.opacity = opacity;
                
                if (pullDistance > 60) {
                    pullIndicator.classList.add('ready-to-refresh');
                }
            }
        });
        
        messagesContainer.addEventListener('touchend', (e) => {
            if (isPulling && pullDistance > 60) {
                this.triggerRefresh();
            }
            
            this.hidePullIndicator();
            isPulling = false;
            pullDistance = 0;
        });
    },
    
    createPullIndicator() {
        let indicator = document.getElementById('pull-refresh-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'pull-refresh-indicator';
            indicator.className = 'pull-refresh-indicator';
            indicator.innerHTML = `
                <div class="pull-icon">
                    <i class="fas fa-arrow-down"></i>
                </div>
                <div class="pull-text">Pull to refresh</div>
            `;
            document.body.appendChild(indicator);
        }
        return indicator;
    },
    
    hidePullIndicator() {
        const indicator = document.getElementById('pull-refresh-indicator');
        if (indicator) {
            if (window.AnimationUtils) {
                window.AnimationUtils.fadeOut(indicator, {
                    duration: 200,
                    onComplete: () => indicator.remove()
                });
            } else {
                indicator.remove();
            }
        }
    },
    
    triggerRefresh() {
        console.log('Pull to refresh triggered');
        
        // Show loading state
        if (window.LoadingAnimations) {
            window.LoadingAnimations.showOverlay('Refreshing...');
        }
        
        // Simulate refresh (implement actual refresh logic)
        setTimeout(() => {
            if (window.LoadingAnimations) {
                window.LoadingAnimations.hideOverlay();
            }
            
            if (window.SecretGPTee && window.SecretGPTee.showToast) {
                window.SecretGPTee.showToast('Refreshed', 'success');
            }
        }, 1500);
    }
};

// Adaptive UI elements
const AdaptiveUI = {
    init() {
        this.setupResponsiveInputs();
        this.setupAdaptiveModal();
        this.setupResponsiveGrid();
        this.setupDynamicFontSizing();
    },
    
    setupResponsiveInputs() {
        const messageInput = document.getElementById('message-input');
        if (messageInput && ResponsiveState.isMobile) {
            // Mobile-specific input handling
            messageInput.addEventListener('focus', () => {
                this.handleKeyboardAppearance();
            });
            
            messageInput.addEventListener('blur', () => {
                this.handleKeyboardDisappearance();
            });
        }
    },
    
    handleKeyboardAppearance() {
        ResponsiveState.keyboardVisible = true;
        
        // Adjust viewport for virtual keyboard
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.classList.add('keyboard-visible');
        }
        
        // Scroll to input when keyboard appears
        setTimeout(() => {
            const messageInput = document.getElementById('message-input');
            if (messageInput) {
                messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 300);
    },
    
    handleKeyboardDisappearance() {
        ResponsiveState.keyboardVisible = false;
        
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.classList.remove('keyboard-visible');
        }
    },
    
    setupAdaptiveModal() {
        // Make modals responsive
        const modals = document.querySelectorAll('.modal, .settings-panel');
        
        modals.forEach(modal => {
            if (ResponsiveState.isMobile) {
                modal.classList.add('mobile-modal');
            }
        });
    },
    
    setupResponsiveGrid() {
        // Adjust grid layouts based on screen size
        const grids = document.querySelectorAll('.grid, .settings-grid');
        
        grids.forEach(grid => {
            this.updateGridColumns(grid);
        });
    },
    
    updateGridColumns(grid) {
        const breakpoint = ResponsiveUtils.getCurrentBreakpoint();
        
        switch (breakpoint) {
            case 'mobile':
                grid.style.gridTemplateColumns = '1fr';
                break;
            case 'tablet':
                grid.style.gridTemplateColumns = 'repeat(2, 1fr)';
                break;
            case 'desktop':
                grid.style.gridTemplateColumns = 'repeat(3, 1fr)';
                break;
        }
    },
    
    setupDynamicFontSizing() {
        // Adjust font sizes based on screen size and user preferences
        const rootFontSize = ResponsiveState.isMobile ? 14 : 16;
        document.documentElement.style.fontSize = `${rootFontSize}px`;
    }
};

// Responsive layout manager
const ResponsiveLayout = {
    init() {
        this.updateLayout();
        this.setupResizeHandler();
        this.setupOrientationHandler();
    },
    
    updateLayout() {
        const body = document.body;
        const breakpoint = ResponsiveUtils.getCurrentBreakpoint();
        
        // Update body classes
        body.classList.remove('mobile', 'tablet', 'desktop');
        body.classList.add(breakpoint);
        
        if (ResponsiveState.isTouchDevice) {
            body.classList.add('touch-device');
        }
        
        if (ResponsiveState.orientation) {
            body.classList.remove('portrait', 'landscape');
            body.classList.add(ResponsiveState.orientation);
        }
        
        // Update chat layout
        this.updateChatLayout();
        
        // Update sidebar behavior
        this.updateSidebarBehavior();
    },
    
    updateChatLayout() {
        const chatContainer = document.querySelector('.chat-container');
        const messagesContainer = document.getElementById('messages-container');
        
        if (chatContainer && messagesContainer) {
            if (ResponsiveState.isMobile) {
                // Mobile: full height, adjust for virtual keyboard
                const availableHeight = window.innerHeight - 120; // Account for input area
                messagesContainer.style.maxHeight = `${availableHeight}px`;
            } else {
                // Desktop/tablet: more flexible height
                messagesContainer.style.maxHeight = 'calc(100vh - 200px)';
            }
        }
    },
    
    updateSidebarBehavior() {
        const sidebar = document.getElementById('sidebar');
        if (!sidebar) return;
        
        if (ResponsiveState.isMobile) {
            // Mobile: overlay sidebar
            sidebar.classList.add('sidebar-overlay');
            if (ResponsiveState.sidebarOpen) {
                MobileNavigation.closeSidebar();
            }
        } else {
            // Desktop/tablet: side-by-side
            sidebar.classList.remove('sidebar-overlay');
            sidebar.classList.remove('sidebar-open');
            ResponsiveState.sidebarOpen = false;
        }
    },
    
    setupResizeHandler() {
        const handleResize = ResponsiveUtils.debounce(() => {
            ResponsiveUtils.updateState();
            this.updateLayout();
            AdaptiveUI.updateGridColumns(document.querySelector('.settings-grid'));
            
            // Trigger custom resize event
            window.dispatchEvent(new CustomEvent('responsiveResize', {
                detail: {
                    breakpoint: ResponsiveUtils.getCurrentBreakpoint(),
                    dimensions: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                }
            }));
        }, 250);
        
        window.addEventListener('resize', handleResize);
    },
    
    setupOrientationHandler() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                ResponsiveUtils.updateState();
                this.updateLayout();
            }, 100);
        });
    }
};

// Initialize responsive functionality
const ResponsiveManager = {
    init() {
        console.log('📱 Initializing responsive enhancements...');
        
        ResponsiveUtils.updateState();
        ResponsiveLayout.init();
        MobileNavigation.init();
        TouchEnhancements.init();
        AdaptiveUI.init();
        
        console.log(`✅ Responsive enhancements initialized for ${ResponsiveUtils.getCurrentBreakpoint()} device`);
    }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        ResponsiveManager.init();
    });
} else {
    ResponsiveManager.init();
}

// Export responsive utilities for global access
window.ResponsiveUtils = ResponsiveUtils;
window.ResponsiveState = ResponsiveState;
window.MobileNavigation = MobileNavigation;
window.TouchEnhancements = TouchEnhancements;
window.AdaptiveUI = AdaptiveUI;
// SecretGPTee Animations and Interactive UI Enhancement JavaScript
// Smooth animations, loading states, and visual feedback for enhanced user experience

// Animation configuration
const ANIMATION_CONFIG = {
    duration: {
        fast: 150,
        normal: 300,
        slow: 500
    },
    easing: {
        easeOut: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        easeIn: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)',
        easeInOut: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
        bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
    }
};

// Animation state management
const AnimationState = {
    activeAnimations: new Set(),
    reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
};

// Core animation utilities
const AnimationUtils = {
    // Create and manage CSS animations
    animate(element, keyframes, options = {}) {
        if (AnimationState.reducedMotion && !options.forceAnimation) {
            // Skip animations if user prefers reduced motion
            if (options.onComplete) options.onComplete();
            return;
        }
        
        const animation = element.animate(keyframes, {
            duration: options.duration || ANIMATION_CONFIG.duration.normal,
            easing: options.easing || ANIMATION_CONFIG.easing.easeOut,
            fill: options.fill || 'forwards',
            ...options
        });
        
        const animationId = Symbol('animation');
        AnimationState.activeAnimations.add(animationId);
        
        animation.addEventListener('finish', () => {
            AnimationState.activeAnimations.delete(animationId);
            if (options.onComplete) options.onComplete();
        });
        
        return animation;
    },
    
    // Fade in animation
    fadeIn(element, options = {}) {
        element.style.opacity = '0';
        element.style.display = options.display || 'block';
        
        return this.animate(element, [
            { opacity: 0 },
            { opacity: 1 }
        ], {
            duration: options.duration || ANIMATION_CONFIG.duration.normal,
            easing: options.easing || ANIMATION_CONFIG.easing.easeOut,
            onComplete: options.onComplete
        });
    },
    
    // Fade out animation
    fadeOut(element, options = {}) {
        return this.animate(element, [
            { opacity: 1 },
            { opacity: 0 }
        ], {
            duration: options.duration || ANIMATION_CONFIG.duration.normal,
            easing: options.easing || ANIMATION_CONFIG.easing.easeIn,
            onComplete: () => {
                element.style.display = 'none';
                if (options.onComplete) options.onComplete();
            }
        });
    },
    
    // Slide in from top
    slideInFromTop(element, options = {}) {
        element.style.transform = 'translateY(-100%)';
        element.style.display = options.display || 'block';
        
        return this.animate(element, [
            { transform: 'translateY(-100%)', opacity: 0 },
            { transform: 'translateY(0)', opacity: 1 }
        ], {
            duration: options.duration || ANIMATION_CONFIG.duration.normal,
            easing: options.easing || ANIMATION_CONFIG.easing.easeOut,
            onComplete: options.onComplete
        });
    },
    
    // Slide out to top
    slideOutToTop(element, options = {}) {
        return this.animate(element, [
            { transform: 'translateY(0)', opacity: 1 },
            { transform: 'translateY(-100%)', opacity: 0 }
        ], {
            duration: options.duration || ANIMATION_CONFIG.duration.normal,
            easing: options.easing || ANIMATION_CONFIG.easing.easeIn,
            onComplete: () => {
                element.style.display = 'none';
                if (options.onComplete) options.onComplete();
            }
        });
    },
    
    // Scale in animation
    scaleIn(element, options = {}) {
        element.style.transform = 'scale(0)';
        element.style.display = options.display || 'block';
        
        return this.animate(element, [
            { transform: 'scale(0)', opacity: 0 },
            { transform: 'scale(1)', opacity: 1 }
        ], {
            duration: options.duration || ANIMATION_CONFIG.duration.normal,
            easing: options.easing || ANIMATION_CONFIG.easing.bounce,
            onComplete: options.onComplete
        });
    },
    
    // Scale out animation
    scaleOut(element, options = {}) {
        return this.animate(element, [
            { transform: 'scale(1)', opacity: 1 },
            { transform: 'scale(0)', opacity: 0 }
        ], {
            duration: options.duration || ANIMATION_CONFIG.duration.fast,
            easing: options.easing || ANIMATION_CONFIG.easing.easeIn,
            onComplete: () => {
                element.style.display = 'none';
                if (options.onComplete) options.onComplete();
            }
        });
    },
    
    // Shake animation for errors
    shake(element, options = {}) {
        return this.animate(element, [
            { transform: 'translateX(0)' },
            { transform: 'translateX(-10px)' },
            { transform: 'translateX(10px)' },
            { transform: 'translateX(-10px)' },
            { transform: 'translateX(10px)' },
            { transform: 'translateX(0)' }
        ], {
            duration: options.duration || 500,
            easing: 'ease-in-out',
            onComplete: options.onComplete
        });
    },
    
    // Pulse animation for attention
    pulse(element, options = {}) {
        return this.animate(element, [
            { transform: 'scale(1)' },
            { transform: 'scale(1.05)' },
            { transform: 'scale(1)' }
        ], {
            duration: options.duration || 1000,
            easing: 'ease-in-out',
            iterations: options.iterations || 3,
            onComplete: options.onComplete
        });
    },
    
    // Typing indicator animation
    startTypingAnimation(element) {
        if (!element) return;
        
        element.innerHTML = `
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        `;
        
        const dots = element.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            this.animate(dot, [
                { opacity: 0.3 },
                { opacity: 1 },
                { opacity: 0.3 }
            ], {
                duration: 1400,
                delay: index * 200,
                iterations: Infinity,
                easing: 'ease-in-out'
            });
        });
    },
    
    // Stop typing animation
    stopTypingAnimation(element) {
        if (!element) return;
        element.innerHTML = '';
    }
};

// Loading states and spinners
const LoadingAnimations = {
    // Create spinning loader
    createSpinner(size = 'medium', color = 'primary') {
        const spinner = document.createElement('div');
        spinner.className = `spinner spinner-${size} spinner-${color}`;
        spinner.innerHTML = '<div class="spinner-circle"></div>';
        return spinner;
    },
    
    // Show loading overlay
    showOverlay(message = 'Loading...', container = document.body) {
        let overlay = container.querySelector('.loading-overlay');
        
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-content">
                    ${this.createSpinner('large').outerHTML}
                    <div class="loading-message">${message}</div>
                </div>
            `;
            container.appendChild(overlay);
        }
        
        overlay.querySelector('.loading-message').textContent = message;
        AnimationUtils.fadeIn(overlay);
        
        return overlay;
    },
    
    // Hide loading overlay
    hideOverlay(container = document.body) {
        const overlay = container.querySelector('.loading-overlay');
        if (overlay) {
            AnimationUtils.fadeOut(overlay, {
                onComplete: () => overlay.remove()
            });
        }
    },
    
    // Show inline loading
    showInlineLoading(element, message = '') {
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        
        const spinner = this.createSpinner('small');
        element.innerHTML = `${spinner.outerHTML} ${message}`;
        element.disabled = true;
        
        return originalContent;
    },
    
    // Hide inline loading
    hideInlineLoading(element) {
        const originalContent = element.dataset.originalContent;
        if (originalContent) {
            element.innerHTML = originalContent;
            delete element.dataset.originalContent;
        }
        element.disabled = false;
    },
    
    // Progress bar animation
    animateProgress(progressBar, targetPercent, duration = 1000) {
        const startPercent = parseInt(progressBar.style.width) || 0;
        const progressDiff = targetPercent - startPercent;
        
        return AnimationUtils.animate(progressBar, [
            { width: `${startPercent}%` },
            { width: `${targetPercent}%` }
        ], {
            duration: duration,
            easing: ANIMATION_CONFIG.easing.easeOut,
            onComplete: () => {
                progressBar.style.width = `${targetPercent}%`;
                progressBar.setAttribute('aria-valuenow', targetPercent);
            }
        });
    }
};

// Interactive feedback animations
const InteractiveAnimations = {
    // Button click feedback
    buttonClick(button) {
        if (!button) return;
        
        // Add ripple effect
        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        button.appendChild(ripple);
        
        AnimationUtils.animate(ripple, [
            { transform: 'scale(0)', opacity: 1 },
            { transform: 'scale(2)', opacity: 0 }
        ], {
            duration: 600,
            easing: 'ease-out',
            onComplete: () => ripple.remove()
        });
        
        // Button scale feedback
        AnimationUtils.animate(button, [
            { transform: 'scale(1)' },
            { transform: 'scale(0.95)' },
            { transform: 'scale(1)' }
        ], {
            duration: 150,
            easing: 'ease-out'
        });
    },
    
    // Input field focus animation
    inputFocus(input) {
        const parent = input.parentElement;
        if (parent) {
            parent.classList.add('input-focused');
            
            // Animate label if present
            const label = parent.querySelector('label');
            if (label) {
                AnimationUtils.animate(label, [
                    { transform: 'translateY(0) scale(1)' },
                    { transform: 'translateY(-20px) scale(0.8)' }
                ], {
                    duration: 200,
                    easing: ANIMATION_CONFIG.easing.easeOut
                });
            }
        }
    },
    
    // Input field blur animation
    inputBlur(input) {
        const parent = input.parentElement;
        if (parent && !input.value.trim()) {
            parent.classList.remove('input-focused');
            
            // Animate label back if present
            const label = parent.querySelector('label');
            if (label) {
                AnimationUtils.animate(label, [
                    { transform: 'translateY(-20px) scale(0.8)' },
                    { transform: 'translateY(0) scale(1)' }
                ], {
                    duration: 200,
                    easing: ANIMATION_CONFIG.easing.easeOut
                });
            }
        }
    },
    
    // Hover effects
    addHoverEffect(element, options = {}) {
        element.addEventListener('mouseenter', () => {
            if (!AnimationState.reducedMotion) {
                AnimationUtils.animate(element, [
                    { transform: 'translateY(0)' },
                    { transform: 'translateY(-2px)' }
                ], {
                    duration: options.duration || 200,
                    easing: ANIMATION_CONFIG.easing.easeOut
                });
            }
        });
        
        element.addEventListener('mouseleave', () => {
            if (!AnimationState.reducedMotion) {
                AnimationUtils.animate(element, [
                    { transform: 'translateY(-2px)' },
                    { transform: 'translateY(0)' }
                ], {
                    duration: options.duration || 200,
                    easing: ANIMATION_CONFIG.easing.easeOut
                });
            }
        });
    },
    
    // Success animation
    showSuccess(element) {
        // Add success class for styling
        element.classList.add('success-animation');
        
        // Scale and glow animation
        AnimationUtils.animate(element, [
            { transform: 'scale(1)', filter: 'brightness(1)' },
            { transform: 'scale(1.02)', filter: 'brightness(1.1)' },
            { transform: 'scale(1)', filter: 'brightness(1)' }
        ], {
            duration: 600,
            easing: ANIMATION_CONFIG.easing.easeOut,
            onComplete: () => {
                setTimeout(() => element.classList.remove('success-animation'), 2000);
            }
        });
    },
    
    // Error animation
    showError(element) {
        // Add error class for styling
        element.classList.add('error-animation');
        
        // Shake and highlight
        AnimationUtils.shake(element, {
            onComplete: () => {
                setTimeout(() => element.classList.remove('error-animation'), 2000);
            }
        });
    }
};

// Message animations for chat interface
const MessageAnimations = {
    // Animate new message appearance
    animateNewMessage(messageElement) {
        if (!messageElement) return;
        
        // Start invisible and slightly offset
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        // Animate in
        AnimationUtils.animate(messageElement, [
            { opacity: 0, transform: 'translateY(20px)' },
            { opacity: 1, transform: 'translateY(0)' }
        ], {
            duration: ANIMATION_CONFIG.duration.normal,
            easing: ANIMATION_CONFIG.easing.easeOut
        });
    },
    
    // Animate message streaming (typing effect)
    startStreamingAnimation(messageElement) {
        if (!messageElement) return;
        
        messageElement.classList.add('streaming-message');
        
        // Add cursor animation
        const cursor = document.createElement('span');
        cursor.className = 'streaming-cursor';
        cursor.textContent = '|';
        messageElement.appendChild(cursor);
        
        // Animate cursor
        AnimationUtils.animate(cursor, [
            { opacity: 1 },
            { opacity: 0 }
        ], {
            duration: 1000,
            iterations: Infinity,
            direction: 'alternate',
            easing: 'ease-in-out'
        });
    },
    
    // Stop streaming animation
    stopStreamingAnimation(messageElement) {
        if (!messageElement) return;
        
        messageElement.classList.remove('streaming-message');
        
        const cursor = messageElement.querySelector('.streaming-cursor');
        if (cursor) {
            cursor.remove();
        }
    },
    
    // Animate message deletion
    animateMessageDeletion(messageElement, onComplete) {
        if (!messageElement) return;
        
        AnimationUtils.animate(messageElement, [
            { opacity: 1, transform: 'translateX(0) scale(1)' },
            { opacity: 0, transform: 'translateX(-50px) scale(0.8)' }
        ], {
            duration: ANIMATION_CONFIG.duration.normal,
            easing: ANIMATION_CONFIG.easing.easeIn,
            onComplete: () => {
                messageElement.remove();
                if (onComplete) onComplete();
            }
        });
    }
};

// Toast notification animations
const ToastAnimations = {
    // Show toast with slide-in animation
    showToast(toastElement) {
        if (!toastElement) return;
        
        // Start from right side
        toastElement.style.transform = 'translateX(100%)';
        toastElement.style.opacity = '0';
        
        AnimationUtils.animate(toastElement, [
            { transform: 'translateX(100%)', opacity: 0 },
            { transform: 'translateX(0)', opacity: 1 }
        ], {
            duration: ANIMATION_CONFIG.duration.normal,
            easing: ANIMATION_CONFIG.easing.easeOut
        });
    },
    
    // Hide toast with slide-out animation
    hideToast(toastElement, onComplete) {
        if (!toastElement) return;
        
        AnimationUtils.animate(toastElement, [
            { transform: 'translateX(0)', opacity: 1 },
            { transform: 'translateX(100%)', opacity: 0 }
        ], {
            duration: ANIMATION_CONFIG.duration.fast,
            easing: ANIMATION_CONFIG.easing.easeIn,
            onComplete: () => {
                toastElement.remove();
                if (onComplete) onComplete();
            }
        });
    }
};

// Auto-setup animations on common elements
const AutoAnimations = {
    init() {
        this.setupButtonAnimations();
        this.setupInputAnimations();
        this.setupHoverEffects();
        this.setupScrollAnimations();
    },
    
    setupButtonAnimations() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn, [role="button"]')) {
                InteractiveAnimations.buttonClick(e.target);
            }
        });
    },
    
    setupInputAnimations() {
        document.addEventListener('focus', (e) => {
            if (e.target.matches('input, textarea')) {
                InteractiveAnimations.inputFocus(e.target);
            }
        }, true);
        
        document.addEventListener('blur', (e) => {
            if (e.target.matches('input, textarea')) {
                InteractiveAnimations.inputBlur(e.target);
            }
        }, true);
    },
    
    setupHoverEffects() {
        // Add hover effects to cards and interactive elements
        const hoverElements = document.querySelectorAll('.card, .message-wrapper, .settings-tab');
        hoverElements.forEach(element => {
            InteractiveAnimations.addHoverEffect(element);
        });
    },
    
    setupScrollAnimations() {
        // Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        // Observe elements that should animate on scroll
        const animateOnScroll = document.querySelectorAll('.animate-on-scroll');
        animateOnScroll.forEach(element => observer.observe(element));
    }
};

// Initialize animations when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        AutoAnimations.init();
    });
} else {
    AutoAnimations.init();
}

// Listen for reduced motion preference changes
window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
    AnimationState.reducedMotion = e.matches;
    console.log(`Reduced motion preference: ${e.matches ? 'enabled' : 'disabled'}`);
});

// Export animations for global access
window.AnimationUtils = AnimationUtils;
window.LoadingAnimations = LoadingAnimations;
window.InteractiveAnimations = InteractiveAnimations;
window.MessageAnimations = MessageAnimations;
window.ToastAnimations = ToastAnimations;
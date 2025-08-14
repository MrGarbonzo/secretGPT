// SecretJS Browser Wrapper
// This file creates global variables from the ESM bundle

(function() {
    'use strict';
    
    console.log('SecretJS wrapper loading...');
    
    // Check what's available in the global scope after secretjs loads
    const checkGlobals = () => {
        console.log('🔍 Debugging SecretJS wrapper...');
        
        // Log all window properties that might be related to secretjs
        const allGlobals = Object.keys(window);
        const secretRelated = allGlobals.filter(key => 
            key.toLowerCase().includes('secret') || 
            key.includes('$') || 
            key.includes('browser') ||
            key.includes('export') ||
            key.includes('module')
        );
        console.log('All secret-related globals:', secretRelated);
        
        // Check for any object that might contain SecretNetworkClient
        for (const key of allGlobals) {
            try {
                const obj = window[key];
                if (obj && typeof obj === 'object') {
                    if (obj.SecretNetworkClient) {
                        console.log(`🎯 Found SecretNetworkClient in window.${key}`);
                        window.SecretNetworkClient = obj.SecretNetworkClient;
                        console.log('✅ SecretNetworkClient exposed globally from', key);
                        return true;
                    }
                    if (obj.exports && obj.exports.SecretNetworkClient) {
                        console.log(`🎯 Found SecretNetworkClient in window.${key}.exports`);
                        window.SecretNetworkClient = obj.exports.SecretNetworkClient;
                        console.log('✅ SecretNetworkClient exposed globally from exports');
                        return true;
                    }
                }
            } catch (e) {
                // Skip objects that can't be accessed
            }
        }
        
        // Check if it's already available but not detected
        if (typeof window.SecretNetworkClient !== 'undefined') {
            console.log('✅ SecretNetworkClient already available globally');
            return true;
        }
        
        console.log('❌ SecretNetworkClient not found in any globals');
        return false;
    };
    
    // Try immediately
    if (!checkGlobals()) {
        // Try again after a short delay
        setTimeout(() => {
            if (!checkGlobals()) {
                console.error('❌ Could not find SecretJS exports');
                console.log('Available globals:', Object.keys(window).slice(0, 20));
            }
        }, 100);
    }
    
})();

// UMD should expose SecretNetworkClient directly
// If it doesn't work, try loading from jsDelivr
setTimeout(() => {
    if (typeof SecretNetworkClient === 'undefined') {
        console.warn('⚠️ UMD SecretJS failed, attempting jsDelivr fallback...');
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/secretjs@1.15.1/dist/secretjs.umd.min.js';
        script.onload = () => {
            setTimeout(() => {
                if (typeof SecretNetworkClient !== 'undefined') {
                    console.log('✅ SecretJS loaded from jsDelivr fallback');
                } else {
                    console.error('❌ All SecretJS loading methods failed');
                }
            }, 100);
        };
        script.onerror = () => {
            console.error('❌ jsDelivr fallback also failed');
        };
        
        document.head.appendChild(script);
    }
}, 1000);
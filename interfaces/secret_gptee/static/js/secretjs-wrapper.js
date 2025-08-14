// SecretJS Browser Wrapper
// This file creates global variables from the ESM bundle

(function() {
    'use strict';
    
    console.log('SecretJS wrapper loading...');
    
    // Check what's available in the global scope after secretjs loads
    const checkGlobals = () => {
        console.log('Checking for SecretJS exports...');
        
        // List of possible global variable names where SecretJS might be exposed
        const possibleNames = [
            'browser$1',
            'secretjs', 
            'SecretJS',
            'module',
            'exports',
            '__SECRETJS_EXPORTS__'
        ];
        
        for (const name of possibleNames) {
            if (typeof window[name] !== 'undefined') {
                console.log(`Found global: ${name}`, window[name]);
                
                // Check if it has exports
                if (window[name] && window[name].exports) {
                    console.log(`${name}.exports found:`, Object.keys(window[name].exports));
                    
                    const exports = window[name].exports;
                    if (exports.SecretNetworkClient) {
                        window.SecretNetworkClient = exports.SecretNetworkClient;
                        console.log('✅ SecretNetworkClient exposed globally');
                        return true;
                    }
                }
                
                // Check if it directly contains SecretNetworkClient
                if (window[name] && window[name].SecretNetworkClient) {
                    window.SecretNetworkClient = window[name].SecretNetworkClient;
                    console.log('✅ SecretNetworkClient found and exposed');
                    return true;
                }
            }
        }
        
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

// Fallback: Use CDN if local loading fails completely
setTimeout(() => {
    if (typeof SecretNetworkClient === 'undefined') {
        console.warn('⚠️ Local SecretJS failed, attempting CDN fallback...');
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/secretjs@1.15.1/+esm';
        script.type = 'module';
        script.onload = () => {
            console.log('✅ SecretJS loaded from CDN fallback');
        };
        script.onerror = () => {
            console.error('❌ CDN fallback also failed');
        };
        
        document.head.appendChild(script);
    }
}, 500);
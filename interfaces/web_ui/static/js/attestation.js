// secretGPT Web UI - Attestation JavaScript

class AttestationManager {
    constructor() {
        this.API_BASE = '/api/v1';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeProgressiveDisclosure();
    }

    setupEventListeners() {
        // Self VM verification
        const verifySelfButton = document.getElementById('verify-self-vm');
        if (verifySelfButton) {
            verifySelfButton.addEventListener('click', () => this.verifySelfVM());
        }

        // Secret AI VM verification
        const verifySecretAIButton = document.getElementById('verify-secretai-vm');
        if (verifySecretAIButton) {
            verifySecretAIButton.addEventListener('click', () => this.verifySecretAIVM());
        }

        // Both VMs verification
        const verifyBothButton = document.getElementById('verify-both-vms');
        if (verifyBothButton) {
            verifyBothButton.addEventListener('click', () => this.verifyBothVMs());
        }

        // Proof verification form
        const proofForm = document.getElementById('proof-verify-form');
        if (proofForm) {
            proofForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.verifyProof();
            });
        }
    }

    async verifySelfVM() {
        this.setLoadingState('self-vm', true);
        
        try {
            const response = await fetch(`${this.API_BASE}/attestation/self`);
            const data = await response.json();
            
            if (data.success) {
                this.displayAttestationData('self', data.attestation);
                this.updateVMStatus('self-vm', 'verified');
            } else {
                throw new Error(data.error || 'Verification failed');
            }
        } catch (error) {
            console.error('Self VM verification failed:', error);
            this.showError('self-vm', error.message);
            this.updateVMStatus('self-vm', 'error');
        } finally {
            this.setLoadingState('self-vm', false);
        }
    }

    async verifySecretAIVM() {
        this.setLoadingState('secretai-vm', true);
        
        try {
            const response = await fetch(`${this.API_BASE}/attestation/secret-ai`);
            const data = await response.json();
            
            if (data.success) {
                this.displayAttestationData('secretai', data.attestation);
                this.updateVMStatus('secretai-vm', 'verified');
            } else {
                throw new Error(data.error || 'Verification failed');
            }
        } catch (error) {
            console.error('Secret AI VM verification failed:', error);
            this.showError('secretai-vm', error.message);
            this.updateVMStatus('secretai-vm', 'error');
        } finally {
            this.setLoadingState('secretai-vm', false);
        }
    }

    async verifyBothVMs() {
        // Verify both VMs concurrently
        await Promise.all([
            this.verifySelfVM(),
            this.verifySecretAIVM()
        ]);
    }

    displayAttestationData(vmType, attestation) {
        const detailsDiv = document.getElementById(`${vmType}-vm-details`);
        if (!detailsDiv) return;

        // Update all attestation fields
        this.updateField(`${vmType}-mrtd`, attestation.mrtd);
        this.updateField(`${vmType}-rtmr0`, attestation.rtmr0);
        this.updateField(`${vmType}-rtmr1`, attestation.rtmr1);
        this.updateField(`${vmType}-rtmr2`, attestation.rtmr2);
        this.updateField(`${vmType}-rtmr3`, attestation.rtmr3);
        this.updateField(`${vmType}-report-data`, attestation.report_data);
        this.updateField(`${vmType}-cert-fingerprint`, attestation.certificate_fingerprint);
        
        // Format timestamp
        const timestamp = new Date(attestation.timestamp).toLocaleString();
        this.updateField(`${vmType}-timestamp`, timestamp);

        // Show details
        detailsDiv.style.display = 'block';
    }

    updateField(fieldId, value) {
        const element = document.getElementById(fieldId);
        if (element) {
            element.textContent = value || '-';
        }
    }

    updateVMStatus(vmId, status) {
        const statusIcon = document.getElementById(`${vmId}-status`);
        const statusText = document.getElementById(`${vmId}-text`);
        const vmBox = document.getElementById(`${vmId}-box`);
        
        if (statusIcon && statusText && vmBox) {
            switch (status) {
                case 'verified':
                    statusIcon.className = 'fas fa-circle text-success';
                    statusText.textContent = 'Verified';
                    vmBox.classList.add('verified');
                    vmBox.classList.remove('error');
                    break;
                case 'error':
                    statusIcon.className = 'fas fa-circle text-danger';
                    statusText.textContent = 'Verification Failed';
                    vmBox.classList.add('error');
                    vmBox.classList.remove('verified');
                    break;
                default:
                    statusIcon.className = 'fas fa-circle text-secondary';
                    statusText.textContent = 'Not Verified';
                    vmBox.classList.remove('verified', 'error');
            }
        }
    }

    setLoadingState(vmType, loading) {
        const loadingDiv = document.getElementById(`${vmType}-loading`);
        const detailsDiv = document.getElementById(`${vmType}-details`);
        const errorDiv = document.getElementById(`${vmType}-error`);
        
        if (loading) {
            if (loadingDiv) loadingDiv.style.display = 'block';
            if (detailsDiv) detailsDiv.style.display = 'none';
            if (errorDiv) errorDiv.style.display = 'none';
        } else {
            if (loadingDiv) loadingDiv.style.display = 'none';
        }
    }

    showError(vmType, message) {
        const errorDiv = document.getElementById(`${vmType}-error`);
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    async verifyProof() {
        const fileInput = document.getElementById('proof-file');
        const passwordInput = document.getElementById('proof-verify-password');
        const resultsDiv = document.getElementById('proof-results');
        const contentDiv = document.getElementById('proof-content');
        
        if (!fileInput.files[0] || !passwordInput.value) {
            alert('Please select a proof file and enter the password.');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', passwordInput.value);

        try {
            const response = await fetch(`${this.API_BASE}/proof/verify`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success && data.verified) {
                this.displayProofResults(data.proof_data, contentDiv);
                resultsDiv.style.display = 'block';
                this.showAlert('Proof verified successfully!', 'success');
            } else {
                throw new Error(data.error || 'Proof verification failed');
            }
        } catch (error) {
            console.error('Proof verification error:', error);
            this.showAlert(`Proof verification failed: ${error.message}`, 'danger');
        }

        // Clear form
        fileInput.value = '';
        passwordInput.value = '';
    }

    displayProofResults(proofData, container) {
        const html = `
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-check-circle text-success"></i> Verified Proof</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Interaction</h6>
                            <div class="mb-2">
                                <strong>Question:</strong>
                                <div class="border p-2 bg-light">${this.escapeHtml(proofData.interaction.question)}</div>
                            </div>
                            <div class="mb-2">
                                <strong>Answer:</strong>
                                <div class="border p-2 bg-light">${this.escapeHtml(proofData.interaction.answer)}</div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Attestation Verification</h6>
                            <div class="mb-2">
                                <strong>Dual VM:</strong>
                                <span class="badge bg-success">${proofData.attestation.dual_attestation ? 'Verified' : 'Failed'}</span>
                            </div>
                            <div class="mb-2">
                                <strong>Timestamp:</strong>
                                <code>${new Date(proofData.timestamp).toLocaleString()}</code>
                            </div>
                            <div class="mb-2">
                                <strong>Generator:</strong>
                                <code>${proofData.metadata.generator}</code>
                            </div>
                            <div class="mb-2">
                                <strong>Version:</strong>
                                <code>${proofData.version}</code>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    initializeProgressiveDisclosure() {
        this.progressiveDisclosure = {
            levels: {
                mrtd: 1,
                rtmr: 1,
                report: 1,
                cert: 1,
                infra: 1
            },
            
            toggleLevel(topic, targetLevel, element) {
                const content = element.querySelector('.level-content');
                const icon = element.querySelector('.expand-icon');
                const isExpanded = content.classList.contains('show');
                
                if (isExpanded) {
                    // Collapse current level
                    content.classList.remove('show');
                    icon.classList.remove('rotated');
                    element.classList.remove('active');
                } else {
                    // Collapse any other open levels in this topic
                    document.querySelectorAll(`[data-topic="${topic}"]`).forEach(otherLevel => {
                        const otherContent = otherLevel.querySelector('.level-content');
                        const otherIcon = otherLevel.querySelector('.expand-icon');
                        if (otherContent && otherContent.classList.contains('show')) {
                            otherContent.classList.remove('show');
                            otherIcon.classList.remove('rotated');
                            otherLevel.classList.remove('active');
                        }
                    });
                    
                    // Expand current level
                    content.classList.add('show');
                    icon.classList.add('rotated');
                    element.classList.add('active');
                    
                    // Update current level and unlock next level
                    this.levels[topic] = targetLevel;
                    this.unlockNextLevel(topic, targetLevel);
                    
                    // Update technical data if available
                    window.attestationManager.updateTechnicalData(topic, targetLevel);
                }
            },
            
            unlockNextLevel(topic, currentLevel) {
                const nextLevel = currentLevel + 1;
                const nextElement = document.querySelector(`[data-topic="${topic}"][data-level="${nextLevel}"]`);
                
                if (nextElement && nextElement.classList.contains('locked')) {
                    nextElement.classList.remove('locked');
                    
                    // Add a subtle animation to highlight the newly unlocked level
                    nextElement.style.opacity = '0.5';
                    setTimeout(() => {
                        nextElement.style.transition = 'opacity 0.5s ease';
                        nextElement.style.opacity = '1';
                    }, 100);
                }
            }
        };
        
        // Add click handlers to drill-down levels
        document.querySelectorAll('.drill-down-level').forEach(level => {
            level.addEventListener('click', (e) => {
                const topic = level.dataset.topic;
                const targetLevel = parseInt(level.dataset.level);
                const isLocked = level.classList.contains('locked');
                
                if (!isLocked) {
                    this.progressiveDisclosure.toggleLevel(topic, targetLevel, level);
                }
            });
        });
    }
    
    updateTechnicalData(topic, level) {
        if (level === 3) {
            // Update technical data with real values when available
            if (topic === 'mrtd') {
                const mrtdElement = document.getElementById('current-mrtd');
                const selfMrtd = document.getElementById('self-mrtd');
                if (selfMrtd && selfMrtd.textContent !== '-') {
                    mrtdElement.textContent = selfMrtd.textContent;
                }
            } else if (topic === 'rtmr') {
                const rtmrElement = document.getElementById('current-rtmr');
                const rtmr0 = document.getElementById('self-rtmr0');
                const rtmr1 = document.getElementById('self-rtmr1');
                if (rtmr0 && rtmr0.textContent !== '-') {
                    rtmrElement.innerHTML = `
                        RTMR0: ${rtmr0.textContent}<br>
                        RTMR1: ${rtmr1.textContent}<br>
                        RTMR2: ${document.getElementById('self-rtmr2').textContent}<br>
                        RTMR3: ${document.getElementById('self-rtmr3').textContent}
                    `;
                }
            } else if (topic === 'report') {
                const reportElement = document.getElementById('current-report');
                const selfReport = document.getElementById('self-report-data');
                if (selfReport && selfReport.textContent !== '-') {
                    reportElement.textContent = selfReport.textContent;
                }
            } else if (topic === 'cert') {
                const certElement = document.getElementById('current-cert');
                const selfCert = document.getElementById('self-cert-fingerprint');
                if (selfCert && selfCert.textContent !== '-') {
                    certElement.textContent = selfCert.textContent;
                }
            }
        }
    }
}

// Hash Timeline Functions
function expandHashTimeline() {
    document.getElementById('hash-explainer-compact').style.display = 'none';
    document.getElementById('hash-timeline-expanded').style.display = 'block';
    
    // Smooth scroll to expanded content with slight delay for better UX
    setTimeout(() => {
        document.getElementById('hash-timeline-expanded').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }, 100);
}

function collapseHashTimeline() {
    document.getElementById('hash-timeline-expanded').style.display = 'none';
    document.getElementById('hash-explainer-compact').style.display = 'block';
    
    // Smooth scroll back to the section header
    document.getElementById('hash-generation-section').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

function toggleVerticalDetails(step) {
    const details = document.getElementById(`v-details-${step}`);
    const isVisible = details.style.display !== 'none';
    
    details.style.display = isVisible ? 'none' : 'block';
}

// Verification Process Functions
function expandVerificationProcess() {
    document.getElementById('verification-explainer-compact').style.display = 'none';
    document.getElementById('verification-process-expanded').style.display = 'block';
    
    // Smooth scroll to expanded content with slight delay for better UX
    setTimeout(() => {
        document.getElementById('verification-process-expanded').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }, 100);
}

function collapseVerificationProcess() {
    document.getElementById('verification-process-expanded').style.display = 'none';
    document.getElementById('verification-explainer-compact').style.display = 'block';
    
    // Smooth scroll back to the section header
    document.getElementById('verification-generation-section').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Initialize attestation manager
document.addEventListener('DOMContentLoaded', () => {
    window.attestationManager = new AttestationManager();
});
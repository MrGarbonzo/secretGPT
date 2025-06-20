// secretGPT Web UI - Attestation JavaScript

class AttestationManager {
    constructor() {
        this.API_BASE = '/api/v1';
        this.init();
    }

    init() {
        this.setupEventListeners();
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
}

// Initialize attestation manager
document.addEventListener('DOMContentLoaded', () => {
    window.attestationManager = new AttestationManager();
});
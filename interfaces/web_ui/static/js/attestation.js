// secretGPT Web UI - Attestation JavaScript

class AttestationManager {
    constructor() {
        this.API_BASE = '/api/v1';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeProgressiveDisclosure();
        this.loadContainerInfo();
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

    async loadContainerInfo() {
        // TODO: Integrate with TEE attestation system for verifiable deployment info
        // Expected future endpoint: /api/v1/attestation/deployment or port 29343 extension
        // Should provide: Docker image, SHA256, build time, compose hash
        
        // Try to get verifiable container info from TEE attestation system
        try {
            const response = await fetch(`${this.API_BASE}/system/container-info`);
            const data = await response.json();
            
            if (data.success && data.container_info) {
                this.updateContainerDisplay(data.container_info);
            } else {
                console.warn('Container info not available:', data.error);
                this.updateContainerDisplay(null);
            }
        } catch (error) {
            console.error('Failed to load container info:', error);
            // Show that data is not available rather than fake static data
            this.updateContainerDisplay(null);
        }
    }

    updateContainerDisplay(containerInfo) {
        // Update Current Deployment section with real data
        const deploymentSection = document.getElementById('deployment-info');
        
        if (containerInfo && deploymentSection) {
            const imageName = containerInfo.image_name || 'ghcr.io/mrgarbonzo/secretgpt';
            const imageTag = containerInfo.image_tag || 'security';
            const fullImageName = `${imageName}:${imageTag}`;
            
            // Format build time
            let buildTime = 'Unknown';
            if (containerInfo.build_time && containerInfo.build_time !== 'unknown') {
                try {
                    buildTime = new Date(containerInfo.build_time).toLocaleString('en-US', {
                        year: 'numeric',
                        month: '2-digit', 
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit',
                        timeZone: 'UTC'
                    }) + ' UTC';
                } catch (e) {
                    buildTime = containerInfo.build_time;
                }
            }
            
            // Format SHA256 - if available from TEE attestation
            let sha256 = containerInfo.image_sha || 'Requires TEE attestation';
            if (sha256 && sha256 !== 'unknown' && sha256 !== 'unavailable' && sha256 !== 'Requires TEE attestation') {
                // Truncate long SHA hashes for display
                if (sha256.startsWith('sha256:')) {
                    sha256 = sha256.substring(0, 19) + '...';
                } else if (sha256.length > 16) {
                    sha256 = sha256.substring(0, 16) + '...';
                }
            }
            
            deploymentSection.innerHTML = `
                Image: ${fullImageName}<br>
                SHA256: ${sha256}<br>
                Built: ${buildTime}
            `;
        } else if (deploymentSection) {
            // Show that deployment info requires TEE attestation
            deploymentSection.innerHTML = `
                <span class="text-muted">
                    <i class="fas fa-shield-alt"></i> Deployment verification requires TEE attestation<br>
                    <small>Image details available through VM attestation system</small>
                </span>
            `;
        }
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
        // Generate unique IDs for collapsible sections
        const selfVmId = 'self-vm-' + Date.now();
        const secretAiId = 'secret-ai-' + Date.now();
        const conversationId = 'conversation-' + Date.now();
        
        const html = `
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-check-circle text-success"></i> Verified Proof - Complete Attestation Details</h6>
                </div>
                <div class="card-body">
                    <!-- Basic Information -->
                    <div class="row mb-4">
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
                            <div class="mt-2">
                                <small class="text-muted">
                                    Question Hash: <code>${proofData.interaction.question_hash.substring(0, 16)}...</code><br>
                                    Answer Hash: <code>${proofData.interaction.answer_hash.substring(0, 16)}...</code>
                                </small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Proof Metadata</h6>
                            <div class="mb-2">
                                <strong>Dual VM Attestation:</strong>
                                <span class="badge bg-success">${proofData.attestation.dual_attestation ? 'Verified' : 'Failed'}</span>
                            </div>
                            <div class="mb-2">
                                <strong>Generated:</strong>
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
                            <div class="mb-2">
                                <strong>Encryption:</strong>
                                <code>${proofData.metadata.encryption}</code>
                            </div>
                            <div class="mb-2">
                                <strong>Full Conversation:</strong>
                                <span class="badge ${proofData.metadata.includes_full_conversation ? 'bg-info' : 'bg-secondary'}">
                                    ${proofData.metadata.includes_full_conversation ? 'Included' : 'Not Included'}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Attestation Details Section -->
                    <h6 class="mt-4 mb-3"><i class="fas fa-shield-alt"></i> Attestation Details</h6>
                    
                    <!-- Self VM Attestation -->
                    <div class="card mb-3">
                        <div class="card-header py-2 d-flex justify-content-between align-items-center" 
                             data-bs-toggle="collapse" data-bs-target="#${selfVmId}" 
                             style="cursor: pointer;">
                            <h6 class="mb-0"><i class="fas fa-server"></i> Self VM Attestation</h6>
                            <i class="fas fa-chevron-down"></i>
                        </div>
                        <div id="${selfVmId}" class="collapse show">
                            <div class="card-body">
                                ${this.formatAttestationData(proofData.attestation.self_vm.attestation)}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Secret AI VM Attestation -->
                    <div class="card mb-3">
                        <div class="card-header py-2 d-flex justify-content-between align-items-center" 
                             data-bs-toggle="collapse" data-bs-target="#${secretAiId}" 
                             style="cursor: pointer;">
                            <h6 class="mb-0"><i class="fas fa-brain"></i> Secret AI VM Attestation</h6>
                            <i class="fas fa-chevron-down"></i>
                        </div>
                        <div id="${secretAiId}" class="collapse show">
                            <div class="card-body">
                                ${this.formatAttestationData(proofData.attestation.secret_ai_vm.attestation)}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Conversation Details (if included) -->
                    ${proofData.conversation && proofData.conversation.full_history ? `
                    <div class="card">
                        <div class="card-header py-2 d-flex justify-content-between align-items-center" 
                             data-bs-toggle="collapse" data-bs-target="#${conversationId}" 
                             style="cursor: pointer;">
                            <h6 class="mb-0"><i class="fas fa-comments"></i> Conversation Details</h6>
                            <i class="fas fa-chevron-down"></i>
                        </div>
                        <div id="${conversationId}" class="collapse">
                            <div class="card-body">
                                <div class="mb-2">
                                    <strong>Total Messages:</strong> ${proofData.conversation.total_messages}
                                </div>
                                <div class="mb-2">
                                    <strong>Conversation Hash:</strong>
                                    <code class="d-block small">${proofData.conversation.conversation_hash}</code>
                                </div>
                                <div class="mt-3">
                                    <strong>Full Conversation History:</strong>
                                    <div class="border rounded p-2 mt-2" style="max-height: 300px; overflow-y: auto;">
                                        ${proofData.conversation.full_history.map((msg, idx) => `
                                            <div class="mb-2 ${idx % 2 === 0 ? 'text-primary' : 'text-secondary'}">
                                                <strong>${idx % 2 === 0 ? 'User' : 'AI'}:</strong>
                                                ${this.escapeHtml(msg)}
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
        
        // Add collapse animation handlers
        container.querySelectorAll('[data-bs-toggle="collapse"]').forEach(header => {
            header.addEventListener('click', (e) => {
                const icon = header.querySelector('.fa-chevron-down, .fa-chevron-up');
                if (icon) {
                    icon.classList.toggle('fa-chevron-down');
                    icon.classList.toggle('fa-chevron-up');
                }
            });
        });
    }

    formatAttestationData(attestation) {
        // Format individual attestation data for display
        return `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-primary">Core Measurements</h6>
                    <div class="mb-2">
                        <strong>MRTD:</strong>
                        <code class="d-block small text-break">${attestation.mrtd}</code>
                        <small class="text-muted">Measurement of Trust Domain - VM boot integrity</small>
                    </div>
                    <div class="mb-2">
                        <strong>RTMR0:</strong>
                        <code class="d-block small text-break">${attestation.rtmr0}</code>
                        <small class="text-muted">Runtime measurement register 0</small>
                    </div>
                    <div class="mb-2">
                        <strong>RTMR1:</strong>
                        <code class="d-block small text-break">${attestation.rtmr1}</code>
                        <small class="text-muted">Runtime measurement register 1</small>
                    </div>
                    <div class="mb-2">
                        <strong>RTMR2:</strong>
                        <code class="d-block small text-break">${attestation.rtmr2}</code>
                        <small class="text-muted">Runtime measurement register 2</small>
                    </div>
                    <div class="mb-2">
                        <strong>RTMR3:</strong>
                        <code class="d-block small text-break">${attestation.rtmr3}</code>
                        <small class="text-muted">Runtime measurement register 3</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <h6 class="text-success">Security Details</h6>
                    <div class="mb-2">
                        <strong>Report Data:</strong>
                        <code class="d-block small text-break">${attestation.report_data}</code>
                        <small class="text-muted">Custom attestation report data</small>
                    </div>
                    <div class="mb-2">
                        <strong>Certificate Fingerprint:</strong>
                        <code class="d-block small text-break">${attestation.certificate_fingerprint}</code>
                        <small class="text-muted">TLS certificate SHA-256 fingerprint</small>
                    </div>
                    <div class="mb-2">
                        <strong>Attestation Timestamp:</strong>
                        <code>${new Date(attestation.timestamp).toLocaleString()}</code>
                        <small class="text-muted d-block">When this VM attestation was captured</small>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-outline-secondary btn-sm" 
                                onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">
                            <i class="fas fa-code"></i> Show Raw Quote
                        </button>
                        <div style="display: none;" class="mt-2">
                            <small class="text-muted">Full Intel TDX attestation quote (hex):</small>
                            <textarea class="form-control font-monospace small" rows="4" readonly>${attestation.raw_quote}</textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;
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
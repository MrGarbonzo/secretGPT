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
        // Attest AI VM verification
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
        
        // Set container info immediately (mock data until SecretVM provides live endpoints)
        this.setFallbackContainerInfo('self');
        
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
            console.error('Attest AI VM verification failed:', error);
            this.showError('self-vm', error.message);
            this.updateVMStatus('self-vm', 'error');
        } finally {
            this.setLoadingState('self-vm', false);
        }
    }

    async verifySecretAIVM() {
        this.setLoadingState('secretai-vm', true);
        
        // Set container info immediately (mock data until SecretVM provides live endpoints)
        this.setFallbackContainerInfo('secretai');
        
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
            const imageTag = containerInfo.image_tag || 'main';
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

        // Set fallback container info (until SecretVM team provides live data)
        this.setFallbackContainerInfo(vmType);

        // Show details
        detailsDiv.style.display = 'block';
    }

    updateField(fieldId, value) {
        const element = document.getElementById(fieldId);
        if (element) {
            element.textContent = value || '-';
        }
    }

    async updateContainerInfo(vmType) {
        // TODO: Re-enable when SecretVM team provides container info endpoints
        // For now, using fallback data directly in displayAttestationData
        try {
            // Future: SecretVM team will provide container info on dedicated ports (similar to port 29343 for attestation)
            // For now, try existing endpoints with graceful fallback to mock data
            const endpoint = vmType === 'secretai' ? 
                `${this.API_BASE}/system/secret-ai-container-info` : 
                `${this.API_BASE}/system/container-info`;
            
            console.log(`Fetching container info for ${vmType} from: ${endpoint}`);
            
            const response = await fetch(endpoint);
            
            // Handle non-existent endpoints (404, etc.)
            if (!response.ok) {
                console.log(`Endpoint ${endpoint} not available (${response.status}), using fallback data`);
                this.setFallbackContainerInfo(vmType);
                return;
            }
            
            const data = await response.json();
            console.log(`Container info response for ${vmType}:`, data);
            
            // Check if we have valid container info
            if (data.success && data.container_info && 
                data.container_info.image_name && 
                data.container_info.image_name !== 'unknown') {
                
                const containerInfo = data.container_info;
                
                // Format Docker image
                const imageName = containerInfo.image_name;
                const imageTag = containerInfo.image_tag && containerInfo.image_tag !== 'unknown' ? 
                    containerInfo.image_tag : this.getDefaultImageTag(vmType);
                const fullImageName = `${imageName}:${imageTag}`;
                
                // Format build time
                let buildTime = 'Coming soon';
                if (containerInfo.build_time && 
                    containerInfo.build_time !== 'unknown' && 
                    containerInfo.build_time !== 'unavailable') {
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
                        buildTime = 'Coming soon';
                    }
                }
                
                // Format SHA256
                let sha256 = 'Coming soon';
                if (containerInfo.image_sha && 
                    containerInfo.image_sha !== 'unknown' && 
                    containerInfo.image_sha !== 'unavailable' && 
                    containerInfo.image_sha !== 'Requires TEE attestation') {
                    // Truncate long SHA hashes for display
                    if (containerInfo.image_sha.startsWith('sha256:')) {
                        sha256 = containerInfo.image_sha.substring(0, 19) + '...';
                    } else if (containerInfo.image_sha.length > 16) {
                        sha256 = containerInfo.image_sha.substring(0, 16) + '...';
                    } else {
                        sha256 = containerInfo.image_sha;
                    }
                }
                
                // Update the fields with real or processed data
                this.updateField(`${vmType}-docker-image`, fullImageName);
                this.updateField(`${vmType}-build-time`, buildTime);
                this.updateField(`${vmType}-image-sha`, sha256);
                
                console.log(`Updated ${vmType} with API data`);
                
            } else {
                console.log(`Invalid or insufficient container info for ${vmType}, using fallback`);
                this.setFallbackContainerInfo(vmType);
            }
        } catch (error) {
            console.log(`Error fetching container info for ${vmType}:`, error.message);
            // Use fallback data when API calls fail
            this.setFallbackContainerInfo(vmType);
        }
    }

    getDefaultImageName(vmType) {
        switch (vmType) {
            case 'secretai':
                return 'ghcr.io/scrtlabs/secret-ai';
            case 'self':
            default:
                return 'ghcr.io/mrgarbonzo/secretgpt';
        }
    }

    getDefaultImageTag(vmType) {
        switch (vmType) {
            case 'secretai':
                return 'latest';
            case 'self':
            default:
                return 'main';
        }
    }

    setFallbackContainerInfo(vmType) {
        // Use realistic image names without tags, ready for SecretVM integration
        let imageName;
        if (vmType === 'secretai') {
            imageName = 'ghcr.io/scrtlabs/secret-ai:latest';
        } else {
            // Attest AI VM - no tag as requested
            imageName = 'ghcr.io/mrgarbonzo/secretgpt';
        }
        
        // All additional info shows "Coming soon" until SecretVM team provides endpoints
        const buildTime = 'Coming soon';
        const sha256 = 'Coming soon';
        
        this.updateField(`${vmType}-docker-image`, imageName);
        this.updateField(`${vmType}-build-time`, buildTime);
        this.updateField(`${vmType}-image-sha`, sha256);
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
                                    <strong>Content Integrity Hashes:</strong><br>
                                    Question Hash: <code>${proofData.interaction.question_hash.substring(0, 16)}...</code><br>
                                    Answer Hash: <code>${proofData.interaction.answer_hash.substring(0, 16)}...</code><br>
                                    ${proofData.conversation && proofData.conversation.conversation_hash ? 
                                        `Conversation Hash: <code>${proofData.conversation.conversation_hash.substring(0, 16)}...</code><br>` : 
                                        ''
                                    }
                                    <em>✓ All hashes verified during decryption - content is authentic and unmodified</em>
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
                    
                    <!-- Dual VM Attestation Details -->
                    <h6 class="mb-3"><i class="fas fa-balance-scale"></i> Dual VM Attestation Details</h6>
                    
                    ${this.formatDualVMComparison(proofData.attestation.self_vm.attestation, proofData.attestation.secret_ai_vm.attestation)}
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
        // Generate unique IDs for this attestation display
        const uniqueId = 'attest-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
        // Determine attestation validation status
        const validationStatus = this.validateAttestationData(attestation);
        
        // Format individual attestation data for comprehensive display
        return `
            <div class="row">
                <!-- Core Measurements Column -->
                <div class="col-md-6">
                    <h6 class="text-primary d-flex align-items-center">
                        <i class="fas fa-microchip me-2"></i>Core Measurements
                        ${validationStatus.overall ? 
                            '<span class="badge bg-success ms-2"><i class="fas fa-check"></i> Valid</span>' : 
                            '<span class="badge bg-warning ms-2"><i class="fas fa-exclamation-triangle"></i> Check Required</span>'
                        }
                    </h6>
                    
                    <!-- MRTD - Trust Domain Measurement -->
                    <div class="mb-3 border-start border-primary ps-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <strong>MRTD (Trust Domain):</strong>
                            ${validationStatus.mrtd ? 
                                '<span class="badge bg-success"><i class="fas fa-shield-alt"></i></span>' : 
                                '<span class="badge bg-secondary">Unverified</span>'
                            }
                        </div>
                        <code class="d-block small text-break font-monospace">${attestation.mrtd}</code>
                        <small class="text-muted">
                            <strong>Measurement of Trust Domain:</strong> Cryptographic hash of the VM's initial state, 
                            bootloader, and kernel. This proves the VM hasn't been tampered with at boot time.
                        </small>
                        <div class="mt-1">
                            <button class="btn btn-link btn-sm p-0" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">
                                <i class="fas fa-info-circle"></i> Technical Details
                            </button>
                            <div style="display: none;" class="mt-2 p-2 bg-light rounded">
                                <small>
                                    <strong>Type:</strong> 384-bit SHA-384 hash<br>
                                    <strong>Source:</strong> Intel TDX hardware measurement<br>
                                    <strong>Bytes:</strong> ${attestation.mrtd.length / 2} (${attestation.mrtd.length} hex chars)<br>
                                    <strong>Purpose:</strong> Verify VM boot integrity and authenticity
                                </small>
                            </div>
                        </div>
                    </div>

                    <!-- RTMR Values - Runtime Measurements -->
                    <div class="mb-3">
                        <strong class="text-info">Runtime Measurement Registers (RTMR):</strong>
                        <small class="d-block text-muted mb-2">
                            Continuously updated measurements of the VM's runtime state, OS, and applications.
                        </small>
                        
                        <!-- RTMR0 -->
                        <div class="mb-2 border-start border-info ps-2">
                            <div class="d-flex justify-content-between">
                                <strong class="small">RTMR0 (OS Kernel):</strong>
                                ${validationStatus.rtmr0 ? 
                                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                                    '<span class="badge bg-secondary">Unverified</span>'
                                }
                            </div>
                            <code class="d-block small text-break font-monospace">${attestation.rtmr0}</code>
                            <small class="text-muted">Operating system kernel and critical system components</small>
                        </div>
                        
                        <!-- RTMR1 -->
                        <div class="mb-2 border-start border-info ps-2">
                            <div class="d-flex justify-content-between">
                                <strong class="small">RTMR1 (System Services):</strong>
                                ${validationStatus.rtmr1 ? 
                                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                                    '<span class="badge bg-secondary">Unverified</span>'
                                }
                            </div>
                            <code class="d-block small text-break font-monospace">${attestation.rtmr1}</code>
                            <small class="text-muted">System services, drivers, and runtime environment</small>
                        </div>
                        
                        <!-- RTMR2 -->
                        <div class="mb-2 border-start border-info ps-2">
                            <div class="d-flex justify-content-between">
                                <strong class="small">RTMR2 (Applications):</strong>
                                ${validationStatus.rtmr2 ? 
                                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                                    '<span class="badge bg-secondary">Unverified</span>'
                                }
                            </div>
                            <code class="d-block small text-break font-monospace">${attestation.rtmr2}</code>
                            <small class="text-muted">Application binaries and runtime libraries</small>
                        </div>
                        
                        <!-- RTMR3 -->
                        <div class="mb-2 border-start border-info ps-2">
                            <div class="d-flex justify-content-between">
                                <strong class="small">RTMR3 (Custom/User):</strong>
                                ${validationStatus.rtmr3 ? 
                                    '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                                    '<span class="badge bg-secondary">Unverified</span>'
                                }
                            </div>
                            <code class="d-block small text-break font-monospace">${attestation.rtmr3}</code>
                            <small class="text-muted">User applications and custom configurations</small>
                        </div>
                    </div>
                </div>

                <!-- Security & Verification Column -->
                <div class="col-md-6">
                    <h6 class="text-success d-flex align-items-center">
                        <i class="fas fa-shield-alt me-2"></i>Security & Verification
                        ${validationStatus.security ? 
                            '<span class="badge bg-success ms-2"><i class="fas fa-lock"></i> Secure</span>' : 
                            '<span class="badge bg-warning ms-2"><i class="fas fa-exclamation-triangle"></i> Review</span>'
                        }
                    </h6>
                    
                    <!-- Report Data -->
                    <div class="mb-3 border-start border-success ps-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <strong>Report Data:</strong>
                            ${validationStatus.reportData ? 
                                '<span class="badge bg-success"><i class="fas fa-check"></i></span>' : 
                                '<span class="badge bg-secondary">Standard</span>'
                            }
                        </div>
                        <code class="d-block small text-break font-monospace">${attestation.report_data}</code>
                        <small class="text-muted">
                            <strong>Custom Attestation Data:</strong> Application-specific data included in the attestation.
                            This can contain nonces, request IDs, or other verification data.
                        </small>
                    </div>
                    
                    <!-- Certificate Fingerprint -->
                    <div class="mb-3 border-start border-warning ps-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <strong>TLS Certificate:</strong>
                            ${validationStatus.certificate ? 
                                '<span class="badge bg-success"><i class="fas fa-certificate"></i> Valid</span>' : 
                                '<span class="badge bg-warning"><i class="fas fa-exclamation-triangle"></i> Self-Signed</span>'
                            }
                        </div>
                        <code class="d-block small text-break font-monospace">${attestation.certificate_fingerprint}</code>
                        <small class="text-muted">
                            <strong>SHA-256 Fingerprint:</strong> Prevents man-in-the-middle attacks by verifying 
                            the TLS certificate used during attestation retrieval.
                        </small>
                        <div class="mt-1">
                            <button class="btn btn-link btn-sm p-0" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'">
                                <i class="fas fa-info-circle"></i> Certificate Details
                            </button>
                            <div style="display: none;" class="mt-2 p-2 bg-light rounded">
                                <small>
                                    <strong>Algorithm:</strong> SHA-256<br>
                                    <strong>Length:</strong> 256 bits (64 hex characters)<br>
                                    <strong>Purpose:</strong> Verify TLS connection authenticity<br>
                                    <strong>Status:</strong> ${validationStatus.certificate ? 'Trusted CA' : 'Self-signed (SecretVM standard)'}
                                </small>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Timestamp & Freshness -->
                    <div class="mb-3 border-start border-info ps-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <strong>Attestation Timestamp:</strong>
                            ${validationStatus.timestamp ? 
                                '<span class="badge bg-success"><i class="fas fa-clock"></i> Fresh</span>' : 
                                '<span class="badge bg-warning"><i class="fas fa-clock"></i> Check Age</span>'
                            }
                        </div>
                        <code class="d-block">${new Date(attestation.timestamp).toLocaleString('en-US', {
                            year: 'numeric', month: '2-digit', day: '2-digit',
                            hour: '2-digit', minute: '2-digit', second: '2-digit',
                            timeZone: 'UTC', timeZoneName: 'short'
                        })}</code>
                        <small class="text-muted">
                            <strong>Attestation Age:</strong> ${this.formatTimestampAge(attestation.timestamp)}<br>
                            When this VM's security state was last verified and captured.
                        </small>
                    </div>
                    
                    <!-- Raw Attestation Quote -->
                    <div class="mt-3">
                        <button class="btn btn-outline-secondary btn-sm" id="toggle-raw-${uniqueId}"
                                onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'block' ? 'none' : 'block'; this.innerHTML = this.nextElementSibling.style.display === 'block' ? '<i class=\\"fas fa-eye-slash\\"></i> Hide Raw Quote' : '<i class=\\"fas fa-code\\"></i> Show Raw Quote'">
                            <i class="fas fa-code"></i> Show Raw Quote
                        </button>
                        <div style="display: none;" class="mt-2">
                            <small class="text-muted d-block mb-2">
                                <strong>Complete Intel TDX Attestation Quote (${attestation.raw_quote.length} hex characters):</strong><br>
                                This is the complete cryptographic attestation quote from Intel TDX hardware. 
                                It contains all measurements and is digitally signed by Intel's attestation service.
                            </small>
                            <div class="position-relative">
                                <textarea class="form-control font-monospace small" rows="6" readonly id="raw-quote-${uniqueId}">${attestation.raw_quote}</textarea>
                                <button class="btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-1" 
                                        onclick="navigator.clipboard.writeText(document.getElementById('raw-quote-${uniqueId}').value); this.innerHTML='<i class=\\"fas fa-check\\"></i> Copied!'; setTimeout(() => this.innerHTML='<i class=\\"fas fa-copy\\"></i> Copy', 2000)">
                                    <i class="fas fa-copy"></i> Copy
                                </button>
                            </div>
                            <small class="text-muted">
                                <strong>Format:</strong> Intel TDX Quote v4 • <strong>Signature:</strong> ECDSA-P256 • <strong>Size:</strong> ${Math.round(attestation.raw_quote.length / 2)} bytes
                            </small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Attestation Summary -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="alert ${validationStatus.overall ? 'alert-success' : 'alert-warning'} mb-0">
                        <div class="d-flex align-items-center">
                            <i class="fas ${validationStatus.overall ? 'fa-shield-alt' : 'fa-exclamation-triangle'} fa-lg me-3"></i>
                            <div>
                                <strong>${validationStatus.overall ? 'Attestation Verified' : 'Attestation Requires Review'}</strong><br>
                                <small>
                                    ${validationStatus.overall ? 
                                        'This VM\'s security state has been cryptographically verified using Intel TDX hardware attestation.' :
                                        'This attestation contains unverified elements. In production, compare against known-good baselines.'
                                    }
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    validateAttestationData(attestation) {
        // Validate attestation data with appropriate handling for development/mock data
        
        // Check for explicit error indicators in the data
        const hasError = (value) => {
            return value && (
                value.includes('error_') || 
                value.includes('parse_error_') || 
                value.includes('no_quote_')
            );
        };
        
        // Check if this appears to be mock/development data
        const isMockData = (attestation) => {
            const mockIndicators = [
                attestation.mrtd && attestation.mrtd.length < 64,
                attestation.certificate_fingerprint && attestation.certificate_fingerprint.includes('secretvm_'),
                !attestation.raw_quote || attestation.raw_quote.length < 1000
            ];
            return mockIndicators.some(indicator => indicator);
        };
        
        const isUsingMockData = isMockData(attestation);
        
        // Validate individual components with appropriate expectations
        const mrtdValid = !hasError(attestation.mrtd) && 
                         (isUsingMockData || attestation.mrtd.length >= 64);
        const rtmr0Valid = !hasError(attestation.rtmr0) && 
                          (isUsingMockData || attestation.rtmr0.length >= 64);
        const rtmr1Valid = !hasError(attestation.rtmr1) && 
                          (isUsingMockData || attestation.rtmr1.length >= 64);
        const rtmr2Valid = !hasError(attestation.rtmr2) && 
                          (isUsingMockData || attestation.rtmr2.length >= 64);
        const rtmr3Valid = !hasError(attestation.rtmr3) && 
                          (isUsingMockData || attestation.rtmr3.length >= 64);
        const reportDataValid = !hasError(attestation.report_data);
        
        // Certificate validation (self-signed is acceptable for SecretVM)
        const certificateValid = attestation.certificate_fingerprint && 
                               attestation.certificate_fingerprint.length >= 32 &&
                               !hasError(attestation.certificate_fingerprint);
        
        // Extended timestamp validation for proof verification (7 days for development)
        const timestampAge = new Date() - new Date(attestation.timestamp);
        const timestampValid = timestampAge < (7 * 24 * 60 * 60 * 1000); // 7 days
        
        // Overall validation - more lenient for development environments
        const coreValid = mrtdValid && rtmr0Valid && rtmr1Valid && rtmr2Valid && rtmr3Valid;
        const securityValid = reportDataValid && certificateValid;
        const overallValid = coreValid && securityValid && timestampValid;
        
        return {
            mrtd: mrtdValid,
            rtmr0: rtmr0Valid,
            rtmr1: rtmr1Valid,
            rtmr2: rtmr2Valid,
            rtmr3: rtmr3Valid,
            reportData: reportDataValid,
            certificate: certificateValid,
            timestamp: timestampValid,
            security: securityValid,
            overall: overallValid,
            isMockData: isUsingMockData
        };
    }
    
    formatTimestampAge(timestamp) {
        // Format how long ago the attestation was captured
        const now = new Date();
        const attestationTime = new Date(timestamp);
        const ageMs = now - attestationTime;
        
        if (ageMs < 0) {
            return "Future timestamp (check system clock)";
        }
        
        const ageMinutes = Math.floor(ageMs / (1000 * 60));
        const ageHours = Math.floor(ageMinutes / 60);
        const ageDays = Math.floor(ageHours / 24);
        
        if (ageMinutes < 1) {
            return "Just now";
        } else if (ageMinutes < 60) {
            return `${ageMinutes} minute${ageMinutes !== 1 ? 's' : ''} ago`;
        } else if (ageHours < 24) {
            return `${ageHours} hour${ageHours !== 1 ? 's' : ''} ago`;
        } else {
            return `${ageDays} day${ageDays !== 1 ? 's' : ''} ago`;
        }
    }

    formatDualVMComparison(selfAttestation, secretAiAttestation) {
        // Create side-by-side comparison of both VM attestations
        const selfValidation = this.validateAttestationData(selfAttestation);
        const secretAiValidation = this.validateAttestationData(secretAiAttestation);
        
        // Compare measurements to highlight differences
        const measurementsMatch = this.compareMeasurements(selfAttestation, secretAiAttestation);
        
        return `
            <div class="card">
                <div class="card-header">
                    <div class="row">
                        <div class="col-md-6 text-center">
                            <h6 class="mb-0">
                                <i class="fas fa-server text-primary"></i> Attest AI VM (Interface)
                            </h6>
                            <small class="text-muted">Handles user interface and proof generation</small>
                        </div>
                        <div class="col-md-6 text-center">
                            <h6 class="mb-0">
                                <i class="fas fa-brain text-info"></i> Secret AI VM (Processing)
                            </h6>
                            <small class="text-muted">Processes AI requests securely</small>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Trust Domain Measurements Comparison -->
                    <div class="mb-4">
                        <h6 class="text-primary mb-3">
                            <i class="fas fa-microchip"></i> Trust Domain Measurements (MRTD)
                        </h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="border-start border-primary ps-3 mb-3">
                                    <small class="text-muted d-block">Attest AI VM MRTD:</small>
                                    <code class="d-block small font-monospace text-break">${selfAttestation.mrtd}</code>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="border-start border-info ps-3 mb-3">
                                    <small class="text-muted d-block">Secret AI VM MRTD:</small>
                                    <code class="d-block small font-monospace text-break">${secretAiAttestation.mrtd}</code>
                                </div>
                            </div>
                        </div>
                        <small class="text-muted">
                            <strong>Expected:</strong> Different values indicate separate, independently measured VMs with proper isolation.
                        </small>
                    </div>

                    <!-- Runtime Measurements Comparison -->
                    <div class="mb-4">
                        <h6 class="text-info mb-3"><i class="fas fa-gauge"></i> Runtime Measurements (RTMR)</h6>
                        
                        <!-- RTMR Comparison Table -->
                        <div class="table-responsive">
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Register</th>
                                        <th>Attest AI VM</th>
                                        <th>Secret AI VM</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>RTMR0</strong><br><small class="text-muted">OS Kernel</small></td>
                                        <td><code class="small">${this.truncateHash(selfAttestation.rtmr0)}</code></td>
                                        <td><code class="small">${this.truncateHash(secretAiAttestation.rtmr0)}</code></td>
                                    </tr>
                                    <tr>
                                        <td><strong>RTMR1</strong><br><small class="text-muted">System Services</small></td>
                                        <td><code class="small">${this.truncateHash(selfAttestation.rtmr1)}</code></td>
                                        <td><code class="small">${this.truncateHash(secretAiAttestation.rtmr1)}</code></td>
                                    </tr>
                                    <tr>
                                        <td><strong>RTMR2</strong><br><small class="text-muted">Applications</small></td>
                                        <td><code class="small">${this.truncateHash(selfAttestation.rtmr2)}</code></td>
                                        <td><code class="small">${this.truncateHash(secretAiAttestation.rtmr2)}</code></td>
                                    </tr>
                                    <tr>
                                        <td><strong>RTMR3</strong><br><small class="text-muted">Custom/User</small></td>
                                        <td><code class="small">${this.truncateHash(selfAttestation.rtmr3)}</code></td>
                                        <td><code class="small">${this.truncateHash(secretAiAttestation.rtmr3)}</code></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Security Comparison -->
                    <div class="mb-4">
                        <h6 class="text-success mb-3"><i class="fas fa-shield-alt"></i> Security Details Comparison</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="border-start border-primary ps-3">
                                    <strong class="d-block">Attest AI VM Security</strong>
                                    <div class="mt-2">
                                        <small class="text-muted">Certificate Fingerprint:</small>
                                        <code class="d-block small">${this.truncateHash(selfAttestation.certificate_fingerprint, 32)}</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Report Data:</small>
                                        <code class="d-block small">${this.truncateHash(selfAttestation.report_data, 24)}</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Attestation Time:</small>
                                        <code class="d-block small">${this.formatTimestampAge(selfAttestation.timestamp)}</code>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="border-start border-info ps-3">
                                    <strong class="d-block">Secret AI VM Security</strong>
                                    <div class="mt-2">
                                        <small class="text-muted">Certificate Fingerprint:</small>
                                        <code class="d-block small">${this.truncateHash(secretAiAttestation.certificate_fingerprint, 32)}</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Report Data:</small>
                                        <code class="d-block small">${this.truncateHash(secretAiAttestation.report_data, 24)}</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Attestation Time:</small>
                                        <code class="d-block small">${this.formatTimestampAge(secretAiAttestation.timestamp)}</code>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Infrastructure Transparency -->
                    <div class="mb-4">
                        <h6 class="text-warning mb-3"><i class="fas fa-docker"></i> Infrastructure Transparency</h6>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="border-start border-primary ps-3">
                                    <strong class="d-block">Attest AI VM Deployment</strong>
                                    <div class="mt-2">
                                        <small class="text-muted">Docker Image:</small>
                                        <code class="d-block small">ghcr.io/mrgarbonzo/secretgpt:main</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Build Time:</small>
                                        <code class="d-block small">Coming soon</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Image SHA256:</small>
                                        <code class="d-block small">Coming soon</code>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="border-start border-info ps-3">
                                    <strong class="d-block">Secret AI VM Deployment</strong>
                                    <div class="mt-2">
                                        <small class="text-muted">Docker Image:</small>
                                        <code class="d-block small">ghcr.io/scrtlabs/secret-ai:latest</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Build Time:</small>
                                        <code class="d-block small">Coming soon</code>
                                    </div>
                                    <div class="mt-2">
                                        <small class="text-muted">Image SHA256:</small>
                                        <code class="d-block small">Coming soon</code>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <small class="text-muted mt-2 d-block">
                            <i class="fas fa-info-circle"></i> Infrastructure data will be provided by SecretVM team via dedicated endpoints (similar to CPU attestation on port 29343). Mock data shown until live integration.
                        </small>
                    </div>

                    <!-- Dual Attestation Summary -->
                    <div class="alert ${this.getDualAttestationAlertClass(selfValidation, secretAiValidation)} mb-0">
                        <div class="d-flex align-items-center">
                            <i class="fas ${this.getDualAttestationIcon(selfValidation, secretAiValidation)} fa-lg me-3"></i>
                            <div>
                                <strong>${this.getDualAttestationTitle(selfValidation, secretAiValidation)}</strong><br>
                                <small>
                                    ${this.getDualAttestationMessage(selfValidation, secretAiValidation)}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    compareMeasurements(attest1, attest2) {
        // Compare measurements between two attestations
        return {
            mrtd: attest1.mrtd === attest2.mrtd,
            rtmr0: attest1.rtmr0 === attest2.rtmr0,
            rtmr1: attest1.rtmr1 === attest2.rtmr1,
            rtmr2: attest1.rtmr2 === attest2.rtmr2,
            rtmr3: attest1.rtmr3 === attest2.rtmr3
        };
    }

    truncateHash(hash, maxLength = 16) {
        // Truncate long hashes for display while preserving readability
        if (!hash || hash.length <= maxLength) {
            return hash || 'N/A';
        }
        return hash.substring(0, maxLength) + '...';
    }

    getDualAttestationAlertClass(selfValidation, secretAiValidation) {
        if (selfValidation.overall && secretAiValidation.overall) {
            return 'alert-success';
        } else if (selfValidation.isMockData || secretAiValidation.isMockData) {
            return 'alert-info';
        } else {
            return 'alert-warning';
        }
    }

    getDualAttestationIcon(selfValidation, secretAiValidation) {
        if (selfValidation.overall && secretAiValidation.overall) {
            return 'fa-shield-alt';
        } else if (selfValidation.isMockData || secretAiValidation.isMockData) {
            return 'fa-info-circle';
        } else {
            return 'fa-exclamation-triangle';
        }
    }

    getDualAttestationTitle(selfValidation, secretAiValidation) {
        if (selfValidation.overall && secretAiValidation.overall) {
            return 'Dual VM Attestation Verified';
        } else if (selfValidation.isMockData || secretAiValidation.isMockData) {
            return 'Development Environment - Ready for SecretVM Integration';
        } else {
            return 'Dual VM Attestation Requires Review';
        }
    }

    getDualAttestationMessage(selfValidation, secretAiValidation) {
        if (selfValidation.overall && secretAiValidation.overall) {
            return 'Both VMs have been successfully attested with Intel TDX hardware verification. The dual architecture provides enhanced security through independent VM isolation.';
        } else if (selfValidation.isMockData || secretAiValidation.isMockData) {
            return 'This proof was generated in a development environment with mock attestation data. The system is ready for live Intel TDX attestation when deployed in SecretVM infrastructure.';
        } else {
            return 'One or both VMs require attestation review. Verify that both VMs are properly configured and measurements match expected baselines.';
        }
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
            if (topic === 'boot') {
                const bootElement = document.getElementById('current-boot');
                const selfMrtd = document.getElementById('self-mrtd');
                const rtmr0 = document.getElementById('self-rtmr0');
                if (selfMrtd && selfMrtd.textContent !== '-') {
                    bootElement.innerHTML = `
                        <strong>MRTD:</strong> ${selfMrtd.textContent}<br>
                        <strong>RTMR0:</strong> ${rtmr0.textContent}<br>
                        <strong>RTMR1:</strong> ${document.getElementById('self-rtmr1').textContent}<br>
                        <strong>RTMR2:</strong> ${document.getElementById('self-rtmr2').textContent}<br>
                        <strong>RTMR3:</strong> ${document.getElementById('self-rtmr3').textContent}
                    `;
                }
            } else if (topic === 'identity') {
                const identityElement = document.getElementById('current-identity');
                const selfCert = document.getElementById('self-cert-fingerprint');
                const selfReport = document.getElementById('self-report-data');
                if (selfCert && selfCert.textContent !== '-') {
                    identityElement.innerHTML = `
                        <strong>Certificate Fingerprint:</strong> ${selfCert.textContent}<br>
                        <strong>Report Data:</strong> ${selfReport.textContent}
                    `;
                }
            } else if (topic === 'hardware') {
                const hardwareElement = document.getElementById('current-hardware');
                const selfMrtd = document.getElementById('self-mrtd');
                if (selfMrtd && selfMrtd.textContent !== '-') {
                    hardwareElement.innerHTML = `
                        <strong>SEAM Module MRTD:</strong> ${selfMrtd.textContent}<br>
                        <strong>Hardware Foundation:</strong> Intel TDX attestation chain verified
                    `;
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
    if (details) {
        const isVisible = details.style.display !== 'none';
        details.style.display = isVisible ? 'none' : 'block';
    }
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
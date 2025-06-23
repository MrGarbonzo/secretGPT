# secretGPT Deployment Guide

## Automatic Deployment (Recommended)

For SecretVM deployments where the external IP needs to be auto-discovered:

```bash
./deploy.sh
```

This script will:
1. Automatically discover the host's external IP address
2. Set the correct attestation endpoint (`https://<external-ip>:29343/cpu.html`)
3. Start secretGPT with the correct configuration

## Manual Deployment

If you know the external IP address or want to set it manually:

```bash
export SECRETGPT_ATTESTATION_ENDPOINT="https://YOUR_VM_IP:29343/cpu.html"
docker-compose up -d
```

## How Self-Attestation Works

The secretGPT container needs to access the host VM's attestation endpoint. The deployment process:

1. **Auto-Discovery**: The deploy script discovers the VM's external IP using multiple methods:
   - `https://ipv4.icanhazip.com`
   - `https://api.ipify.org` 
   - `https://checkip.amazonaws.com`

2. **Container Access**: The docker-compose configuration includes:
   - `extra_hosts: host.docker.internal:host-gateway` for container-to-host communication
   - Environment variable `SECRETGPT_ATTESTATION_ENDPOINT` set to the correct external IP

3. **Fallback Methods**: If the environment variable isn't set, the AttestationService tries:
   - `host.docker.internal` resolution
   - Docker gateway IP discovery
   - Socket-based IP discovery

## Troubleshooting

### Self-Attestation Not Working

1. Check if the attestation endpoint is set correctly:
   ```bash
   docker-compose exec secretgpt env | grep ATTESTATION
   ```

2. Verify the VM's external IP:
   ```bash
   curl https://ipv4.icanhazip.com
   ```

3. Test attestation endpoint accessibility:
   ```bash
   curl -k https://YOUR_VM_IP:29343/cpu.html
   ```

### Container Network Issues

1. Check if `host.docker.internal` resolves inside container:
   ```bash
   docker-compose exec secretgpt nslookup host.docker.internal
   ```

2. Check container's network routing:
   ```bash
   docker-compose exec secretgpt ip route show default
   ```

## Files Modified

- `docker-compose.yml`: Added `extra_hosts` and updated attestation endpoint
- `docker-compose.dev.yaml`: Added `extra_hosts` for development consistency  
- `secretGPT/interfaces/web_ui/attestation/service.py`: Enhanced IP discovery logic
- `deploy.sh`: Automatic deployment script with IP discovery
- `scripts/start-with-host-ip.sh`: Container startup script (alternative approach)

## SecretVM Requirements

- Port 29343 must be accessible for attestation endpoint
- Container must have network access to reach external IP services for discovery
- The VM must be running a SecretVM that provides attestation at `/cpu.html`
# SecretGPT Network Architecture Analysis

## 1. Current Network Flow

### Application Architecture
- **Main Service**: secretGPT runs on port 8000 inside container, exposed as 8003 on host
- **Attestation Endpoint**: SecretVM attestation service on host at port 29343
- **Docker Networking**: Default bridge mode with extra_hosts configuration

### Request Flow Patterns

#### External → Application
```
User Browser (port 8003) → Docker Host → Docker Bridge → Container (port 8000)
```

#### Container → Host Attestation Service
```
Container → host.docker.internal:29343 → Host SecretVM Service
```

#### Container → External Secret AI
```
Container → Docker Bridge → Host Network → Internet → secretai.scrtlabs.com
```

## 2. Docker Networking Modes Analysis

### Current Configuration (Bridge Mode)
```yaml
services:
  secretgpt:
    ports:
      - "8003:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

**Characteristics:**
- Container gets its own IP in Docker bridge network (172.17.0.x)
- Port mapping required for external access
- `host.docker.internal` resolves to host gateway IP
- Isolation between container and host network

### Alternative: Host Mode
```yaml
network_mode: host
```
**Pros:**
- Direct access to host ports (no mapping needed)
- Better performance (no NAT overhead)
- Simpler host service access

**Cons:**
- No network isolation
- Port conflicts with host services
- Less portable across environments

## 3. IP Address Resolution

### Current IP Resolution Chain

1. **Container Internal IP**: 172.17.0.2 (example)
2. **Docker Bridge Gateway**: 172.17.0.1
3. **Host External IP**: Discovered via deploy.sh
4. **host.docker.internal**: Maps to Docker gateway (172.17.0.1)

### IP Discovery Methods in Code

From `attestation/service.py`:
```python
# Method 1: host.docker.internal resolution
host_ip = socket.gethostbyname('host.docker.internal')

# Method 2: Docker gateway from route table
ip route show default → extract gateway IP

# Method 3: External IP discovery
Connect to 8.8.8.8 → get local IP
```

## 4. Potential Issues Identified

### A. Container-to-Container Communication
**Issue**: No multi-container setup currently, but future services would need:
- Shared Docker network
- Service discovery mechanism
- Internal DNS resolution

### B. Host-to-Container Communication
**Current Issues:**
1. **Attestation Endpoint Access**:
   - Container tries multiple methods to find host IP
   - `host.docker.internal` may not resolve correctly in all environments
   - Self-signed certificates cause verification issues

2. **IP Discovery Complexity**:
   - Multiple fallback methods indicate fragility
   - Environment-specific behavior (Docker Desktop vs Linux)

### C. External Access to Containers
**Issues:**
1. **Port Confusion**: 
   - Internal port 8000 vs external port 8003
   - Users must remember non-standard port
   - Multiple services would need port management

2. **SSL/TLS Termination**:
   - No HTTPS for main application
   - Self-signed certs for attestation cause warnings

### D. Attestation Endpoint Issues
**Specific Problems:**
1. **Dynamic IP Resolution**:
   - Complex logic to find host IP from container
   - Different behavior in different environments

2. **Certificate Validation**:
   ```python
   verify=False  # Security risk
   ```

3. **Network Routing**:
   - Container → host.docker.internal:29343
   - May fail in production environments
   - Firewall/iptables complications

## 5. Benefits of Adding Nginx Reverse Proxy

### Architecture with Nginx
```
                        ┌─────────────┐
                        │    Nginx    │
                        │  (Port 80)  │
                        └──────┬──────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
         ┌──────▼──────┐              ┌──────▼──────┐
         │  secretGPT  │              │ Attestation │
         │  (Port 8000)│              │(Port 29343) │
         └─────────────┘              └─────────────┘
```

### Key Benefits

1. **Unified Entry Point**:
   - Single port 80/443 for all services
   - Path-based routing (/api, /attestation)
   - No port confusion for users

2. **SSL/TLS Management**:
   - Central SSL termination
   - Let's Encrypt integration
   - Proper certificate validation

3. **Service Discovery**:
   - Nginx can use Docker DNS
   - Upstream configuration for containers
   - Health checks and failover

4. **Request Routing**:
   ```nginx
   location / {
       proxy_pass http://secretgpt:8000;
   }
   
   location /attestation {
       proxy_pass https://host.docker.internal:29343;
       proxy_ssl_verify off;
   }
   ```

5. **IP Resolution Simplification**:
   - Nginx handles host resolution
   - Containers only need to know service names
   - No complex IP discovery logic needed

## 6. Common Docker/Nginx Integration Pitfalls

### Pitfall 1: DNS Resolution
**Problem**: Container names not resolving
**Solution**: Use custom Docker network
```yaml
networks:
  secretgpt-net:
    driver: bridge

services:
  nginx:
    networks:
      - secretgpt-net
```

### Pitfall 2: Upstream Connectivity
**Problem**: "502 Bad Gateway" errors
**Solution**: Ensure services are on same network
```nginx
upstream secretgpt {
    server secretgpt:8000 max_fails=3 fail_timeout=30s;
}
```

### Pitfall 3: Host Service Access
**Problem**: Cannot reach host services from nginx
**Solution**: Use host network or extra_hosts
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

### Pitfall 4: Health Checks
**Problem**: Nginx starts before backend services
**Solution**: Implement proper health checks
```nginx
location /health {
    access_log off;
    proxy_pass http://secretgpt:8000/health;
}
```

### Pitfall 5: WebSocket Support
**Problem**: Real-time features broken
**Solution**: Configure WebSocket headers
```nginx
location /ws {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## 7. Recommended Nginx Configuration

### docker-compose.yml Addition
```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: secretgpt-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - secretgpt
    networks:
      - secretgpt-net
    extra_hosts:
      - "host.docker.internal:host-gateway"

  secretgpt:
    networks:
      - secretgpt-net
    # Remove ports mapping - only accessible via nginx

networks:
  secretgpt-net:
    driver: bridge
```

### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream secretgpt_backend {
        server secretgpt:8000;
    }

    server {
        listen 80;
        server_name _;

        # Main application
        location / {
            proxy_pass http://secretgpt_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Attestation proxy
        location /attestation/ {
            proxy_pass https://host.docker.internal:29343/;
            proxy_ssl_verify off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://secretgpt_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## 8. Benefits Summary

With Nginx reverse proxy:

1. **Simplified Networking**: 
   - Single entry point
   - No port confusion
   - Clean service separation

2. **Better Security**:
   - Central SSL/TLS handling
   - Hide internal service details
   - Request filtering/rate limiting

3. **Improved Reliability**:
   - Health checks
   - Load balancing ready
   - Graceful error handling

4. **Easier Deployment**:
   - Standard ports (80/443)
   - Professional appearance
   - CDN/cache ready

5. **Resolved Attestation Issues**:
   - Nginx handles host access
   - No complex IP discovery in app
   - Stable endpoint configuration

## Conclusion

The current Docker networking setup works but has several pain points around IP resolution, port management, and attestation endpoint access. Adding an Nginx reverse proxy would significantly simplify the architecture, improve security, and provide a more professional deployment suitable for production use.
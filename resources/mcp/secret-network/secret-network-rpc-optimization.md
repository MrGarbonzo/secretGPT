# Secret Network RPC Optimization

**Purpose**: Optimize Secret Network API calls for performance and reliability  
**Target**: MCP tools with efficient blockchain interactions  
**Focus**: Caching, connection pooling, and failover strategies

## Overview

This document outlines optimization strategies for Secret Network RPC/LCD API calls within MCP tools to ensure fast, reliable blockchain queries while minimizing API load and handling network failures gracefully.

## Performance Challenges

### Common Issues
1. **Network Latency**: Blockchain API calls can be slow (500ms-3s)
2. **Rate Limiting**: Public endpoints have usage limits
3. **Endpoint Reliability**: Single endpoints can go offline
4. **Redundant Queries**: Repeated calls for same data
5. **Cache Invalidation**: Determining when cached data is stale

### Optimization Goals
- **Response Time**: < 2 seconds for cached queries, < 5 seconds for fresh data
- **Availability**: > 99% uptime through failover strategies  
- **Efficiency**: Minimize redundant API calls
- **User Experience**: Graceful degradation when APIs are slow/unavailable

## Endpoint Management

### Multi-Endpoint Configuration

```python
class SecretNetworkEndpointManager:
    """Manages multiple Secret Network API endpoints with failover"""
    
    def __init__(self, network="mainnet"):
        self.network = network
        self.endpoints = self._get_endpoint_config(network)
        self.current_endpoint_index = 0
        self.endpoint_health = {}
        self.last_health_check = 0
        self.health_check_interval = 60  # 60 seconds
    
    def _get_endpoint_config(self, network):
        """Get endpoint configuration by network"""
        configs = {
            "mainnet": {
                "lcd": [
                    "https://lcd.mainnet.secretsaturn.net",
                    "https://secretnetwork-api.lavenderfive.com:443", 
                    "https://rest-secret.01node.com",
                    "https://public.stakewolle.com/cosmos/secretnetwork/rest"
                ],
                "rpc": [
                    "https://rpc.mainnet.secretsaturn.net",
                    "https://secretnetwork-rpc.lavenderfive.com:443",
                    "https://rpc-secret.01node.com",
                    "https://public.stakewolle.com/cosmos/secretnetwork/rpc"
                ]
            },
            "testnet": {
                "lcd": [
                    "https://lcd.testnet.secretsaturn.net"
                ],
                "rpc": [
                    "https://rpc.testnet.secretsaturn.net"
                ]
            }
        }
        return configs.get(network, configs["mainnet"])
    
    async def get_healthy_endpoint(self, endpoint_type="lcd"):
        """Get a healthy endpoint with automatic failover"""
        endpoints = self.endpoints[endpoint_type]
        
        # Check if we need to refresh health status
        current_time = time.time()
        if current_time - self.last_health_check > self.health_check_interval:
            await self._check_endpoint_health()
            self.last_health_check = current_time
        
        # Try to find a healthy endpoint
        for i in range(len(endpoints)):
            endpoint_index = (self.current_endpoint_index + i) % len(endpoints)
            endpoint = endpoints[endpoint_index]
            
            if self.endpoint_health.get(endpoint, True):  # Default to healthy
                self.current_endpoint_index = endpoint_index
                return endpoint
        
        # If no healthy endpoints, return the first one as fallback
        logger.warning(f"No healthy {endpoint_type} endpoints found, using fallback")
        return endpoints[0]
    
    async def _check_endpoint_health(self):
        """Check health of all endpoints"""
        for endpoint_type in ["lcd", "rpc"]:
            for endpoint in self.endpoints[endpoint_type]:
                try:
                    # Quick health check - try to get status
                    timeout = aiohttp.ClientTimeout(total=5)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        if endpoint_type == "lcd":
                            health_url = f"{endpoint}/cosmos/base/tendermint/v1beta1/node_info"
                        else:
                            health_url = f"{endpoint}/status"
                        
                        async with session.get(health_url) as response:
                            self.endpoint_health[endpoint] = response.status == 200
                            
                except Exception:
                    self.endpoint_health[endpoint] = False
                    logger.warning(f"Endpoint {endpoint} health check failed")
```

### Intelligent Endpoint Selection

```python
class SmartEndpointSelector:
    """Select best endpoint based on latency and reliability"""
    
    def __init__(self):
        self.endpoint_metrics = {}  # endpoint -> {latency, success_rate, last_used}
        self.measurement_window = 300  # 5 minutes
    
    async def select_best_endpoint(self, endpoints, endpoint_type="lcd"):
        """Select endpoint based on performance metrics"""
        
        if not self.endpoint_metrics:
            # First time - return random endpoint
            return random.choice(endpoints)
        
        # Score endpoints based on metrics
        scored_endpoints = []
        current_time = time.time()
        
        for endpoint in endpoints:
            metrics = self.endpoint_metrics.get(endpoint, {
                'latency': 1000,  # Default high latency
                'success_rate': 1.0,  # Assume good until proven otherwise
                'last_used': 0
            })
            
            # Calculate score (lower is better)
            latency_score = metrics['latency']
            reliability_score = (1.0 - metrics['success_rate']) * 1000
            freshness_penalty = max(0, (current_time - metrics['last_used']) / 60)  # Minutes since last use
            
            total_score = latency_score + reliability_score - freshness_penalty
            scored_endpoints.append((endpoint, total_score))
        
        # Sort by score and return best endpoint
        scored_endpoints.sort(key=lambda x: x[1])
        return scored_endpoints[0][0]
    
    async def record_request_metrics(self, endpoint, latency, success):
        """Record metrics for an API request"""
        current_time = time.time()
        
        if endpoint not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint] = {
                'latency': latency,
                'success_rate': 1.0 if success else 0.0,
                'last_used': current_time,
                'request_count': 1
            }
        else:
            metrics = self.endpoint_metrics[endpoint]
            
            # Update moving average latency
            alpha = 0.3  # Smoothing factor
            metrics['latency'] = alpha * latency + (1 - alpha) * metrics['latency']
            
            # Update success rate
            metrics['request_count'] += 1
            if success:
                metrics['success_rate'] = (metrics['success_rate'] * (metrics['request_count'] - 1) + 1) / metrics['request_count']
            else:
                metrics['success_rate'] = (metrics['success_rate'] * (metrics['request_count'] - 1)) / metrics['request_count']
            
            metrics['last_used'] = current_time
```

## Caching Strategies

### Multi-Level Cache Architecture

```python
class SecretNetworkCache:
    """Multi-level caching for Secret Network data"""
    
    def __init__(self):
        # Level 1: In-memory cache (fastest)
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        
        # Level 2: Redis cache (shared across instances)
        # self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # Cache TTL configurations by data type
        self.cache_ttls = {
            'block_height': 10,      # 10 seconds - changes frequently
            'balance': 30,           # 30 seconds - can change
            'transaction': 3600,     # 1 hour - immutable once confirmed
            'validator_info': 300,   # 5 minutes - changes slowly
            'network_params': 1800,  # 30 minutes - rarely changes
        }
    
    def _generate_cache_key(self, operation, **params):
        """Generate consistent cache key"""
        # Sort parameters for consistent keys
        param_str = '&'.join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"secret_network:{operation}:{param_str}"
    
    async def get_cached(self, operation, **params):
        """Get data from cache if available and not expired"""
        cache_key = self._generate_cache_key(operation, **params)
        current_time = time.time()
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached_time = self.memory_cache_ttl.get(cache_key, 0)
            ttl = self.cache_ttls.get(operation, 300)
            
            if current_time - cached_time < ttl:
                logger.debug(f"Cache hit (memory): {cache_key}")
                return self.memory_cache[cache_key]
            else:
                # Expired - remove from memory cache
                del self.memory_cache[cache_key]
                del self.memory_cache_ttl[cache_key]
        
        # TODO: Check Redis cache for shared caching
        # redis_value = await self.redis_client.get(cache_key)
        # if redis_value:
        #     data = json.loads(redis_value)
        #     # Update memory cache
        #     self.memory_cache[cache_key] = data
        #     self.memory_cache_ttl[cache_key] = current_time
        #     return data
        
        return None
    
    async def set_cached(self, operation, data, **params):
        """Store data in cache"""
        cache_key = self._generate_cache_key(operation, **params)
        current_time = time.time()
        
        # Store in memory cache
        self.memory_cache[cache_key] = data
        self.memory_cache_ttl[cache_key] = current_time
        
        # TODO: Store in Redis with TTL
        # ttl = self.cache_ttls.get(operation, 300)
        # await self.redis_client.setex(
        #     cache_key, 
        #     ttl, 
        #     json.dumps(data, default=str)
        # )
        
        logger.debug(f"Cached: {cache_key}")
    
    def invalidate_cache(self, operation=None, **params):
        """Invalidate cache entries"""
        if operation:
            # Invalidate specific operation
            cache_key = self._generate_cache_key(operation, **params)
            self.memory_cache.pop(cache_key, None)
            self.memory_cache_ttl.pop(cache_key, None)
        else:
            # Clear all cache
            self.memory_cache.clear()
            self.memory_cache_ttl.clear()
        
        logger.debug(f"Cache invalidated: {operation or 'all'}")
```

## Connection Pooling

### HTTP Connection Pool

```python
class OptimizedHTTPClient:
    """HTTP client with connection pooling and retry logic"""
    
    def __init__(self):
        # Connection pool settings
        connector = aiohttp.TCPConnector(
            limit=100,              # Total connection pool size
            limit_per_host=20,      # Connections per host
            ttl_dns_cache=300,      # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,   # Keep connections alive
            enable_cleanup_closed=True
        )
        
        # Client session with optimized settings
        timeout = aiohttp.ClientTimeout(
            total=30,       # Total timeout
            connect=10,     # Connection timeout
            sock_read=20    # Socket read timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'secretGPT-MCP/1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
        )
    
    async def get_with_retry(self, url, params=None, max_retries=3):
        """GET request with retry logic"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Log successful request
                        latency = (time.time() - start_time) * 1000
                        logger.debug(f"API request successful: {url} ({latency:.1f}ms)")
                        
                        return data
                    
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    else:
                        response.raise_for_status()
                        
            except asyncio.TimeoutError:
                last_exception = TimeoutError(f"Request timeout: {url}")
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logger.warning(f"Request timeout, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
                
            except aiohttp.ClientError as e:
                last_exception = e
                wait_time = (attempt + 1) * 2
                logger.warning(f"Request failed: {e}, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
        
        # All retries exhausted
        raise last_exception or Exception(f"Max retries exceeded for {url}")
    
    async def close(self):
        """Clean up connections"""
        await self.session.close()
```

## Performance Monitoring

### Metrics Collection

```python
class PerformanceMonitor:
    """Monitor API performance and provide insights"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_cached': 0,
            'average_latency': 0,
            'endpoint_performance': {},
        }
        self.request_history = []
        self.history_limit = 1000
    
    def record_request(self, endpoint, operation, latency, success, cached=False):
        """Record request metrics"""
        self.metrics['requests_total'] += 1
        
        if success:
            self.metrics['requests_success'] += 1
        
        if cached:
            self.metrics['requests_cached'] += 1
        
        # Update average latency
        self.metrics['average_latency'] = (
            (self.metrics['average_latency'] * (self.metrics['requests_total'] - 1) + latency) 
            / self.metrics['requests_total']
        )
        
        # Record endpoint performance
        if endpoint not in self.metrics['endpoint_performance']:
            self.metrics['endpoint_performance'][endpoint] = {
                'requests': 0,
                'successes': 0,
                'average_latency': 0
            }
        
        ep_metrics = self.metrics['endpoint_performance'][endpoint]
        ep_metrics['requests'] += 1
        if success:
            ep_metrics['successes'] += 1
        
        ep_metrics['average_latency'] = (
            (ep_metrics['average_latency'] * (ep_metrics['requests'] - 1) + latency) 
            / ep_metrics['requests']
        )
        
        # Add to history
        self.request_history.append({
            'timestamp': time.time(),
            'endpoint': endpoint,
            'operation': operation,
            'latency': latency,
            'success': success,
            'cached': cached
        })
        
        # Trim history
        if len(self.request_history) > self.history_limit:
            self.request_history = self.request_history[-self.history_limit:]
    
    def get_performance_report(self):
        """Generate performance report"""
        total_requests = self.metrics['requests_total']
        if total_requests == 0:
            return "No requests recorded"
        
        success_rate = (self.metrics['requests_success'] / total_requests) * 100
        cache_hit_rate = (self.metrics['requests_cached'] / total_requests) * 100
        
        report = f"""Secret Network API Performance Report:
Total Requests: {total_requests}
Success Rate: {success_rate:.1f}%
Cache Hit Rate: {cache_hit_rate:.1f}%
Average Latency: {self.metrics['average_latency']:.1f}ms

Endpoint Performance:"""
        
        for endpoint, metrics in self.metrics['endpoint_performance'].items():
            ep_success_rate = (metrics['successes'] / metrics['requests']) * 100
            report += f"""
  {endpoint}:
    Requests: {metrics['requests']}
    Success Rate: {ep_success_rate:.1f}%
    Avg Latency: {metrics['average_latency']:.1f}ms"""
        
        return report
```

## Integration Example

### Optimized MCP Tool Implementation

```python
class OptimizedSecretNetworkMCPTool:
    """Optimized Secret Network MCP tool with all performance features"""
    
    def __init__(self, network="mainnet"):
        self.endpoint_manager = SecretNetworkEndpointManager(network)
        self.cache = SecretNetworkCache()
        self.http_client = OptimizedHTTPClient()
        self.performance_monitor = PerformanceMonitor()
    
    async def execute_balance_query_optimized(self, arguments):
        """Optimized balance query with all performance features"""
        address = arguments["address"]
        denom = arguments.get("denom", "uscrt")
        
        try:
            result = await self.query_with_optimization(
                "balance", 
                address=address, 
                denom=denom
            )
            
            return {
                "content": [{
                    "type": "text",
                    "text": result
                }],
                "isError": False
            }
            
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error querying balance: {str(e)}"
                }],
                "isError": True
            }
    
    async def query_with_optimization(self, query_type, **params):
        """Execute query with all optimizations"""
        start_time = time.time()
        endpoint = None
        
        try:
            # Check cache first
            cached_result = await self.cache.get_cached(query_type, **params)
            if cached_result:
                self.performance_monitor.record_request(
                    "cache", query_type, 0, True, cached=True
                )
                return cached_result
            
            # Get optimal endpoint
            endpoint = await self.endpoint_manager.get_healthy_endpoint("lcd")
            
            # Build URL based on query type
            if query_type == "balance":
                url = f"{endpoint}/cosmos/bank/v1beta1/balances/{params['address']}/by_denom"
                query_params = {"denom": params["denom"]}
            elif query_type == "block_height":
                url = f"{endpoint}/cosmos/base/tendermint/v1beta1/node_info"
                query_params = None
            else:
                raise ValueError(f"Unknown query type: {query_type}")
            
            # Make optimized HTTP request
            response_data = await self.http_client.get_with_retry(url, query_params)
            
            # Process response
            if query_type == "balance":
                balance = response_data.get("balance", {})
                amount_uscrt = int(balance.get("amount", "0"))
                amount_scrt = amount_uscrt / 1_000_000
                result = f"Balance: {amount_scrt:.6f} SCRT ({amount_uscrt} uscrt)"
            elif query_type == "block_height":
                # This would need to be implemented based on actual response structure
                result = "Block height query processed"
            
            # Cache the result
            await self.cache.set_cached(query_type, result, **params)
            
            # Record metrics
            latency = (time.time() - start_time) * 1000
            self.performance_monitor.record_request(
                endpoint, query_type, latency, True, cached=False
            )
            
            return result
            
        except Exception as e:
            # Record failure metrics
            latency = (time.time() - start_time) * 1000
            self.performance_monitor.record_request(
                endpoint or "unknown", query_type, latency, False, cached=False
            )
            raise
    
    async def get_performance_stats(self):
        """Get performance statistics for monitoring"""
        return self.performance_monitor.get_performance_report()
    
    async def cleanup(self):
        """Clean up resources"""
        await self.http_client.close()
```

## Production Configuration

### Configuration Management

```yaml
# config/secret_network_optimization.yaml
secret_network:
  mainnet:
    endpoints:
      lcd:
        - url: "https://lcd.mainnet.secretsaturn.net"
          priority: 1
          timeout: 30
        - url: "https://secretnetwork-api.lavenderfive.com:443"
          priority: 2
          timeout: 30
        - url: "https://rest-secret.01node.com"
          priority: 3
          timeout: 30
      rpc:
        - url: "https://rpc.mainnet.secretsaturn.net"
          priority: 1
          timeout: 30
        - url: "https://secretnetwork-rpc.lavenderfive.com:443"
          priority: 2
          timeout: 30
  
  cache:
    ttl:
      block_height: 10
      balance: 30
      transaction: 3600
      validator_info: 300
    max_memory_size: 100MB
    
  performance:
    connection_pool_size: 100
    connections_per_host: 20
    request_timeout: 30
    retry_attempts: 3
    health_check_interval: 60
```

### Environment Variables

```bash
# Secret Network optimization settings
SECRET_NETWORK_CACHE_TTL_BALANCE=30
SECRET_NETWORK_CACHE_TTL_BLOCK_HEIGHT=10
SECRET_NETWORK_CONNECTION_POOL_SIZE=100
SECRET_NETWORK_REQUEST_TIMEOUT=30
SECRET_NETWORK_RETRY_ATTEMPTS=3
SECRET_NETWORK_HEALTH_CHECK_INTERVAL=60

# Redis cache (optional)
SECRET_NETWORK_REDIS_URL=redis://localhost:6379/1
SECRET_NETWORK_REDIS_TTL_DEFAULT=300
```

---

**Implementation Priority:**
1. **Multi-endpoint failover** for reliability
2. **Basic caching** for common queries (balances, block height)  
3. **Connection pooling** for HTTP efficiency
4. **Performance monitoring** for optimization insights
5. **Advanced caching** with Redis for multi-instance deployments

**Expected Performance Improvements:**
- **95% reduction** in response time for cached queries
- **99%+ availability** through endpoint failover
- **80%+ cache hit rate** for repeated queries
- **50% reduction** in API load through optimization

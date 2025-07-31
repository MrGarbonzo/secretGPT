"""
SecretGPTee Web Interface - Consumer-focused UI for secretGPT
Modern React-like experience with full Keplr wallet integration
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from hub.core.router import HubRouter, ComponentType

logger = logging.getLogger(__name__)


class SecretGPTeeInterface:
    """
    SecretGPTee Web Interface - Consumer-focused UI
    Features: Modern chat UI, Keplr wallet integration, advanced settings
    """
    
    def __init__(self, hub_router: HubRouter):
        """Initialize SecretGPTee interface with hub router integration"""
        self.hub_router = hub_router
        self.app = FastAPI(
            title="SecretGPTee - AI Chat with Secret Network",
            description="Consumer-focused AI chat interface with blockchain integration",
            version="1.0.0"
        )
        
        # Set up paths
        self.base_path = Path(__file__).parent
        self.template_path = self.base_path / "templates"
        self.static_path = self.base_path / "static"
        
        # Initialize Jinja2 templates
        self.templates = Jinja2Templates(directory=str(self.template_path))
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
        
        # Mount static files
        self._setup_static_files()
        
        logger.info("SecretGPTee interface initialized")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_static_files(self):
        """Mount static file directories"""
        try:
            # Create static directories if they don't exist
            self.static_path.mkdir(parents=True, exist_ok=True)
            (self.static_path / "css").mkdir(exist_ok=True)
            (self.static_path / "js").mkdir(exist_ok=True)
            (self.static_path / "img").mkdir(exist_ok=True)
            
            # Mount static files
            self.app.mount("/static", StaticFiles(directory=str(self.static_path)), name="static")
            logger.info("SecretGPTee static files mounted")
        except Exception as e:
            logger.error(f"Failed to setup SecretGPTee static files: {e}")
    
    def _setup_routes(self):
        """Setup all FastAPI routes for SecretGPTee"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """SecretGPTee main page - modern chat interface"""
            return self.templates.TemplateResponse(
                "index.html", 
                {
                    "request": request, 
                    "title": "SecretGPTee - AI Chat with Secret Network",
                    "interface_type": "secret_gptee"
                }
            )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint for SecretGPTee"""
            try:
                return {
                    "status": "healthy", 
                    "interface": "secret_gptee",
                    "hub_connection": "connected"
                }
            except Exception as e:
                logger.error(f"SecretGPTee health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")
        
        # Chat API Endpoints
        @self.app.post("/api/v1/chat")
        async def chat_endpoint(request: Request):
            """
            SecretGPTee chat endpoint with enhanced features
            Supports wallet integration and blockchain queries
            """
            try:
                data = await request.json()
                message = data.get("message", "")
                temperature = data.get("temperature", 0.7)
                system_prompt = data.get("system_prompt", "You are SecretGPTee, a helpful AI assistant integrated with the Secret Network blockchain. You can help with both general questions and blockchain-specific queries.")
                enable_tools = data.get("enable_tools", True)
                wallet_connected = data.get("wallet_connected", False)
                wallet_address = data.get("wallet_address", "")
                
                if not message:
                    raise HTTPException(status_code=400, detail="Message is required")
                
                # Enhanced system prompt for SecretGPTee with wallet context
                if wallet_connected and wallet_address:
                    system_prompt += f"\n\nThe user has connected their Keplr wallet with address: {wallet_address}. You can help them with Secret Network transactions, balance queries, and other blockchain operations."
                
                # Route through hub router
                response = await self.hub_router.route_message(
                    interface="secret_gptee",
                    message=message,
                    options={
                        "temperature": temperature,
                        "system_prompt": system_prompt,
                        "enable_tools": enable_tools
                    }
                )
                
                if response["success"]:
                    return {
                        "success": True,
                        "response": response["content"],
                        "model": response.get("model"),
                        "interface": "secret_gptee",
                        "tools_used": response.get("tools_used", []),
                        "wallet_context": {
                            "connected": wallet_connected,
                            "address": wallet_address if wallet_connected else None
                        }
                    }
                else:
                    logger.error(f"SecretGPTee chat failed: {response.get('error')}")
                    raise HTTPException(status_code=500, detail=response.get("error", "Chat failed"))
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"SecretGPTee chat endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/chat/stream")
        async def chat_stream_endpoint(request: Request):
            """
            SecretGPTee streaming chat endpoint
            Real-time responses with wallet integration
            """
            try:
                data = await request.json()
                message = data.get("message", "")
                temperature = data.get("temperature", 0.7)
                system_prompt = data.get("system_prompt", "You are SecretGPTee, a helpful AI assistant integrated with the Secret Network blockchain.")
                enable_tools = data.get("enable_tools", True)
                wallet_connected = data.get("wallet_connected", False)
                wallet_address = data.get("wallet_address", "")
                
                if not message:
                    raise HTTPException(status_code=400, detail="Message is required")
                
                # Enhanced system prompt with wallet context
                if wallet_connected and wallet_address:
                    system_prompt += f"\n\nWallet connected: {wallet_address}"
                
                async def event_generator():
                    """Generate Server-Sent Events for streaming response"""
                    try:
                        # Stream through hub router
                        async for chunk_response in self.hub_router.stream_message(
                            interface="secret_gptee",
                            message=message,
                            options={
                                "temperature": temperature,
                                "system_prompt": system_prompt,
                                "enable_tools": enable_tools
                            }
                        ):
                            # Add SecretGPTee-specific metadata
                            event_data = {
                                "success": chunk_response.get("success", True),
                                "chunk": chunk_response.get("chunk", {}),
                                "model": chunk_response.get("model"),
                                "interface": "secret_gptee",
                                "stream_id": chunk_response.get("stream_id"),
                                "wallet_context": {
                                    "connected": wallet_connected,
                                    "address": wallet_address if wallet_connected else None
                                }
                            }
                            
                            if not chunk_response.get("success", True):
                                event_data["error"] = chunk_response.get("error")
                            
                            # Send as SSE format
                            sse_data = f"data: {json.dumps(event_data)}\n\n"
                            yield sse_data
                            
                    except Exception as e:
                        logger.error(f"SecretGPTee streaming error: {e}")
                        error_event = {
                            "success": False,
                            "error": str(e),
                            "interface": "secret_gptee",
                            "chunk": {
                                "type": "stream_error",
                                "data": str(e),
                                "metadata": {"error": True}
                            }
                        }
                        yield f"data: {json.dumps(error_event)}\n\n"
                
                return StreamingResponse(
                    event_generator(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*",
                        "X-Accel-Buffering": "no"
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"SecretGPTee stream endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Wallet Integration Endpoints
        @self.app.post("/api/v1/wallet/connect")
        async def connect_wallet(request: Request):
            """Connect a Keplr wallet"""
            try:
                data = await request.json()
                address = data.get("address")
                name = data.get("name")
                is_hardware_wallet = data.get("isHardwareWallet", False)
                
                if not address:
                    raise HTTPException(status_code=400, detail="Wallet address required")
                
                # Use HTTP wallet service to connect
                from services.wallet_proxy.http_wallet_service import HTTPWalletService
                wallet_service = HTTPWalletService()
                
                await wallet_service.initialize()
                result = await wallet_service.connect_wallet(address, name, is_hardware_wallet)
                
                return result
                
            except Exception as e:
                logger.error(f"Wallet connect error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/wallet/status")
        async def wallet_status():
            """Get wallet service status"""
            try:
                wallet_service = self._get_wallet_proxy()
                if not wallet_service:
                    return {
                        "available": False,
                        "error": "Wallet proxy service not available"
                    }
                
                status = await wallet_service.get_status()
                return {
                    "available": True,
                    "status": status
                }
            except Exception as e:
                logger.error(f"Wallet status error: {e}")
                return {
                    "available": False,
                    "error": str(e)
                }
        
        @self.app.post("/api/v1/wallet/balance")
        async def get_wallet_balance(request: Request):
            """Get Secret Network balance for connected wallet"""
            try:
                data = await request.json()
                address = data.get("address")
                
                if not address:
                    raise HTTPException(status_code=400, detail="Wallet address required")
                
                # Try to use HTTP wallet service first
                from services.wallet_proxy.http_wallet_service import HTTPWalletService
                wallet_service = HTTPWalletService()
                
                try:
                    await wallet_service.initialize()
                    result = await wallet_service.get_balance(address)
                    
                    if result.get("success"):
                        return {
                            "success": True,
                            "address": address,
                            "amount": result.get("balance"),
                            "denom": result.get("denom"),
                            "formatted": result.get("formatted")
                        }
                except Exception as wallet_error:
                    logger.warning(f"HTTP wallet service failed, falling back to MCP: {wallet_error}")
                
                # Fallback to MCP service
                mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
                if not mcp_service:
                    raise HTTPException(status_code=503, detail="MCP service not available")
                
                result = await mcp_service.execute_tool("secret_query_balance", {"address": address})
                
                return {
                    "success": True,
                    "address": address,
                    "balance": result
                }
                
            except Exception as e:
                logger.error(f"Wallet balance error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/wallet/transaction/prepare")
        async def prepare_transaction(request: Request):
            """Prepare a Secret Network transaction"""
            try:
                data = await request.json()
                tx_type = data.get("type")  # "send", "contract_execute", etc.
                tx_data = data.get("data", {})
                
                wallet_service = self._get_wallet_proxy()
                if not wallet_service:
                    raise HTTPException(status_code=503, detail="Wallet service not available")
                
                prepared_tx = await wallet_service.prepare_transaction(tx_type, tx_data)
                
                return {
                    "success": True,
                    "transaction": prepared_tx
                }
                
            except Exception as e:
                logger.error(f"Transaction preparation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # System and Status Endpoints
        @self.app.get("/api/v1/models")
        async def get_models():
            """Get available AI models"""
            try:
                models = await self.hub_router.get_available_models()
                return {"models": models}
            except Exception as e:
                logger.error(f"Failed to get models: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/status")
        async def get_status():
            """Get SecretGPTee system status"""
            try:
                # Add SecretGPTee-specific status without circular hub calls
                wallet_service = self._get_wallet_proxy()
                wallet_available = wallet_service is not None
                
                return {
                    "interface": "secret_gptee",
                    "status": "operational",
                    "hub_connection": "connected",
                    "wallet_service": "operational" if wallet_available else "unavailable",
                    "features": {
                        "chat": True,
                        "streaming": True,
                        "wallet_integration": wallet_available,
                        "blockchain_tools": True,
                        "advanced_settings": True
                    }
                }
            except Exception as e:
                logger.error(f"SecretGPTee status endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # MCP Tools Integration
        @self.app.get("/api/v1/tools")
        async def get_available_tools():
            """Get available MCP tools for SecretGPTee"""
            try:
                mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
                if not mcp_service:
                    return {"tools": [], "count": 0}
                
                tools = await mcp_service.get_available_tools()
                
                # Filter and categorize tools for SecretGPTee UI
                blockchain_tools = [
                    tool for tool in tools 
                    if any(keyword in tool["name"].lower() for keyword in ["secret", "network", "balance", "transaction", "block"])
                ]
                
                return {
                    "tools": tools,
                    "blockchain_tools": blockchain_tools,
                    "count": len(tools)
                }
            except Exception as e:
                logger.error(f"Error getting SecretGPTee tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Settings and Configuration
        @self.app.get("/settings", response_class=HTMLResponse)
        async def settings_page(request: Request):
            """SecretGPTee settings page"""
            return self.templates.TemplateResponse(
                "settings.html",
                {
                    "request": request, 
                    "title": "SecretGPTee - Settings",
                    "interface_type": "secret_gptee"
                }
            )
        
        @self.app.get("/api/v1/settings")
        async def get_settings():
            """Get SecretGPTee settings"""
            # Return default settings for now
            return {
                "temperature": 0.7,
                "model": "deepseek-r1:70b",
                "enable_tools": True,
                "theme": "auto",
                "streaming": True,
                "wallet_auto_connect": False,
                "privacy_mode": False
            }
        
        @self.app.post("/api/v1/settings")
        async def update_settings(request: Request):
            """Update SecretGPTee settings"""
            try:
                settings = await request.json()
                # For now, just return the settings (implement persistence later)
                return {
                    "success": True,
                    "settings": settings
                }
            except Exception as e:
                logger.error(f"Settings update error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _get_wallet_proxy(self):
        """Get wallet proxy service from hub router"""
        return self.hub_router.get_component(ComponentType.WALLET_PROXY)
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
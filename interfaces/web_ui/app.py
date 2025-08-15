"""
Web UI Interface for secretGPT
Migrated from attest_ai following DETAILED_BUILD_PLAN.md patterns
REFERENCE: F:/coding/attest_ai/src/main.py (FastAPI app structure)
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from hub.core.router import HubRouter, ComponentType

logger = logging.getLogger(__name__)


class WebUIInterface:
    """
    Web UI Interface for secretGPT
    MIGRATE: Preserve existing attest_ai FastAPI routes but route through hub
    """
    
    def __init__(self, hub_router: HubRouter):
        """Initialize the Web UI interface with hub router integration"""
        self.hub_router = hub_router  # Route through hub instead of direct Secret AI
        self.app = FastAPI(
            title="AttestAI - Trusted AI Platform",
            description="Confidential AI Web Interface with Attestation",
            version="2.0.0"
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
        
        logger.info("Web UI Interface initialized")
    
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
            
            # Mount static files
            self.app.mount("/static", StaticFiles(directory=str(self.static_path)), name="static")
            logger.info("Static files mounted")
        except Exception as e:
            logger.error(f"Failed to setup static files: {e}")
    
    def _setup_routes(self):
        """Setup all FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            """Main page - chat interface"""
            return self.templates.TemplateResponse(
                "index.html", 
                {"request": request, "title": "Attest AI - Trusted AI Chat"}
            )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                return {"status": "healthy", "interface": "attest_ai", "hub_connection": "connected"}
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")
        
        @self.app.post("/api/v1/chat")
        async def chat_endpoint(request: Request):
            """
            Chat endpoint - routes through hub to Secret AI
            CRITICAL: Routes through hub router (NOT direct Secret AI calls)
            """
            try:
                data = await request.json()
                message = data.get("message", "")
                temperature = data.get("temperature", 0.7)
                system_prompt = data.get("system_prompt", "You are a helpful assistant.")
                
                if not message:
                    raise HTTPException(status_code=400, detail="Message is required")
                
                # Route through Phase 1 hub router
                response = await self.hub_router.route_message(
                    interface="web_ui",
                    message=message,
                    options={
                        "temperature": temperature,
                        "system_prompt": system_prompt
                    }
                )
                
                if response["success"]:
                    return {
                        "success": True,
                        "response": response["content"],
                        "model": response.get("model"),
                        "interface": "web_ui"
                    }
                else:
                    logger.error(f"Chat failed: {response.get('error')}")
                    raise HTTPException(status_code=500, detail=response.get("error", "Chat failed"))
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Chat endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/chat/stream")
        async def chat_stream_endpoint(request: Request):
            """
            Server-Sent Events streaming chat endpoint
            Routes through hub to Secret AI for real-time streaming responses
            """
            try:
                data = await request.json()
                message = data.get("message", "")
                temperature = data.get("temperature", 0.7)
                system_prompt = data.get("system_prompt", "You are a helpful assistant.")
                
                if not message:
                    raise HTTPException(status_code=400, detail="Message is required")
                
                async def event_generator():
                    """Generate Server-Sent Events for streaming response"""
                    try:
                        # Stream through hub router
                        async for chunk_response in self.hub_router.stream_message(
                            interface="web_ui",
                            message=message,
                            options={
                                "temperature": temperature,
                                "system_prompt": system_prompt
                            }
                        ):
                            # Format as SSE event
                            event_data = {
                                "success": chunk_response.get("success", True),
                                "chunk": chunk_response.get("chunk", {}),
                                "model": chunk_response.get("model"),
                                "interface": chunk_response.get("interface"),
                                "stream_id": chunk_response.get("stream_id")
                            }
                            
                            if not chunk_response.get("success", True):
                                event_data["error"] = chunk_response.get("error")
                            
                            # Send as SSE format
                            sse_data = f"data: {json.dumps(event_data)}\n\n"
                            yield sse_data
                            
                    except Exception as e:
                        logger.error(f"Streaming error: {e}")
                        error_event = {
                            "success": False,
                            "error": str(e),
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
                        "X-Accel-Buffering": "no"  # Disable nginx buffering
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Stream endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/models")
        async def get_models():
            """Get available models from Secret AI via hub"""
            try:
                models = await self.hub_router.get_available_models()
                return {"models": models}
            except Exception as e:
                logger.error(f"Failed to get models: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/status")
        async def get_status():
            """Get system status including attestation info"""
            try:
                # Simple status without circular hub calls
                attestation_service = self._get_attestation_service()
                attestation_available = attestation_service is not None
                
                # Check Secret AI component status
                secret_ai_status = "unavailable"
                try:
                    secret_ai = self.hub_router.get_component(ComponentType.SECRET_AI)
                    if secret_ai and hasattr(secret_ai, 'chat_client'):
                        secret_ai_status = "operational" if secret_ai.chat_client else "not_initialized"
                    elif secret_ai:
                        secret_ai_status = "registered"
                except Exception as e:
                    logger.warning(f"Could not check Secret AI status: {e}")
                    secret_ai_status = "error"
                
                return {
                    "interface": "attest_ai",
                    "status": "operational",
                    "hub_connection": "connected",
                    "attestation_service": "operational" if attestation_available else "unavailable",
                    "components": {
                        "secret_ai": secret_ai_status
                    },
                    "features": {
                        "chat": True,
                        "attestation": attestation_available,
                        "proof_generation": True,
                        "mcp_tools": True
                    }
                }
            except Exception as e:
                logger.error(f"Status endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/attestation", response_class=HTMLResponse)
        async def attestation_page(request: Request):
            """Attestation verification page"""
            return self.templates.TemplateResponse(
                "attestation.html",
                {"request": request, "title": "Attest AI - Attestation Verification"}
            )
        
        @self.app.get("/api/v1/attestation/self")
        async def get_self_attestation():
            """
            Get self VM attestation from localhost:29343/cpu.html
            REFERENCE: secretVM-full-verification.txt
            """
            try:
                attestation_service = self._get_attestation_service()
                if not attestation_service:
                    raise HTTPException(status_code=503, detail="Attestation service not available")
                
                attestation = await attestation_service.get_self_attestation()
                return attestation
            except Exception as e:
                logger.error(f"Self attestation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/attestation/secret-ai")
        async def get_secret_ai_attestation():
            """Get Secret AI VM attestation (for dual attestation)"""
            try:
                attestation_service = self._get_attestation_service()
                if not attestation_service:
                    raise HTTPException(status_code=503, detail="Attestation service not available")
                
                attestation = await attestation_service.get_secret_ai_attestation()
                return attestation
            except Exception as e:
                logger.error(f"Secret AI attestation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/system/container-info")
        async def get_container_info():
            """Get information about the running Docker container"""
            try:
                container_info = await self._get_container_info()
                return {
                    "success": True,
                    "container_info": container_info
                }
            except Exception as e:
                logger.error(f"Container info error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "container_info": {
                        "image_name": "ghcr.io/mrgarbonzo/secretgpt",
                        "image_tag": "unknown",
                        "build_time": "unknown",
                        "image_sha": "unknown"
                    }
                }
        
        @self.app.post("/api/v1/proof/generate")
        async def generate_proof(
            question: str = Form(...),
            answer: str = Form(...),
            password: str = Form(...),
            conversation_history: str = Form(None)
        ):
            """
            Generate encrypted proof file with dual VM attestation
            REFERENCE: F:/coding/attest_ai/src/encryption/proof_manager.py
            """
            try:
                proof_manager = self._get_proof_manager()
                if not proof_manager:
                    raise HTTPException(status_code=503, detail="Proof manager not available")
                
                # Parse conversation history if provided
                parsed_conversation_history = None
                if conversation_history:
                    try:
                        parsed_conversation_history = json.loads(conversation_history)
                    except json.JSONDecodeError:
                        logger.warning("Invalid conversation history JSON, ignoring")
                
                # Generate proof with dual attestation
                proof_file = await proof_manager.generate_proof(
                    question=question,
                    answer=answer,
                    password=password,
                    conversation_history=parsed_conversation_history
                )
                
                return FileResponse(
                    proof_file,
                    filename=f"proof_{proof_file.name}",
                    media_type="application/octet-stream"
                )
                
            except Exception as e:
                logger.error(f"Proof generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/proof/verify")
        async def verify_proof(file: UploadFile = File(...), password: str = Form(...)):
            """Verify and decrypt proof file"""
            try:
                proof_manager = self._get_proof_manager()
                if not proof_manager:
                    raise HTTPException(status_code=503, detail="Proof manager not available")
                
                # Read uploaded file
                content = await file.read()
                
                # Verify proof
                result = await proof_manager.verify_proof(content, password)
                return result
                
            except Exception as e:
                logger.error(f"Proof verification error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _get_attestation_service(self):
        """Get attestation service from hub router"""
        # Return the attestation service if available via monkey patching
        return getattr(self, '_attestation_service_instance', None)
    
    def _get_proof_manager(self):
        """Get proof manager service"""
        # Return the proof manager if available via monkey patching
        return getattr(self, '_proof_manager_instance', None)
    
    async def _get_container_info(self) -> dict:
        """Get information about the running Docker container"""
        import os
        import subprocess
        import json
        from datetime import datetime
        
        try:
            # Try to get container info from environment variables first
            container_info = {
                "image_name": os.getenv("DOCKER_IMAGE", "unknown"),
                "image_tag": os.getenv("DOCKER_TAG", "unknown"),
                "build_time": os.getenv("BUILD_TIME", "unknown"),
                "image_sha": os.getenv("IMAGE_SHA", "unknown")
            }
            
            # If running in Docker, try to get more info
            try:
                # Check if we're in a container by looking for .dockerenv
                if os.path.exists("/.dockerenv"):
                    # Try to get container ID from cgroup
                    with open("/proc/self/cgroup", "r") as f:
                        cgroup_content = f.read()
                        # Extract container ID from cgroup path
                        for line in cgroup_content.split("\n"):
                            if "docker" in line and "/" in line:
                                # Extract potential container ID
                                parts = line.strip().split("/")
                                if len(parts) > 1:
                                    container_id = parts[-1][:12]  # First 12 chars
                                    break
                    
                    # Try to get image info from Docker if available
                    try:
                        result = subprocess.run(
                            ["docker", "inspect", container_id],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            inspect_data = json.loads(result.stdout)[0]
                            image_info = inspect_data.get("Config", {})
                            
                            # Extract image information
                            if "Image" in inspect_data:
                                container_info["image_sha"] = inspect_data["Image"]
                            
                            # Get creation time
                            if "Created" in inspect_data:
                                container_info["build_time"] = inspect_data["Created"]
                                
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, json.JSONDecodeError):
                        # Docker commands not available or failed, use fallback
                        pass
                        
            except (OSError, IOError):
                # Not in container or can't read cgroup info
                pass
            
            # Set reasonable defaults if still unknown
            if container_info["image_name"] == "unknown":
                container_info["image_name"] = "ghcr.io/mrgarbonzo/secretgpt"
            
            if container_info["image_tag"] == "unknown":
                container_info["image_tag"] = "main"
                
            if container_info["build_time"] == "unknown":
                container_info["build_time"] = datetime.now().isoformat()
            
            return container_info
            
        except Exception as e:
            logger.error(f"Error getting container info: {e}")
            return {
                "image_name": "ghcr.io/mrgarbonzo/secretgpt",
                "image_tag": "main", 
                "build_time": datetime.now().isoformat(),
                "image_sha": "unavailable",
                "error": str(e)
            }
        
        # MCP Endpoints
        @self.app.get("/api/v1/mcp/tools")
        async def get_available_tools():
            """Get list of available MCP tools"""
            try:
                mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
                if not mcp_service:
                    raise HTTPException(status_code=503, detail="MCP service not available")
                
                tools = await mcp_service.get_available_tools()
                return {"tools": tools, "count": len(tools)}
            except Exception as e:
                logger.error(f"Error getting MCP tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/v1/mcp/resources")  
        async def get_available_resources():
            """Get list of available MCP resources"""
            try:
                mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
                if not mcp_service:
                    raise HTTPException(status_code=503, detail="MCP service not available")
                
                resources = await mcp_service.get_available_resources()
                return {"resources": resources, "count": len(resources)}
            except Exception as e:
                logger.error(f"Error getting MCP resources: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/v1/mcp/tools/{tool_name}/execute")
        async def execute_tool_directly(tool_name: str, request: Request):
            """Direct tool execution for testing/debugging"""
            try:
                mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
                if not mcp_service:
                    raise HTTPException(status_code=503, detail="MCP service not available")
                
                data = await request.json()
                arguments = data.get("arguments", {})
                
                result = await mcp_service.execute_tool(tool_name, arguments)
                return {"success": True, "result": result, "tool": tool_name}
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/v1/mcp/status")
        async def get_mcp_status():
            """Get MCP service status and capabilities"""
            try:
                mcp_service = self.hub_router.get_component(ComponentType.MCP_SERVICE)
                if not mcp_service:
                    return {"mcp_service": "not_available", "servers": {}, "capabilities": {}}
                
                status = await mcp_service.get_status()
                return status
            except Exception as e:
                logger.error(f"Error getting MCP status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @self.app.get("/api/v1/debug/version")
        async def get_debug_version():
            """Get version and feature information for debugging"""
            import datetime
            return {
                "mcp_integration": "enabled",
                "features": {
                    "mcp_debug_commands": True,
                    "flexible_command_format": True,
                    "aggressive_detection": True,
                    "secret_network_tools": True
                },
                "debug_commands": [
                    "/mcp status", "/mcp test", "/mcp tools", "/mcp exec <tool>",
                    "mcp test", "test secret network", "secret network status"
                ],
                "available_triggers": [
                    "secret network status", "chain information", 
                    "test secret network", "check secret network"
                ],
                "last_updated": "2024-12-20T10:00:00Z",
                "version": "mcp-integrated-v2"
            }
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
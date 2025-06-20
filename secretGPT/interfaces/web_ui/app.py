r"""
Web UI Interface for secretGPT
Migrated from attest_ai following DETAILED_BUILD_PLAN.md patterns
REFERENCE: F:\coding\attest_ai\src\main.py (FastAPI app structure)
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from secretGPT.hub.core.router import HubRouter, ComponentType

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
            title="secretGPT Web UI",
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
                {"request": request, "title": "secretGPT - Confidential AI Chat"}
            )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                status = await self.hub_router.get_system_status()
                return {"status": "healthy", "hub_status": status}
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
                status = await self.hub_router.get_system_status()
                
                # Add attestation service status
                attestation_service = self._get_attestation_service()
                if attestation_service:
                    status["attestation"] = await attestation_service.get_status()
                
                return status
            except Exception as e:
                logger.error(f"Status endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/attestation", response_class=HTMLResponse)
        async def attestation_page(request: Request):
            """Attestation verification page"""
            return self.templates.TemplateResponse(
                "attestation.html",
                {"request": request, "title": "VM Attestation Verification"}
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
        
        @self.app.post("/api/v1/proof/generate")
        async def generate_proof(
            question: str = Form(...),
            answer: str = Form(...),
            password: str = Form(...)
        ):
            """
            Generate encrypted proof file with dual VM attestation
            REFERENCE: F:\coding\attest_ai\src\encryption\proof_manager.py
            """
            try:
                proof_manager = self._get_proof_manager()
                if not proof_manager:
                    raise HTTPException(status_code=503, detail="Proof manager not available")
                
                # Generate proof with dual attestation
                proof_file = await proof_manager.generate_proof(
                    question=question,
                    answer=answer,
                    password=password
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
        # Will be implemented when attestation service is registered
        return None
    
    def _get_proof_manager(self):
        """Get proof manager service"""
        # Will be implemented when proof manager is created
        return None
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app
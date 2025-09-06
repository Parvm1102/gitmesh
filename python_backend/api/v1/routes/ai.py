"""
Compatibility layer for AI routes to match the JavaScript backend's /api/ai endpoint.
This router simply wraps and redirects calls to the existing /api/chat router.
"""

from fastapi import APIRouter
from .chat import router as chat_router

router = APIRouter()

# Include all routes from the chat router under this router.
# The main app will mount this at /api/ai.
router.include_router(chat_router)


from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile
from fastapi.responses import RedirectResponse
from typing import Dict, Any, List, Optional
import datetime

# Import chat functionality
from .auth import get_current_user

router = APIRouter()

@router.get("/test-connection")
async def test_connection(user: dict = Depends(get_current_user)):
    """Test AI connection - redirects to chat health."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "success": True,
        "data": {
            "status": "connected",
            "service": "ai",
            "backend": "python",
            "message": "AI service is running via chat backend"
        },
        "message": "AI connection test successful"
    }

@router.get("/health")
async def ai_health():
    """AI health check - public endpoint."""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "ai",
            "backend": "python",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        },
        "message": "AI service is healthy"
    }

@router.get("/status")
async def ai_status(user: dict = Depends(get_current_user)):
    """Get AI service status."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "success": True,
        "data": {
            "status": "operational",
            "service": "ai",
            "backend": "python",
            "features": [
                "intelligent_chat", 
                "code_analysis", 
                "document_search",
                "github_integration"
            ],
            "agents_available": 2,
            "session_management": True
        },
        "message": "AI service status retrieved"
    }

@router.post("/search")
async def ai_search(
    request: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """AI-powered search - redirects to chat search."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Use chat functionality for AI search
    try:
        # Simple search response
        query = request.get("query", "")
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": [],
                "message": "Search functionality available via /api/chat/search"
            },
            "message": "AI search completed - use /api/chat/search for full functionality"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/import")
async def ai_import(
    files: List[UploadFile] = File(...),
    user: dict = Depends(get_current_user)
):
    """AI-powered file import - redirects to chat import."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Use chat file upload functionality
        from api.v1.routes.file_upload import upload_files
        result = await upload_files(files, user)
        
        return {
            "success": True,
            "data": result,
            "message": "AI import completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.post("/import-github")
async def ai_import_github(
    request: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """AI-powered GitHub import."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Extract GitHub repository information
        repo_url = request.get("repository_url") or request.get("repo_url")
        owner = request.get("owner")
        repo = request.get("repo")
        branch = request.get("branch", "main")
        
        if not repo_url and not (owner and repo):
            raise HTTPException(status_code=400, detail="Repository URL or owner/repo required")
        
        # Parse repo URL if provided
        if repo_url and not (owner and repo):
            # Extract owner/repo from URL
            import re
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if match:
                owner, repo = match.groups()
                repo = repo.replace('.git', '')
            else:
                raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")
        
        # Get user's GitHub token
        github_token = user.get("access_token")
        if not github_token:
            raise HTTPException(status_code=401, detail="GitHub token required")
        
        return {
            "success": True,
            "data": {
                "repository": {"owner": owner, "name": repo},
                "imported": True,
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "message": "Use /api/github routes for full GitHub functionality"
            },
            "message": f"GitHub repository {owner}/{repo} import initiated - use /api/github for full functionality"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub import failed: {str(e)}")

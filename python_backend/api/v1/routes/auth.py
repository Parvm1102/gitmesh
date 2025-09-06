"""
Authentication routes for GitHub OAuth and user management
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Response, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from models.api.auth_models import (
    GitHubOAuthURLResponse, AuthStatusResponse, TokenValidationResponse,
    LogoutResponse, TokenRefreshResponse, UserProfileResponse,
    UserProfileUpdateRequest, UserNotesResponse, UserFiltersResponse,
    UserPinsResponse, UserSettingsResponse, UserSettingsUpdateRequest,
    UserSettingsResetResponse, User, UserNote, UserSavedFilter,
    UserPinnedItem, UserSettings
)
from utils.auth_utils import (
    github_oauth, jwt_handler, security_utils, rate_limit_manager,
    get_demo_user, get_demo_settings
)
from core.session_manager import get_session_manager

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

# In-memory storage for demo (replace with database in production)
oauth_states = {}
user_sessions = {}
user_data = {}
user_notes = {}
user_filters = {}
user_pins = {}
user_settings = {}


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current authenticated user."""
    if not credentials:
        return None
    
    token = credentials.credentials
    
    # Handle demo token
    if token == 'demo-token':
        return get_demo_user()
    
    try:
        # Verify JWT token
        payload = jwt_handler.verify_token(token)
        session_id = payload.get('session_id')
        
        if not session_id:
            logger.error("Token missing session_id")
            return None
            
        # Get session from memory store
        if session_id in user_sessions:
            session = user_sessions[session_id]
            
            # Update last activity timestamp
            session['last_activity'] = datetime.now()
            
            # Check if session is expired (optional additional check)
            session_duration = (datetime.now() - session['created_at']).total_seconds()
            max_session_duration = 7 * 24 * 60 * 60  # 7 days in seconds
            
            if session_duration > max_session_duration:
                logger.warning(f"Session {session_id[:8]}... has exceeded maximum duration")
                # We could invalidate the session here, but let's keep it active
                # del user_sessions[session_id]
                # return None
            
            return session
        else:
            logger.warning(f"Session {session_id[:8]}... not found")
            return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


def require_auth(user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authentication."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


@router.get("/github/url", response_model=GitHubOAuthURLResponse)
async def get_github_oauth_url(request: Request):
    """Generate GitHub OAuth authorization URL."""
    # Rate limiting (more lenient for development)
    client_ip = request.client.host
    if rate_limit_manager.is_rate_limited(f"oauth_initiate_{client_ip}", max_requests=50, window_minutes=15):
        raise HTTPException(status_code=429, detail="Too many OAuth requests")
    
    # Generate secure state token
    state = security_utils.generate_secure_token(32)
    
    # Validate redirect URI
    allowed_origins = github_oauth.get_allowed_origins()
    if not security_utils.validate_redirect_uri(github_oauth.callback_url, allowed_origins):
        logger.error(f"Invalid redirect URI configuration: {github_oauth.callback_url}")
        raise HTTPException(status_code=400, detail="Invalid redirect URI configuration")
    
    # Store state with metadata
    oauth_states[state] = {
        'client_ip': client_ip,
        'user_agent': request.headers.get('user-agent'),
        'timestamp': datetime.now(),
        'used': False,
        'expires_at': datetime.now() + timedelta(minutes=10)
    }
    
    # Generate auth URL
    auth_url = github_oauth.generate_auth_url(state)
    
    # Log OAuth initiation (similar to JavaScript backend)
    logger.info(f"OAuth URL generated for client {client_ip[:10]}... with state {state[:10]}...")
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.get("/github/callback")
async def github_oauth_callback(
    request: Request,
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None)
):
    """Handle GitHub OAuth callback."""
    client_ip = request.client.host
    
    logger.info(f"🔵 OAuth callback started: {datetime.now().isoformat()}")
    
    # Rate limiting (more lenient for development)
    if rate_limit_manager.is_rate_limited(f"oauth_callback_{client_ip}", max_requests=100, window_minutes=5):
        return _redirect_with_error("Rate Limit Exceeded", "Too many authentication attempts. Please try again later.")
    
    # Enhanced state validation with additional security
    if state:
        # Validate state
        if state not in oauth_states:
            logger.error(f"❌ Invalid OAuth state: {state}")
            return _redirect_with_error("OAuth State Error", "Invalid OAuth state. Please try again.")
        
        state_data = oauth_states[state]
        
        # Check if state already used
        if state_data['used']:
            logger.error(f"❌ OAuth state already used: {state}")
            return _redirect_with_error("OAuth State Error", "OAuth state already used. Please try again.")
        
        # Check state expiration
        if datetime.now() > state_data['expires_at']:
            logger.error(f"❌ OAuth state expired: {state}")
            del oauth_states[state]
            return _redirect_with_error("OAuth State Error", "OAuth state expired. Please try again.")
        
        # Additional security checks
        if state_data['client_ip'] != client_ip:
            logger.error(f"❌ OAuth state IP mismatch: stored={state_data['client_ip']}, actual={client_ip}")
            return _redirect_with_error("Security Error", "Security validation failed. Please try again.")
        
        # Mark state as used
        state_data['used'] = True
        logger.info(f"✅ OAuth state validated: {state}")
    else:
        logger.error("❌ No OAuth state provided")
        return _redirect_with_error("OAuth State Error", "Missing OAuth state. Please try again.")
    
    if not code:
        logger.error("❌ No authorization code received")
        return _redirect_with_error("Authorization code required", "GitHub authorization code is missing")
    
    try:
        logger.info("🔄 Exchanging code for access token...")
        # Exchange code for token
        token_response = await github_oauth.exchange_code_for_token(code)
        
        if 'error' in token_response:
            error = token_response['error']
            error_description = token_response.get('error_description', 'Unknown OAuth error')
            
            logger.error(f"❌ GitHub OAuth error: {error} - {error_description}")
            
            # Provide more specific error messages for common OAuth errors
            if error == 'bad_verification_code':
                error_message = 'The OAuth code has expired or was already used. This often happens when the server restarts during authentication. Please try logging in again.'
            elif error == 'invalid_client':
                error_message = 'OAuth client configuration error. Please contact support.'
            elif error == 'redirect_uri_mismatch':
                error_message = 'OAuth redirect URI mismatch. Please contact support.'
            else:
                error_message = error_description
                
            return _redirect_with_error("GitHub OAuth Error", error_message)
            
        if 'access_token' not in token_response:
            logger.error("❌ No access token received from GitHub")
            return _redirect_with_error("Access token missing", "GitHub did not return an access token")
        
        logger.info("✅ Token exchange completed")
        access_token = token_response['access_token']
        
        logger.info("🔄 Getting user profile from GitHub...")
        # Get user profile from GitHub
        user_profile = await github_oauth.get_user_profile(access_token)
        logger.info(f"✅ User profile received: {user_profile.get('login')}")
        
        # Create or update user
        github_id = user_profile['id']
        login = user_profile['login']
        
        logger.info(f"🔄 Checking user in database: {github_id}")
        
        # Check if user exists
        existing_user = user_data.get(github_id)
        if not existing_user:
            logger.info("🔄 Creating new user in database...")
            user_info = {
                'id': github_id,
                'github_id': github_id,
                'login': login,
                'name': user_profile.get('name'),
                'email': user_profile.get('email'),
                'avatar_url': user_profile['avatar_url'],
                'bio': user_profile.get('bio'),
                'location': user_profile.get('location'),
                'company': user_profile.get('company'),
                'blog': user_profile.get('blog'),
                'twitter_username': user_profile.get('twitter_username'),
                'public_repos': user_profile.get('public_repos', 0),
                'followers': user_profile.get('followers', 0),
                'following': user_profile.get('following', 0),
                'created_at': user_profile.get('created_at'),
                'updated_at': user_profile.get('updated_at')
            }
        else:
            logger.info("🔄 Updating existing user in database...")
            user_info = existing_user
            # Update existing user
            user_info.update({
                'name': user_profile.get('name'),
                'email': user_profile.get('email'),
                'avatar_url': user_profile['avatar_url'],
                'bio': user_profile.get('bio'),
                'location': user_profile.get('location'),
                'company': user_profile.get('company'),
                'blog': user_profile.get('blog'),
                'twitter_username': user_profile.get('twitter_username'),
                'public_repos': user_profile.get('public_repos', 0),
                'followers': user_profile.get('followers', 0),
                'following': user_profile.get('following', 0),
                'updated_at': user_profile.get('updated_at')
            })
        
        # Update last login time
        user_info['last_login'] = datetime.now().isoformat()
        
        # Store user data
        user_data[github_id] = user_info
        
        logger.info("🔄 Checking for existing user sessions...")
        # Check for existing sessions - we could implement additional logic here
        
        logger.info("🔄 Creating session with encrypted token...")
        # Create session
        session_id = security_utils.generate_secure_token(32)
        session_data = {
            'session_id': session_id,
            'user_id': github_id,
            'github_id': github_id,
            'login': login,
            'name': user_profile.get('name'),
            'avatar_url': user_profile['avatar_url'],
            'access_token': security_utils.encrypt_token(access_token),
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        
        user_sessions[session_id] = session_data
        
        logger.info("🔄 Generating JWT token...")
        # Generate JWT token
        jwt_payload = {
            'session_id': session_id,
            'github_id': github_id,
            'login': login
        }
        jwt_token = jwt_handler.create_access_token(jwt_payload)
        
        # Clean up OAuth state
        if state:
            del oauth_states[state]
        
        # Redirect to frontend with token and full user profile
        frontend_url = _get_frontend_url()
        
        # Ensure user_info has the proper structure expected by frontend
        user_profile_for_frontend = {
            "id": user_info["id"],
            "login": user_info["login"],
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "avatar_url": user_info["avatar_url"],
            "bio": user_info.get("bio", ""),
            "location": user_info.get("location", ""),
            "company": user_info.get("company", ""),
            "blog": user_info.get("blog", ""),
            "twitter_username": user_info.get("twitter_username", ""),
            "public_repos": user_info.get("public_repos", 0),
            "followers": user_info.get("followers", 0),
            "following": user_info.get("following", 0),
            "created_at": user_info.get("created_at", ""),
            "lastLogin": user_info.get("last_login", datetime.now().isoformat())
        }
        
        logger.info("🔄 Redirecting directly to homepage...")
        from urllib.parse import quote
        user_json = quote(json.dumps(user_profile_for_frontend))
        redirect_url = f"{frontend_url}/?auth_token={jwt_token}&auth_user={user_json}"
        
        logger.info(f"✅ OAuth callback completed, redirecting to frontend: {redirect_url[:100]}...")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"❌ GitHub OAuth callback error: {e}")
        return _redirect_with_error("Authentication failed", str(e))


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Get authentication status."""
    if not user:
        return {"authenticated": False, "message": "No Bearer token provided"}
    
    # Handle demo mode
    if user.get('login') == 'demo-user':
        return {
            "authenticated": True,
            "user": {
                "id": user['id'],
                "login": user['login'],
                "name": user['name'],
                "avatar_url": user['avatar_url']
            },
            "mode": "demo"
        }
    
    # Test GitHub API access
    github_api_test = "success"
    github_user = user.get('login')
    github_error = None
    
    try:
        # In a real implementation, we would test GitHub API access here
        # This matches the JS backend which doesn't actually do a test at this endpoint
        pass
    except Exception as e:
        github_api_test = "failed"
        github_error = str(e)
    
    return {
        "authenticated": True,
        "user": {
            "id": user['github_id'],
            "login": user['login'],
            "name": user['name'],
            "avatar_url": user['avatar_url']
        },
        "mode": "github",
        "githubApiTest": github_api_test,
        "githubUser": github_user,
        "githubError": github_error
    }


@router.get("/validate", response_model=TokenValidationResponse)
async def validate_token(user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Validate authentication token."""
    if not user:
        raise HTTPException(
            status_code=401, 
            detail={
                "valid": False,
                "error": "Access token required",
                "message": "Please provide a valid Bearer token"
            }
        )
    
    # Handle demo token
    if user.get('login') == 'demo-user':
        return {
            "valid": True,
            "user": {
                "id": 1,
                "login": "demo-user",
                "name": "Demo User",
                "email": "demo@example.com",
                "avatar_url": "https://github.com/github.png",
                "bio": "Demo user for development",
                "location": "Demo City",
                "company": "Demo Corp",
                "blog": "https://demo.com",
                "twitter_username": "demo",
                "public_repos": 2,
                "followers": 50,
                "following": 25,
                "created_at": "2023-01-01T00:00:00Z",
                "lastLogin": datetime.now().isoformat()
            }
        }
    
    # Fetch user data from storage if it exists
    github_id = user.get('github_id')
    user_profile = user_data.get(github_id, user)
    
    return {
        "valid": True,
        "user": {
            "id": user_profile.get('id', github_id),
            "github_id": github_id,
            "login": user_profile.get('login'),
            "name": user_profile.get('name'),
            "avatar_url": user_profile.get('avatar_url'),
            "email": user_profile.get('email'),
            "bio": user_profile.get('bio'),
            "location": user_profile.get('location'),
            "company": user_profile.get('company'),
            "blog": user_profile.get('blog'),
            "twitter_username": user_profile.get('twitter_username'),
            "public_repos": user_profile.get('public_repos', 0),
            "followers": user_profile.get('followers', 0),
            "following": user_profile.get('following', 0),
            "created_at": user_profile.get('created_at'),
            "lastLogin": user_profile.get('last_login', user_profile.get('lastLogin', datetime.now().isoformat()))
        }
    }


@router.post("/logout", response_model=LogoutResponse)
async def logout(user: Dict[str, Any] = Depends(require_auth)):
    """Logout user."""
    session_id = user.get('session_id')
    if session_id and session_id in user_sessions:
        del user_sessions[session_id]
    
    return {
        "message": "Successfully logged out",
        "success": True
    }


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=401, 
            detail={
                "error": "Access token required",
                "message": "Please provide a valid Bearer token"
            }
        )
    
    try:
        # Demo token doesn't need refresh, just return it back
        if credentials.credentials == 'demo-token':
            return {
                "token": 'demo-token',
                "message": "Demo token refreshed (unchanged)"
            }
            
        # Extract payload from token without verifying expiration
        payload = jwt_handler.verify_token(
            credentials.credentials, 
            verify_expiration=False
        )
        
        # Verify session still exists
        session_id = payload.get('session_id')
        if not session_id or session_id not in user_sessions:
            logger.warning(f"Attempted to refresh token with invalid session: {session_id}")
            raise HTTPException(
                status_code=401, 
                detail={
                    "error": "Invalid session",
                    "message": "Session not found or expired"
                }
            )
            
        # Create new token with the same payload
        new_token = jwt_handler.create_access_token({
            'session_id': session_id,
            'github_id': payload.get('github_id'),
            'login': payload.get('login')
        })
        
        # Update session last activity
        user_sessions[session_id]['last_activity'] = datetime.now()
        
        return {
            "token": new_token,
            "message": "Token refreshed successfully"
        }
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=401, 
            detail={
                "error": "Invalid token",
                "message": "Cannot refresh invalid token"
            }
        )


@router.get("/user", response_model=UserProfileResponse)
async def get_user_info(user: dict = Depends(get_current_user)):
    """Get current user information - alias for profile."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        profile_data = {
            "id": user.get("github_id"),
            "login": user.get("login"),
            "name": user.get("name"),
            "avatar_url": user.get("avatar_url"),
            "email": user.get("email"),
            "bio": user.get("bio"),
            "location": user.get("location"),
            "company": user.get("company"),
            "blog": user.get("blog"),
            "twitter_username": user.get("twitter_username"),
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "created_at": user.get("created_at"),
            "lastLogin": user.get("lastLogin"),
            "analytics": user.get("analytics", {})
        }
        
        return {
            "success": True,
            "data": {"user": profile_data},
            "message": "User information retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Error retrieving user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user information")


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(user: dict = Depends(get_current_user)):
    """Get current user profile."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Handle demo user
        if user.get('login') == 'demo-user':
            return {
                "user": get_demo_user()
            }
            
        user_id = user.get('github_id')
        
        if user_id in user_data:
            profile_user = user_data[user_id]
            return {
                "user": {
                    "id": profile_user['id'],
                    "login": profile_user['login'],
                    "name": profile_user['name'],
                    "avatar_url": profile_user['avatar_url'],
                    "email": profile_user.get('email'),
                    "bio": profile_user.get('bio'),
                    "location": profile_user.get('location'),
                    "company": profile_user.get('company'),
                    "blog": profile_user.get('blog'),
                    "twitter_username": profile_user.get('twitter_username'),
                    "public_repos": profile_user.get('public_repos', 0),
                    "followers": profile_user.get('followers', 0),
                    "following": profile_user.get('following', 0),
                    "created_at": profile_user.get('created_at'),
                    "lastLogin": profile_user.get('last_login', profile_user.get('lastLogin')),
                    "analytics": profile_user.get('analytics', {})
                }
            }
            
        # If user not found in in-memory storage
        return {
            "user": {
                "id": user.get("github_id"),
                "login": user.get("login"),
                "name": user.get("name"),
                "avatar_url": user.get("avatar_url"),
                "email": user.get("email"),
                "bio": user.get("bio"),
                "location": user.get("location"),
                "company": user.get("company"),
                "blog": user.get("blog"),
                "twitter_username": user.get("twitter_username"),
                "public_repos": user.get("public_repos", 0),
                "followers": user.get("followers", 0),
                "following": user.get("following", 0),
                "created_at": user.get("created_at"),
                "lastLogin": user.get("last_login", user.get("lastLogin")),
                "analytics": user.get("analytics", {})
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdateRequest,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Update user profile."""
    user_id = user['id']
    
    # Update user data
    if user_id in user_data:
        # Extract only the fields that can be updated
        update_data = profile_update.dict(exclude_none=True)
        
        # Validate fields similar to JavaScript backend
        if 'name' in update_data:
            name = update_data['name'].strip() if update_data['name'] else None
            if name and (len(name) < 1 or len(name) > 100):
                raise HTTPException(status_code=400, detail="Name must be between 1 and 100 characters")
            update_data['name'] = name
            
        if 'bio' in update_data:
            bio = update_data['bio'].strip() if update_data['bio'] else None
            if bio and len(bio) > 500:
                raise HTTPException(status_code=400, detail="Bio must be 500 characters or less")
            update_data['bio'] = bio
            
        if 'location' in update_data:
            location = update_data['location'].strip() if update_data['location'] else None
            if location and len(location) > 100:
                raise HTTPException(status_code=400, detail="Location must be 100 characters or less")
            update_data['location'] = location
            
        if 'company' in update_data:
            company = update_data['company'].strip() if update_data['company'] else None
            if company and len(company) > 100:
                raise HTTPException(status_code=400, detail="Company must be 100 characters or less")
            update_data['company'] = company
            
        if 'twitter_username' in update_data:
            twitter = update_data['twitter_username'].strip() if update_data['twitter_username'] else None
            if twitter and len(twitter) > 50:
                raise HTTPException(status_code=400, detail="Twitter username must be 50 characters or less")
            update_data['twitter_username'] = twitter
        
        user_data[user_id].update(update_data)
        user_data[user_id]['updated_at'] = datetime.now().isoformat()
        
        # Return response matching JavaScript backend structure
        updated_user = user_data[user_id]
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": updated_user['id'],
                "login": updated_user['login'],
                "name": updated_user['name'],
                "avatar_url": updated_user['avatar_url'],
                "email": updated_user['email'],
                "bio": updated_user['bio'],
                "location": updated_user['location'],
                "company": updated_user['company'],
                "blog": updated_user['blog'],
                "twitter_username": updated_user['twitter_username'],
                "public_repos": updated_user['public_repos'],
                "followers": updated_user['followers'],
                "following": updated_user['following'],
                "created_at": updated_user['created_at'],
                "lastLogin": updated_user.get('last_login', updated_user.get('lastLogin')),
                "analytics": updated_user.get('analytics')
            }
        }
    
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/notes", response_model=UserNotesResponse)
async def get_user_notes(user: Dict[str, Any] = Depends(require_auth)):
    """Get user notes."""
    user_id = user['id']
    notes = user_notes.get(user_id, [])
    return UserNotesResponse(notes=notes)


@router.post("/notes", response_model=UserNotesResponse)
async def create_user_note(
    note: UserNote,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Create user note."""
    user_id = user['id']
    if user_id not in user_notes:
        user_notes[user_id] = []
    
    user_notes[user_id].append(note)
    return UserNotesResponse(notes=user_notes[user_id])


@router.put("/notes/{id}", response_model=UserNotesResponse)
async def update_user_note(
    id: str,
    updates: Dict[str, Any],
    user: Dict[str, Any] = Depends(require_auth)
):
    """Update user note."""
    user_id = user['id']
    notes = user_notes.get(user_id, [])
    
    for note in notes:
        if note.id == id:
            for key, value in updates.items():
                if hasattr(note, key):
                    setattr(note, key, value)
            note.updated_at = datetime.now()
            break
    
    return UserNotesResponse(notes=notes)


@router.delete("/notes/{id}", response_model=UserNotesResponse)
async def delete_user_note(
    id: str,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Delete user note."""
    user_id = user['id']
    notes = user_notes.get(user_id, [])
    user_notes[user_id] = [note for note in notes if note.id != id]
    
    return UserNotesResponse(notes=user_notes[user_id])


@router.get("/filters", response_model=UserFiltersResponse)
async def get_user_filters(user: Dict[str, Any] = Depends(require_auth)):
    """Get user saved filters."""
    user_id = user['id']
    filters = user_filters.get(user_id, [])
    return UserFiltersResponse(filters=filters)


@router.post("/filters", response_model=UserFiltersResponse)
async def create_user_filter(
    filter_data: UserSavedFilter,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Create user saved filter."""
    user_id = user['id']
    if user_id not in user_filters:
        user_filters[user_id] = []
    
    user_filters[user_id].append(filter_data)
    return UserFiltersResponse(filters=user_filters[user_id])


@router.put("/filters/{id}", response_model=UserFiltersResponse)
async def update_user_filter(
    id: str,
    updates: Dict[str, Any],
    user: Dict[str, Any] = Depends(require_auth)
):
    """Update user saved filter."""
    user_id = user['id']
    filters = user_filters.get(user_id, [])
    
    for filter_item in filters:
        if filter_item.id == id:
            for key, value in updates.items():
                if hasattr(filter_item, key):
                    setattr(filter_item, key, value)
            filter_item.updated_at = datetime.now()
            break
    
    return UserFiltersResponse(filters=filters)


@router.delete("/filters/{id}", response_model=UserFiltersResponse)
async def delete_user_filter(
    id: str,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Delete user saved filter."""
    user_id = user['id']
    filters = user_filters.get(user_id, [])
    user_filters[user_id] = [f for f in filters if f.id != id]
    
    return UserFiltersResponse(filters=user_filters[user_id])


@router.get("/pins", response_model=UserPinsResponse)
async def get_user_pins(user: Dict[str, Any] = Depends(require_auth)):
    """Get user pinned items."""
    user_id = user['id']
    pins = user_pins.get(user_id, [])
    return UserPinsResponse(pins=pins)


@router.post("/pins", response_model=UserPinsResponse)
async def create_user_pin(
    pin: UserPinnedItem,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Create user pinned item."""
    user_id = user['id']
    if user_id not in user_pins:
        user_pins[user_id] = []
    
    user_pins[user_id].append(pin)
    return UserPinsResponse(pins=user_pins[user_id])


@router.delete("/pins/{id}", response_model=UserPinsResponse)
async def delete_user_pin(
    id: str,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Delete user pinned item."""
    user_id = user['id']
    pins = user_pins.get(user_id, [])
    user_pins[user_id] = [pin for pin in pins if pin.id != id]
    
    return UserPinsResponse(pins=user_pins[user_id])


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(user: Dict[str, Any] = Depends(require_auth)):
    """Get user settings."""
    user_id = user['id']
    
    # Handle demo mode
    if user.get('login') == 'demo-user':
        demo_settings = get_demo_settings()
        return {"settings": demo_settings}
    
    settings = user_settings.get(user_id, get_demo_settings())
    return {"settings": settings}


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdateRequest,
    user: Dict[str, Any] = Depends(require_auth)
):
    """Update user settings."""
    user_id = user['id']
    
    # Handle demo mode
    if user.get('login') == 'demo-user':
        demo_settings = get_demo_settings()
        update_data = settings_update.dict(exclude_none=True)
        
        # Merge with existing demo settings
        demo_settings.update(update_data)
        demo_settings['updated_at'] = datetime.now().isoformat()
        
        return {
            "settings": demo_settings,
            "message": "Settings updated successfully (demo mode)"
        }
    
    if user_id not in user_settings:
        user_settings[user_id] = get_demo_settings()
    
    update_data = settings_update.dict(exclude_none=True)
    user_settings[user_id].update(update_data)
    user_settings[user_id]['updated_at'] = datetime.now().isoformat()
    
    return {
        "settings": user_settings[user_id],
        "message": "Settings updated successfully"
    }


@router.post("/settings/reset", response_model=UserSettingsResetResponse)
async def reset_user_settings(user: Dict[str, Any] = Depends(require_auth)):
    """Reset user settings to defaults."""
    user_id = user['id']
    
    default_settings = get_demo_settings()
    
    # Handle demo mode
    if user.get('login') == 'demo-user':
        return {
            "settings": default_settings,
            "message": "Settings reset to default values (demo mode)"
        }
    
    user_settings[user_id] = default_settings
    
    return {
        "settings": default_settings,
        "message": "Settings reset to default values"
    }


def _get_frontend_url() -> str:
    """Get frontend URL based on environment."""
    # Use the FRONTEND_URL environment variable if set
    frontend_url = os.getenv('FRONTEND_URL')
    if frontend_url:
        return frontend_url
        
    # Otherwise use environment-specific defaults
    if os.getenv('NODE_ENV') == 'production':
        return 'https://your-frontend-domain.com'
        
    # Default to localhost for development
    return 'http://localhost:3000'


def _redirect_with_error(error_title: str, error_message: str) -> RedirectResponse:
    """Redirect to frontend with error parameters."""
    frontend_url = _get_frontend_url()
    
    from urllib.parse import quote
    redirect_url = f"{frontend_url}/?auth_error={quote(error_title)}&auth_message={quote(error_message)}"
    
    logger.error(f"❌ Redirecting to frontend with error: {error_title} - {error_message}")
    logger.debug(f"Redirect URL: {redirect_url}")
    
    return RedirectResponse(url=redirect_url)

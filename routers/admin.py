from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import psycopg2
from config import settings
from services.database_service import database_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str

class AdminSettingsRequest(BaseModel):
    top_k: Optional[int] = None
    min_score: Optional[float] = None
    voice: Optional[str] = None
    tts_enabled: Optional[bool] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_admin_by_email(email: str):
    """Get admin user from database"""
    try:
        conn = database_service.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, email, password_hash FROM admin_users WHERE email = %s", (email,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "password_hash": result[2]
            }
        return None
    except Exception as e:
        logger.error(f"Failed to get admin: {e}")
        return None

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.post("/login", response_model=LoginResponse)
async def admin_login(login_data: LoginRequest):
    """
    Admin login endpoint
    
    **Authentication**:
    - Use email and password stored in database
    - Create admin using: python create_admin.py create
    
    Returns JWT token for authenticated requests
    """
    # Get admin from database
    admin = get_admin_by_email(login_data.email)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, admin["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": admin["email"]})
    
    logger.info(f"Admin logged in: {admin['email']}")
    
    return LoginResponse(
        access_token=access_token,
        email=admin["email"]
    )

@router.get("/settings")
async def get_admin_settings(email: str = Depends(verify_token)):
    """
    Get admin settings from database
    
    Requires authentication token
    """
    try:
        settings_data = database_service.get_settings()
        return {
            **settings_data,
            "note": "use_legal_search and province are auto-detected from query"
        }
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")

@router.post("/settings")
async def update_admin_settings(
    settings_data: AdminSettingsRequest,
    email: str = Depends(verify_token)
):
    """
    Update admin settings in database
    
    Requires authentication token
    
    **Available Settings (Admin Only)**:
    - **top_k** (int): Number of results (1-20) - Default: 5
    - **min_score** (float): Minimum relevance score (0.0-1.0) - Default: 0.5
    - **voice** (str): TTS voice (alloy, echo, fable, onyx, nova, shimmer) - Default: alloy
    - **tts_enabled** (bool): Enable audio responses - Default: false
    """
    try:
        # Validate inputs
        if settings_data.top_k is not None:
            settings_data.top_k = max(1, min(20, settings_data.top_k))
        if settings_data.min_score is not None:
            settings_data.min_score = max(0.0, min(1.0, settings_data.min_score))
        if settings_data.voice is not None:
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if settings_data.voice not in valid_voices:
                raise HTTPException(status_code=400, detail=f"Invalid voice. Must be one of: {', '.join(valid_voices)}")
        
        # Update in database
        updated_settings = database_service.update_settings(
            top_k=settings_data.top_k,
            min_score=settings_data.min_score,
            voice=settings_data.voice,
            tts_enabled=settings_data.tts_enabled
        )
        
        logger.info(f"Admin settings updated by {email}")
        
        return {
            **updated_settings,
            "note": "use_legal_search and province are auto-detected from query"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

@router.get("/verify")
async def verify_admin_token(email: str = Depends(verify_token)):
    """
    Verify if token is valid
    
    Returns email if token is valid
    """
    return {"email": email, "valid": True}

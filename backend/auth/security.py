# backend/auth/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
import os

# Configuración desde variables de entorno (nunca hardcodeada)
class AuthSettings(BaseModel):
    SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ISSUER: str = "alzheimer-dt-api"
    AUDIENCE: str = "research-clients"

# Contexto de hashing con bcrypt (FIPS-compliant)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    scopes: list[str] = Field(default_factory=list)
    jti: str  # Unique token identifier for revocation

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta, jti: str, scopes: list[str]):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "nbf": datetime.now(timezone.utc),
        "iss": settings.ISSUER,
        "aud": settings.AUDIENCE,
        "jti": jti,
        "scopes": scopes
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependencia para proteger endpoints: valida JWT y verifica revocación"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        scopes: list[str] = payload.get("scopes", [])
        
        if user_id is None or jti is None:
            raise credentials_exception
        
        # Verificar revocación: ¿este jti está en la lista negra?
        if await is_token_revoked(jti, db):
            raise HTTPException(status_code=401, detail="Token revocado")
            
        token_data = TokenData(user_id=user_id, scopes=scopes, jti=jti)
        
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(token_data.user_id, db)
    if user is None:
        raise credentials_exception
    return user

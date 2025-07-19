import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import config

api_key_header = APIKeyHeader(name="X-API-Key",scheme_name="X-API-Key")
oauth2_scheme = APIKeyHeader(name="Authorization")

    

async def get_current_user(token: str = Depends(oauth2_scheme)):
    token = token.split(" ")[-1]
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return payload

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != config.X_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = await get_current_user(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user_id



def verify_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
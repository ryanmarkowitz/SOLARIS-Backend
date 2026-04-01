from fastapi import Request, HTTPException
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
import httpx
from core.config import settings

# initialize clerk once, not inside the function
clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

async def get_current_user(request: Request):
    httpx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
    )

    print("AUTH HEADER:", request.headers.get("authorization"))
    
    request_state = clerk.authenticate_request(
        httpx_request,
        AuthenticateRequestOptions(),
    )

    print("IS SIGNED IN:", request_state.is_signed_in)
    print("REASON:", request_state.reason)
    print("MESSAGE:", request_state.message)

    if not request_state.is_signed_in:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    return request_state.payload
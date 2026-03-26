from fastapi import Request, HTTPException
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
import httpx
from core.config import settings

# initialize clerk once, not inside the function
clerk = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)

async def get_current_user(request: Request):
    # convert FastAPI request to httpx request
    # Clerk needs the headers of the packet to get the authorization token
    httpx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
    )
    # verify token with clerk
    request_state = clerk.authenticate_request(
        httpx_request,
        auth_options=AuthenticateRequestOptions(
            authorized_parties=[settings.AUTHORIZED_PARTY]
        ),
    )
    # raise 401 if invalid
    if not request_state.is_signed_in:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    # return payload if valid
    return request_state.payload

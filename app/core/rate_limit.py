from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


limiter = Limiter(key_func=get_remote_address)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )


# Rate limit configurations
LOGIN_LIMIT = "5/minute"
REQUEST_CREATE_LIMIT = "10/minute"
REQUEST_LIST_LIMIT = "30/minute"
REQUEST_UPDATE_LIMIT = "10/minute"

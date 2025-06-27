from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from routes import auth
from routes import contacts

app = FastAPI()


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


app.include_router(auth.router, prefix="")
app.include_router(contacts.router, prefix="/contacts")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

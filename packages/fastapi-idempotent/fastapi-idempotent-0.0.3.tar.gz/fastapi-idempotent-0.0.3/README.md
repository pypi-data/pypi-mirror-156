# fastapi-idempotent


### How to use package fastapi-idempotent
```bash
# Install package using poetry
poetry add fastapi-idempotent

# Using pip
pip install fastapi-idempotent
```
### Set rate limit for FastAPI before starting server

Example code
- main.py
```bash
# Import package
from fastapi import FastAPI
from fastapi_idempotent import IdempotentMiddleWare
from core.config import settings # settings is class, where the configuration parameters are saved
from api.responses import JSONResponse

...
# Setup FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_PATH}/openapi.json",
    default_response_class=JSONResponse,
)
```
### Set idempotent for FastAPI
- Using redis storage
```bash
# Default idempotent expired is 10800s
app.add_middleware(
    IdempotentMiddleWare,
    redis_url=settings.IDEMPOTENT_STORAGE_URL,  # type: str
)
```
or
```bash
app.add_middleware(
    IdempotentMiddleWare,
    idempotent_expired=settings.IDEMPOTENT_EXPIRED, # type: int
    redis_url=settings.IDEMPOTENT_STORAGE_URL,  # type: str
)
```
- Using memory storage
```bash
# Default idempotent expired is 10800s
app.add_middleware(
    IdempotentMiddleWare,
    testing=True, # type: bool
)
```
or
```bash
app.add_middleware(
    IdempotentMiddleWare,
    idempotent_expired=settings.IDEMPOTENT_EXPIRED,  # type: int
    testing=True, # type: bool
)
```
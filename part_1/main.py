import re
import json
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi.staticfiles import StaticFiles

from contacts.routes import router
from auth.routes import router as auth_router
from email_service.routes import router as email_router
from users.routes import router as users_router
from web_service.routes import router as html_router
from settings import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    r = await redis.Redis(host=settings.redis_server,
                          port=settings.redis_port,
                          password=settings.redis_pass,
                          db=0,
                          decode_responses=True,
                          encoding='utf-8')
    await FastAPILimiter.init(r)

    yield

app = FastAPI(lifespan=lifespan)

static_path = Path(__file__).parent / 'web_service' / 'static'

app.mount("/static", StaticFiles(directory=static_path), name='static')

app.include_router(router)
app.include_router(auth_router)
app.include_router(email_router)
app.include_router(users_router)
app.include_router(html_router)

origins = [
    "http://localhost:8080",
    "https://localhost:8080",
    "http://localhost:8000",
    "https://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def define_response(request: Request,
                          call_next):
    browser_regexp = (r"Mozilla|Chrome|Chromium|Apple|WebKit|" +
                      r"Edge|IE|MSIE|Firefox|Gecko")
    docs_redoc_regexp = (r"/docs$|/docs#|/docs/|/redoc$|/redoc#|/redoc/"
                         + r"|/openapi.json$|/static/|/favicon.ico$")

    swagger_static_match = re.search(pattern=docs_redoc_regexp,
                                     string=str(request.url),
                                     flags=re.I)
    ua_string = request.headers.get('user-agent')
    browser_match = re.search(browser_regexp, ua_string)
    response_type = "api"
    if swagger_static_match is None:
        if browser_match:
            response_type = "html"
        # request.headers.__dict__["_list"].append(
        #     ("response-type".encode(), response_type.encode())
        # )
    response = await call_next(request)
    content_type = response.headers.get('content-type')
    content_json = re.match(r"application/json", content_type)
    if all([response_type == "html",
            content_json]):
        print(response_type)
        print(request.url.path, request.url.query)
        print(response.headers)
        response_b = b""
        async for chunk in response.body_iterator:
            response_b += chunk
        print(json.loads(response_b)['detail'])
        return Response(content=response_b,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type)
    return response

if __name__ == "__main__":
    uvicorn.run(app="main:app",
                host="localhost",
                port=8080,
                reload=True)

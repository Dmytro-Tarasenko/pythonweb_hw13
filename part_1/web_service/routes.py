from pathlib import Path

from fastapi.templating import Jinja2Templates
from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse
from fastapi import Request


router = APIRouter(tags=['html'],
                   include_in_schema=True,
                   default_response_class=HTMLResponse)

templates = Jinja2Templates(Path(__file__).parent/'templates')


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request,
                                      name="index.html",
                                      context={})

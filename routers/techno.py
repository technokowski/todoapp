import sys
# from urllib.request import Request
sys.path.append("..")

from starlette.responses import RedirectResponse
from starlette import status
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



router = APIRouter(
    prefix="/techno",
    tags=["techno"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

@router.get("/home", response_class=HTMLResponse)
async def techno_home(request: Request):
    return templates.TemplateResponse("techno.html", {"request": request})
import sys
sys.path.append("..")
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette import status
from fastapi import Depends, APIRouter, Request, Form
from .auth import get_current_user, verify_password, get_password_hash
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/change-pw", response_class=HTMLResponse)
async def change_password(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("change-pw.html", {"request": request, "user": user})

@router.post("/change-pw", response_class=HTMLResponse)
async def save_change_password(request: Request, current_pw: str = Form(...), new_pw1: str = Form(...),
                       new_pw2: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()
    msg = "Passwords do not match"
    if user_model is not None:
        if verify_password(current_pw, user_model.hashed_password) and new_pw1 == new_pw2:
            user_model.hashed_password = get_password_hash(new_pw1)
            db.add(user_model)
            db.commit()
            msg = "Password Updated"
             
    return templates.TemplateResponse("change-pw.html", {"request": request, "msg": msg, "user": user})
    
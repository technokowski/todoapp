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

from yahoo_fin.stock_info import get_data
import yahoo_fin.stock_info as si
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Basically, all routes must begin with this prefix. Like registering in Django. 
# The main.py file will make an object of this and use it. 
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
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

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).order_by(models.Todos.id.desc()).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    # makes sure user is logged in
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...),
                        priority: int = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...),
                            description: str = Form(...), priority: str = Form(...),
                            db: Session = Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo.complete = not todo.complete
    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/secret", response_class=HTMLResponse)
async def secret_it(request: Request):
    user = await get_current_user(request)
    # if user is None:
    #     return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    msg = "magic"
    return templates.TemplateResponse("secret.html", {"request": request, "msg": msg, "user": user})

# The below code moved to extras.py, but I've kept it because I don't want to break anything... yet.
@router.get("/stocks", response_class=HTMLResponse)
async def stock_info(request: Request):
    x = await do_magic()
    print(x)
    msg = x[0]
    msg_c = x[1]
    msg_h = x[2]
    return templates.TemplateResponse("stocks.html", {"request": request, "msg": msg, "msg_c": msg_c, "msg_h": msg_h})

async def do_magic():
    quote_table = si.get_quote_table("^GSPC", dict_result=False)
    fifty_two_wh = quote_table['value'].loc[quote_table.index[0]]
    x = fifty_two_wh.split(" - ")
    high52 = x[1]
    hight_no_comma = high52.replace(',',"")
    f_high = float(hight_no_comma)

    current_value = round(quote_table['value'].loc[quote_table.index[5]],3)

    dads_magic = round(current_value / f_high * 100 - 100, 3)
    return dads_magic, current_value, f_high

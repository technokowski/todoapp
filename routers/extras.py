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
import humanize



router = APIRouter(
    prefix="/extras",
    tags=["extras"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

@router.get("/getstocks")
async def get_stocks(request: Request):
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

@router.get("/fincalc", response_class=HTMLResponse)
async def get_calc(request: Request):
    return templates.TemplateResponse("calculator.html", {"request": request})

@router.post("/fincalc")
async def calc_complete(request: Request, response_class=HTMLResponse, start: int = Form(...),
                        peryear: int = Form(...), years: int = Form(...)):
    rate: int = 1.10
    ostr = humanize.intcomma(start)
    for i in range(1, years + 1):
        start = start * rate
        start = start + peryear
        start = round(start, 2)

    start = humanize.intcomma(start)
    return templates.TemplateResponse("calcresults.html", {"request": request, "start": start, "peryear": peryear, "years": years, "ostr": ostr})




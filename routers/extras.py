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
import re 



router = APIRouter(
    prefix="/extras",
    tags=["extras"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

@router.get("/getstocks")
async def get_stocks(request: Request):
    user = await get_current_user(request)
    x = await do_magic()
    print(x)
    msg = x[0]
    msg_c = x[1]
    msg_h = x[2]
    return templates.TemplateResponse("stocks.html", {"request": request, "msg": msg, "msg_c": msg_c, "msg_h": msg_h, "user": user})

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
    user = await get_current_user(request)
    return templates.TemplateResponse("calculator.html", {"request": request, "user": user})

@router.post("/fincalc", response_class=HTMLResponse)
async def calc_complete(request: Request, start = Form(...),
                        peryear = Form(...), years = Form(...)):
    try:
        if "." in start:
            start = start.split('.')[0]
        if "." in peryear:
            peryear = peryear.split('.')[0]
        find_int = re.findall(r'\d+', start)
        start = int("".join(find_int))
        find_int = re.findall(r'\d+', peryear)
        peryear = int("".join(find_int))
        find_int = re.findall(r'\d+', years)
        years = int("".join(find_int))

    except:
        msg = "numbers must not have extra symbols - digits only"
        return templates.TemplateResponse("calculator.html", {"request": request, "msg": msg})

    fin = start
    ostr = humanize.intcomma(start)
    
    months = years * 12
    rate_percentage = 8/100
    mon_rate = rate_percentage / 12
    mon_rate_f = float(format(mon_rate, '.8f'))

    for i in range(0, months):
        fin = fin + peryear
        fin = fin + (fin * mon_rate_f)
    
    # This is for the Year
    # for i in range(1, years + 1):
    #     start = start * rate
    #     start = start + peryear
    #     start = round(start, 2)

    start = humanize.intcomma(float(format(fin, '.2f')))
    return templates.TemplateResponse("calcresults.html", {"request": request, "start": start, "peryear": peryear, "years": years, "ostr": ostr})




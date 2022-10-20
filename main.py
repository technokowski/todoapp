from fastapi import FastAPI, Depends
import models
from database import engine
from routers import auth, todos, users, extras
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static",StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/todos/secret", status_code=status.HTTP_302_FOUND)

# These are basically imports for the other files. 
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(extras.router)
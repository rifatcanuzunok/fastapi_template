import time

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from database import Base, engine
from routers import user_router

app = FastAPI()
app.include_router(user_router)
Base.metadata.create_all(bind=engine)


@app.get("/", response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url="/docs")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

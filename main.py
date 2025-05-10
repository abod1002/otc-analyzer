from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from ws_client import start_ws_clients

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# تشغيل WebSocket تلقائيًا عند تشغيل السيرفر (حتى بدون زيارة الموقع)
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_ws_clients())

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    message = "✅ تم بدء سحب الشموع من 4 عملات OTC. يتم حفظها في مجلد data."
    return templates.TemplateResponse("index.html", {"request": request, "message": message})

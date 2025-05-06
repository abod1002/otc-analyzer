from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
from websocket_client import start_socket  # استيراد سكربت WebSocket

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# تشغيل WebSocket عند بدء التطبيق
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_socket())

# الصفحة الرئيسية للموقع
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import websockets
import json
import os
import csv
from datetime import datetime

app = FastAPI()

# إعداد المسارات
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# مجلد لحفظ البيانات
os.makedirs("data", exist_ok=True)

# الأزواج المراد تتبعها
PAIRS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc"]

# حالة الاتصال لكل زوج
status_dict = {pair: "❌" for pair in PAIRS}

# معالجة بيانات الشمعة
def handle_candle(pair, candle):
    timestamp = datetime.fromtimestamp(candle["timestamp"])
    row = [
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        candle["open"],
        candle["close"],
        candle["high"],
        candle["low"],
        candle["volume"]
    ]
    file_path = f"data/{pair}.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["time", "open", "close", "high", "low", "volume"])
        writer.writerow(row)

# WebSocket لكل زوج
async def connect_socket(pair):
    url = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    while True:
        try:
            async with websockets.connect(url) as ws:
                await ws.send("40")
                await ws.send(f'42["subscribeCandles",{{"asset":"{pair}","period":300}}]')
                status_dict[pair] = "✅"
                while True:
                    msg = await ws.recv()
                    if msg.startswith('42["candle'):
                        data = json.loads(msg[2:])[1]
                        if "candle" in data:
                            handle_candle(pair, data["candle"])
        except Exception as e:
            print(f"Error with {pair}: {e}")
            status_dict[pair] = "❌"
            await asyncio.sleep(5)

# تشغيل جميع WebSocket
@app.on_event("startup")
async def start_collectors():
    for pair in PAIRS:
        asyncio.create_task(connect_socket(pair))

# الصفحة الرئيسية
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "status_dict": status_dict})

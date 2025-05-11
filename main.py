# تأكد من أن مكتبة websocket-client غير مثبتة! فقط websockets

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
templates = Jinja2Templates(directory="templates")

# إعداد مجلد البيانات
import os
import shutil

if os.path.exists("data") and not os.path.isdir("data"):
    os.remove("data")
os.makedirs("data", exist_ok=True)


# الأزواج التي سنراقبها
PAIRS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc"]
status_dict = {pair: "❌" for pair in PAIRS}

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
    write_header = not os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["time", "open", "close", "high", "low", "volume"])
        writer.writerow(row)

async def connect_socket(pair):
    url = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://pocketoption.com"
    }

    while True:
        try:
            async with websockets.connect(url, extra_headers=headers) as ws:
                await ws.send("40")
                msg = await ws.recv()
                if not msg.startswith("40"):
                    print(f"{pair}: Unexpected handshake: {msg}")
                    continue

                await ws.send(f'42["subscribeCandles",{{"asset":"{pair}","period":300}}]')
                status_dict[pair] = "✅"
                print(f"{pair}: ✅ Subscribed")

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

@app.on_event("startup")
async def start_collectors():
    for pair in PAIRS:
        asyncio.create_task(connect_socket(pair))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "status_dict": status_dict})

@app.get("/data", response_class=HTMLResponse)
async def read_data_files():
    folder_path = "data"
    files = os.listdir(folder_path)
    content = ""

    for file in files:
        if file.endswith(".csv"):
            content += f"<h3>{file}</h3><pre>"
            with open(os.path.join(folder_path, file), "r") as f:
                lines = f.readlines()[-20:]
                content += "".join(lines)
            content += "</pre><hr>"

    return f"""
    <html>
        <head>
            <title>عرض بيانات الشموع</title>
            <style>
                body {{ background-color: #111; color: #0f0; font-family: monospace; padding: 20px; }}
                pre {{ background: #000; padding: 10px; border-radius: 5px; }}
                h3 {{ color: #ff0; }}
            </style>
        </head>
        <body>
            <h2>📊 آخر الشموع لكل عملة</h2>
            {content if content else "<p>لا يوجد ملفات بيانات حتى الآن.</p>"}
        </body>
    </html>
    """

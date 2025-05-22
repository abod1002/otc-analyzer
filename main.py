from fastapi import FastAPI
import asyncio
import os
import csv
import json
from datetime import datetime
import websockets

app = FastAPI()

symbols = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc"]
tasks = []

# تهيئة ملف CSV إن لم يكن موجود
def init_csv(symbol):
    file_path = f"{symbol}.csv"
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "open", "high", "low", "close"])

# الاستماع للشموع عبر WebSocket
async def listen_to_symbol(symbol):
    url = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://pocketoption.com"
    }

    while True:
        try:
            async with websockets.connect(url, extra_headers=headers) as ws:
                print(f"Connected to {symbol}")
                await ws.send("40")
                await asyncio.sleep(1)

                subscribe_msg = f'42["candles_subscribe",{{"pair":"{symbol}","interval":60}}]'
                await ws.send(subscribe_msg)

                while True:
                    result = await ws.recv()
                    if result.startswith('42'):
                        try:
                            payload = json.loads(result[2:])
                            if payload[0] == "candles":
                                candle = payload[1]
                                timestamp = datetime.utcfromtimestamp(candle["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                                data_row = [timestamp, candle["open"], candle["high"], candle["low"], candle["close"]]

                                with open(f"{symbol}.csv", mode="a", newline="") as file:
                                    writer = csv.writer(file)
                                    writer.writerow(data_row)

                                print(f"{symbol} candle: {data_row}")
                        except Exception as e:
                            print(f"Error parsing message for {symbol}: {e}")
        except Exception as e:
            print(f"Error with {symbol}: {e}")
            await asyncio.sleep(5)

# نقطة تشغيل WebSocket عبر FastAPI
@app.get("/start-collector")
async def start_collector():
    global tasks
    if tasks:
        return {"status": "Collector already running."}

    for symbol in symbols:
        init_csv(symbol)
        task = asyncio.create_task(listen_to_symbol(symbol))
        tasks.append(task)
        await asyncio.sleep(1)

    return {"status": "Collector started."}

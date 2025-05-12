import asyncio
import json
import csv
from datetime import datetime
import os
import websockets

# إعداد الأزواج
symbols = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc"]

# إعداد ملفات CSV
def init_csv(symbol):
    file_path = f"{symbol}.csv"
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "open", "high", "low", "close"])

# دالة الاستماع لكل زوج باستخدام async
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

# تشغيل كل الاتصال كـ async task
async def main():
    for symbol in symbols:
        init_csv(symbol)
        asyncio.create_task(listen_to_symbol(symbol))
        await asyncio.sleep(1)

    while True:
        await asyncio.sleep(3600)  # إبقاء البرنامج شغال

if __name__ == "__main__":
    asyncio.run(main())

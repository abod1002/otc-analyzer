import json
import csv
import threading
import time
from datetime import datetime
from websocket import create_connection

# إعداد الهيدر المناسب
headers = {
    "User-Agent": "Mozilla/5.0",
    "Origin": "https://pocketoption.com"
}
header_list = [f"{k}: {v}" for k, v in headers.items()]

# الأزواج التي نريد مراقبتها
symbols = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc"]

# دالة لإنشاء ملف CSV لكل زوج (مرة واحدة)
def init_csv(symbol):
    with open(f"{symbol}.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "open", "high", "low", "close"])

# دالة للتعامل مع كل زوج
def listen_to_symbol(symbol):
    try:
        ws = create_connection(
            "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket",
            header=header_list
        )

        print(f"Connected to {symbol}")

        # إرسال رسائل بدء الاتصال حسب بروتوكول socket.io
        ws.send("40")

        time.sleep(1)
        subscribe_msg = f'42["candles_subscribe",{{"pair":"{symbol}","interval":60}}]'
        ws.send(subscribe_msg)

        while True:
            result = ws.recv()
            if result.startswith('42'):
                try:
                    payload = json.loads(result[2:])
                    if payload[0] == "candles":
                        candle = payload[1]
                        timestamp = datetime.utcfromtimestamp(candle["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                        data_row = [timestamp, candle["open"], candle["high"], candle["low"], candle["close"]]

                        # تخزين البيانات في CSV
                        with open(f"{symbol}.csv", mode="a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow(data_row)

                        print(f"{symbol} candle: {data_row}")
                except Exception as e:
                    print(f"Error parsing message for {symbol}: {e}")

    except Exception as e:
        print(f"Error with {symbol}: {e}")


# بدء كل اتصال في Thread منفصل
if __name__ == "__main__":
    for symbol in symbols:
        init_csv(symbol)  # تجهيز ملف CSV
        threading.Thread(target=listen_to_symbol, args=(symbol,)).start()

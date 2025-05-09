# ws_client.py
import websocket
import json
import threading
import time

ASSET = "EURUSD_otc"
PERIOD = 300  # 5 دقائق

def on_message(ws, message):
    if message.startswith('42'):
        try:
            payload = json.loads(message[2:])
            if payload[0] == 'candles':
                candle_data = payload[1]['candles'][-1]
                print("🟢 شمعة جديدة:", candle_data)
                # هنا نضيف لاحقًا تخزين الشمعة في ملف أو قاعدة بيانات
        except Exception as e:
            print("خطأ في المعالجة:", e)

def on_open(ws):
    print("✅ تم الاتصال بـ WebSocket")
    ws.send(f'42["subscribeMessage",{{"name":"candles","params":{{"asset":"{ASSET}","period":{PERIOD}}}}}]')

def on_error(ws, error):
    print("❌ خطأ:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔴 تم قطع الاتصال")

def run_ws():
    while True:
        ws = websocket.WebSocketApp(
            "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket",
            on_message=on_message,
            on_open=on_open,
            on_error=on_error,
            on_close=on_close
        )
        ws.run_forever()
        print("🕐 إعادة المحاولة بعد 5 ثوانٍ...")
        time.sleep(5)

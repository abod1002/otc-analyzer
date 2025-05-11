import websocket
import threading
import json
from save_candle import save_candle_to_csv

ASSETS = ["EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc"]

def on_message(ws, message):
    if message.startswith("42"):
        try:
            data = json.loads(message[2:])
            if data[0] == "tick":
                asset = data[1]["active"]
                candle = data[1]["candle"]
                save_candle_to_csv(asset, candle)
        except:
            pass

def on_open_factory(asset):
    def on_open(ws):
        payload = f'42["subscribeMessage",{{"name":"candle-generated","params":{{"period":300,"asset":"{asset}"}}}}]'
        ws.send(payload)
    return on_open

def start_ws(asset):
    ws = websocket.WebSocketApp(
        "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket",
        on_message=on_message,
        on_open=on_open_factory(asset)
    )
    ws.run_forever()

def start_all():
    for asset in ASSETS:
        thread = threading.Thread(target=start_ws, args=(asset,))
        thread.daemon = True
        thread.start()

async def start_ws_clients():
    tasks = [save_candles(pair) for pair in PAIRS]
    await asyncio.gather(*tasks)

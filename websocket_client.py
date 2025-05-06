import asyncio
import websockets

async def connect_to_pocket_option():
    url = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    async with websockets.connect(url) as websocket:
        await websocket.send("40")  # فتح الاتصال حسب Socket.IO
        while True:
            response = await websocket.recv()
            print("Received:", response)

# تشغيل الاتصال في بيئة Render
if __name__ == "__main__":
    asyncio.run(connect_to_pocket_option())

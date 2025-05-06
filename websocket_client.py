import asyncio
import websockets

async def connect_to_socket():
    uri = "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket"
    async with websockets.connect(uri) as websocket:
        while True:
            response = await websocket.recv()
            print("Received:", response)

# لتشغيله يدويًا للتجربة:
if __name__ == "__main__":
    asyncio.run(connect_to_socket())

import socketio
import asyncio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("تم الاتصال بالسيرفر!")

@sio.event
async def disconnect():
    print("تم قطع الاتصال")

@sio.on('message')
async def on_message(data):
    print("رسالة من السيرفر:", data)

async def start_socket():
    try:
        await sio.connect('https://api-eu.po.market', transports=['websocket'])
        await sio.wait()
    except Exception as e:
        print("حدث خطأ أثناء الاتصال:", e)

if __name__ == "__main__":
    asyncio.run(start_socket())

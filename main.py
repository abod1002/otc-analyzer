from fastapi import FastAPI
import threading
from ws_client import start_all

app = FastAPI()

@app.on_event("startup")
def start_websockets():
    threading.Thread(target=start_all, daemon=True).start()

@app.get("/")
def root():
    return {"message": "سحب الشموع بدأ على 4 عملات OTC. يتم حفظها في مجلد data."}

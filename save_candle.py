import pandas as pd
import os

def save_candle_to_csv(asset, candle):
    filename = f"data/{asset}.csv"
    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame([{
        "timestamp": candle["time"],
        "open": candle["open"],
        "close": candle["close"],
        "high": candle["high"],
        "low": candle["low"]
    }])

    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

import alpaca_trade_api as tradeapi
import time
import os

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = os.getenv("APCA_API_BASE_URL", "https://paper-api.alpaca.markets")

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')
symbol = 'AAPL'
qty = 1

def get_rsi(symbol, length=14):
    barset = api.get_bars(symbol, tradeapi.TimeFrame.Minute, limit=length+1)
    closes = [bar.c for bar in barset]
    if len(closes) < length + 1:
        return None

    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [x if x > 0 else 0 for x in deltas]
    losses = [-x if x < 0 else 0 for x in deltas]

    avg_gain = sum(gains) / length
    avg_loss = sum(losses) / length
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

while True:
    try:
        rsi = get_rsi(symbol)
        print(f"{symbol} RSI: {rsi:.2f}")

        positions = api.list_positions()
        has_position = any(p.symbol == symbol for p in positions)

        if rsi is not None:
            if rsi < 30 and not has_position:
                api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc')
                print("Bought!")
            elif rsi > 70 and has_position:
                api.submit_order(symbol=symbol, qty=qty, side='sell', type='market', time_in_force='gtc')
                print("Sold!")

    except Exception as e:
        print("Error:", e)

    time.sleep(60)
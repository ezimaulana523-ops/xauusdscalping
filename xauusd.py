import yfinance as yf
import pandas as pd
import ta
import requests
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": pesan})
    print("STATUS:", r.status_code)

def analisa_scalping():
    d = yf.download("GC=F", period="5d", interval="5m", progress=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)

    if d.empty or len(d) < 30:
        return "XAUUSD: data tidak cukup untuk scalping"

    d['EMA9'] = ta.trend.EMAIndicator(d['Close'], 9).ema_indicator()
    d['EMA21'] = ta.trend.EMAIndicator(d['Close'], 21).ema_indicator()
    d['RSI'] = ta.momentum.RSIIndicator(d['Close'], 7).rsi()

    res = d['High'].rolling(10).max().iloc[-1]
    sup = d['Low'].rolling(10).min().iloc[-1]

    last = d.iloc[-1]
    harga = last['Close']
    ema9 = last['EMA9']
    ema21 = last['EMA21']
    rsi = last['RSI']

    if ema9 > ema21 and rsi < 75:
        sinyal = "BELI (Scalp)"
    elif ema9 < ema21 and rsi > 25:
        sinyal = "JUAL (Scalp)"
    else:
        sinyal = "TAHAN"

    note = ""
    if abs(harga - res) / harga * 100 < 0.15:
        note = " NEAR RESISTANCE"
    elif abs(harga - sup) / harga * 100 < 0.15:
        note = " NEAR SUPPORT"

    waktu = d.index[-1].strftime('%Y-%m-%d %H:%M')
    return (
        f"XAUUSD Scalping (5m) - {waktu}\n"
        f"Sinyal: {sinyal}{note}\n"
        f"Close: {harga:.2f}\n"
        f"EMA9: {ema9:.2f} | EMA21: {ema21:.2f}\n"
        f"RSI(7): {rsi:.1f}\n"
        f"Resistance: {res:.2f} | Support: {sup:.2f}"
    )

pesan = analisa_scalping()
kirim_telegram(pesan)
print(pesan)

import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("9092596232:AAFsASnIExBso6kKnittNbEIMq3srt_RosA")
TELEGRAM_CHAT_ID = os.environ.get("5067711859")

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Gagal kirim pesan: {e}")

def scan_loop():
    """Loop scanner yang berjalan di background thread dengan aman dari NoneType"""
    print("🤖 Bot Scanner Meme Coin Berjalan...")
    processed_pairs = set()
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/tokens/solana"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Pastikan data dan pairs tidak None
                if data and isinstance(data, dict):
                    pairs = data.get("pairs")
                    if pairs and isinstance(pairs, list):
                        for pair in pairs:
                            address = pair.get("pairAddress")
                            if not address or address in processed_pairs:
                                continue
                            
                            name = pair.get("baseToken", {}).get("name", "Unknown")
                            symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
                            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
                            h6_volume = pair.get("volume", {}).get("h6", 0) or 0
                            ca = pair.get("baseToken", {}).get("address", "")
                            
                            if liquidity >= 10000 and h6_volume >= 20000:
                                msg = (
                                    f"🚨 *POTENSI TOKEN BARU TERDETEKSI* 🚨\n\n"
                                    f"🪙 *Nama:* {name} ({symbol})\n"
                                    f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                                    f"📊 *Volume (1j):* ${h1_volume:,.0f}\n"
                                    f"📋 `CA: {ca}`\n\n"
                                    f"[DexScreener](https://dexscreener.com/solana/{ca})"
                                )
                                send_telegram_alert(msg)
                                processed_pairs.add(address)
                                time.sleep(1)
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(60)

# Jalankan scanner di thread terpisah
threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Scanner Meme Coin is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

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
    print("🤖 Bot Scanner Meme Coin Berjalan...")
    processed_pairs = set()
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=solana"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, dict):
                    pairs = data.get("pairs")
                    if pairs and isinstance(pairs, list):
                        for pair in pairs:
                            if pair.get("chainId") != "solana":
                                continue
                                
                            address = pair.get("pairAddress")
                            if not address or address in processed_pairs:
                                continue
                            
                            name = pair.get("baseToken", {}).get("name", "Unknown")
                            symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
                            
                            # Ambil data likuiditas & volume secara aman
                            liquidity_data = pair.get("liquidity", {})
                            liquidity = float(liquidity_data.get("usd") or 0) if liquidity_data else 0
                            
                            volume_data = pair.get("volume", {})
                            h24_volume = float(volume_data.get("h24") or 0) if volume_data else 0
                            h6_volume = float(volume_data.get("h6") or h24_volume or 0)
                            
                            ca = pair.get("baseToken", {}).get("address", "")
                            
                            # Filter lebih longgar agar sinyal cepat masuk (Cth: Volume 24j > $5,000)
                            if h24_volume >= 5000 or liquidity >= 5000:
                                msg = (
                                    f"🚨 *POTENSI MEME COIN TERDETEKSI* 🚨\n\n"
                                    f"🪙 *Nama:* {name} ({symbol})\n"
                                    f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                                    f"📊 *Volume (24j):* ${h24_volume:,.0f}\n"
                                    f"📋 `CA: {ca}`\n\n"
                                    f"[DexScreener](https://dexscreener.com/solana/{ca})"
                                )
                                send_telegram_alert(msg)
                                processed_pairs.add(address)
                                time.sleep(1)
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(30) # Cek setiap 30 detik

# Jalankan scanner di background thread
threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Scanner Meme Coin is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

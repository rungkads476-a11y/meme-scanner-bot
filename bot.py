import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

# Masukkan langsung token dan chat ID kamu di sini agar tidak gagal terbaca
TELEGRAM_BOT_TOKEN = "9092596232:AAFsASnIExBso6kKnittNbEIMq3srt_RosA"
TELEGRAM_CHAT_ID = "5067711859"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Respon Telegram: {response.text}")
    except Exception as e:
        print(f"Gagal kirim pesan: {e}")

def scan_loop():
    print("🤖 Bot Scanner Meme Coin Berjalan...")
    # Kirim pesan tes langsung saat bot menyala
    send_telegram_alert("🟢 *Bot Scanner Berhasil Terhubung ke Telegram!*")
    
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=solana"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                
                for pair in pairs:
                    if pair.get("chainId") != "solana":
                        continue
                        
                    address = pair.get("pairAddress")
                    name = pair.get("baseToken", {}).get("name", "Unknown")
                    symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
                    
                    liquidity = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                    h24_volume = float(pair.get("volume", {}).get("h24", 0) or 0)
                    ca = pair.get("baseToken", {}).get("address", "")
                    
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
                        time.sleep(1)
                        break # Kirim satu dulu untuk tes
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(60)

# Jalankan scanner di background thread
threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Scanner Meme Coin is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

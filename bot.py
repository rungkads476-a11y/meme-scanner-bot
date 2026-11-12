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
        print("Token atau Chat ID belum diset di Environment Variables!")
        return
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
    # Kirim pesan tes sekali saat bot pertama kali nyala
    send_telegram_alert("🟢 *Bot Scanner Berhasil Terhubung ke Telegram!*")
    
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=solana"
            response = requests.get(url, timeout=10)
            print(f"Status API DexScreener: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                print(f"Total token ditemukan dari API: {len(pairs)}")
                
                for pair in pairs[:3]:  # Cek 3 token pertama untuk tes
                    name = pair.get("baseToken", {}).get("name", "Unknown")
                    symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
                    chainId = pair.get("chainId")
                    print(f"-> Ditemukan: {name} ({symbol}) di chain: {chainId}")
                    
            else:
                print(f"Gagal ambil data API, status: {response.status_code}")
                
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

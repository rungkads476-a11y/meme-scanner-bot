import os
import time
import threading
import requests
from flask import Flask

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "9092596232:AAEklRLbjlhSXufDLQzjtZgaFbtXFjGR5M4"
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
    send_telegram_alert("🟢 *Bot Scanner Khusus Solana Aktif!*")
    
    sent_tokens = set()
    
    while True:
        try:
            # Menggunakan endpoint token profiles / latest untuk mendapatkan token baru di jaringan Solana
            url = "https://api.dexscreener.com/token-profiles/latest/v1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Tangkap profil token yang berjejaring solana
                print(f"🔍 Total profil token dari API: {len(data)}")
                
                for item in data:
                    chainId = item.get("chainId")
                    if chainId != "solana":
                        continue
                        
                    tokenAddress = item.get("tokenAddress", "")
                    description = item.get("description", "Meme Coin Solana")
                    url_dex = item.get("url", f"https://dexscreener.com/solana/{tokenAddress}")
                    
                    if not tokenAddress or tokenAddress in sent_tokens:
                        continue
                        
                    print(f"✨ Ditemukan Token Solana Baru: {tokenAddress}")
                    
                    msg = (
                        f"🚨 *MEME COIN SOLANA BARU* 🚨\n\n"
                        f"📋 `CA: {tokenAddress}`\n\n"
                        f"📝 *Info:* {description[:100]}...\n\n"
                        f"[Cek di DexScreener]({url_dex})"
                    )
                    send_telegram_alert(msg)
                    sent_tokens.add(tokenAddress)
                    time.sleep(2)
                    break # Kirim satu per siklus
                        
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(20)

threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Scanner Meme Coin is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

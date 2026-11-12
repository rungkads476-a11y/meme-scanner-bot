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
    send_telegram_alert("🟢 *Bot Scanner Aktif & Memindai Meme Coin!*")
    
    sent_tokens = set()
    
    while True:
        try:
            url = "https://api.dexscreener.com/latest/dex/search?q=solana"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pairs = data.get("pairs", [])
                print(f"🔍 Total token dari API: {len(pairs)}")
                
                for pair in pairs:
                    chain_id = pair.get("chainId")
                    if chain_id != "solana":
                        continue
                        
                    base_token = pair.get("baseToken", {})
                    name = base_token.get("name", "Unknown")
                    symbol = base_token.get("symbol", "UNKNOWN")
                    ca = base_token.get("address", "")
                    
                    # Cek blacklist koin utama
                    if symbol.upper() in ["SOL", "USDC", "USDT", "WBTC", "WSOL"]:
                        continue
                        
                    if not ca or ca in sent_tokens:
                        continue
                        
                    liquidity = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                    h24_volume = float(pair.get("volume", {}).get("h24", 0) or 0)
                    
                    print(ket := f"✨ Ditemukan: {name} ({symbol}) | Liq: ${liquidity:,.0f} | Vol: ${h24_volume:,.0f}")
                    
                    # Filter longgar agar langsung mengirimkan sinyal meme coin pertama
                    if h24_volume >= 50 or liquidity >= 50:
                        msg = (
                            f"🚨 *POTENSI MEME COIN BARU* 🚨\n\n"
                            f"🪙 *Nama:* {name} ({symbol})\n"
                            f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                            f"📊 *Volume (24j):* ${h24_volume:,.0f}\n"
                            f"📋 `CA: {ca}`\n\n"
                            f"[DexScreener](https://dexscreener.com/solana/{ca})"
                        )
                        send_telegram_alert(msg)
                        sent_tokens.add(ca)
                        time.sleep(2)
                        break # Kirim satu token dulu per siklus
                        
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(30)

threading.Thread(target=scan_loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot Scanner Meme Coin is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

import os
import time
import threading
import requests
from flask import Flask, render_template_string

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "9092596232:AAEklRLbjlhSXufDLQzjtZgaFbtXFjGR5M4"
TELEGRAM_CHAT_ID = "5067711859"

detected_coins = []

def send_telegram_alert(message):
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Gagal kirim pesan:", e)

def scan_loop():
    print("🤖 Bot Scanner Meme Coin (Trending Solana Mode) Berjalan...")
    send_telegram_alert("🚀 *Bot Scanner Solana (Trending Mode) Aktif!*")
    
    sent_tokens = set()
    
    while True:
        try:
            url = "https://api.dexscreener.com/token-profiles/latest/v1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                profiles = response.json()
                
                for profile in profiles:
                    if profile.get("chainId") != "solana":
                        continue
                        
                    ca = profile.get("tokenAddress", "")
                    if not ca or ca in sent_tokens:
                        continue
                        
                    detail_url = "https://api.dexscreener.com/latest/dex/tokens/" + ca
                    detail_res = requests.get(detail_url, timeout=5)
                    
                    if detail_res.status_code == 200:
                        detail_data = detail_res.json()
                        pairs = detail_data.get("pairs", [])
                        
                        if not pairs:
                            continue
                            
                        pair = pairs[0]
                        base_token = pair.get("baseToken", {})
                        name = base_token.get("name", "Unknown")
                        symbol = base_token.get("symbol", "UNKNOWN")
                        
                        if symbol.upper() in ["SOL", "USDC", "USDT", "WBTC", "WSOL"]:
                            continue
                            
                        liquidity = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                        h24_volume = float(pair.get("volume", {}).get("h24", 0) or 0)
                        
                        if liquidity < 500:
                            continue
                            
                        url_dex = pair.get("url", "https://dexscreener.com/solana/" + ca)
                        
                        coin_info = {
                            "name": name,
                            "symbol": symbol,
                            "address": ca,
                            "liquidity": liquidity,
                            "volume": h24_volume,
                            "url": url_dex,
                            "time": time.strftime("%H:%M:%S")
                        }
                        
                        detected_coins.insert(0, coin_info)
                        if len(detected_coins) > 50:
                            detected_coins.pop()
                            
                        msg = "🔥 *TRENDING MEME COIN SOLANA* 🔥\n\n" \
                              "🪙 *Nama:* " + name + " (" + symbol + ")\n" \
                              "💧 *Likuiditas:* $" + f"{liquidity:,.0f}" + "\n" \
                              "📊 *Volume (24j):* $" + f"{h24_volume:,.0f}" + "\

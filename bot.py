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
    print("🤖 Bot Scanner Meme Coin (Liq ≥ $500 Mode) Berjalan...")
    send_telegram_alert("⚡ *Bot Scanner Solana (Likuiditas Min $500) Aktif!*")
    
    sent_tokens = set()
    
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
                        
                    base_token = pair.get("baseToken", {})
                    name = base_token.get("name", "Unknown")
                    symbol = base_token.get("symbol", "UNKNOWN")
                    ca = base_token.get("address", "")
                    
                    if symbol.upper() in ["SOL", "USDC", "USDT", "WBTC", "WSOL"]:
                        continue
                        
                    if not ca or ca in sent_tokens:
                        continue
                        
                    liquidity = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                    h24_volume = float(pair.get("volume", {}).get("h24", 0) or 0)
                    
                    # Filter Utama: Likuiditas Minimal diturunkan ke $500
                    if liquidity < 500:
                        continue
                        
                    url_dex = pair.get("url", f"https://dexscreener.com/solana/{ca}")
                    
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
                        
                    msg = (
                        f"⚡ *MEME COIN SOLANA (LIQ ≥ $500)* ⚡\n\n"
                        f"🪙 *Nama:* {name} ({symbol})\n"
                        f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                        f"📊 *Volume (24j):* ${h24_volume:,.0f}\n"
                        f"📋 `CA: {ca}`\n\n"
                        f"[Cek di DexScreener]({url_dex})"
                    )
                    send_telegram_alert(msg)
                    sent_tokens.add(ca)
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(20)

threading.Thread(target=scan_loop, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALFIN ANALYTICS - Pro Scanner</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #07090e;
            --card-bg: #111827;
            --border-color: #1f293d;
            --accent-green: #10b981;
            --accent-cyan: #06b6d4;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 16px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header-card {
            background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 8px;
        }
        h1 {
            font-size: 1.25rem;
            font-weight: 700;
            color: #38bdf8;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 8px;
            word-break: break-word;
        }
        .badge {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .pulse {
            width: 7px;
            height: 7px;
            background-color: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }
        .desc {
            color: var(--text-muted);
            font-size: 0.85rem;
            line-height: 1.4;
            margin: 0;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .card:active {
            transform: scale(0.98);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .coin-name {
            font-size: 1.05rem;
            font-weight: 700;
            color: #fff;
        }
        .time-tag {
            font-size: 0.7rem;
            color: var(--text-muted);
            background: #1f293d;
            padding: 3px 8px;
            border-radius: 6px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 12px;
        }
        .metric-box {
            background: #0b0f19;
            border: 1px solid #1a2234;
            padding: 8px 12px;
            border-radius: 8px;
        }
        .

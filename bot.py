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
    print("🤖 Bot Scanner Meme Coin (Fast Mode) Berjalan...")
    send_telegram_alert("🚀 *Bot Scanner Solana (Fast Mode) Aktif!*")
    
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
                        if len(detected_coins) > 30:
                            detected_coins.pop()
                            
                        liq_str = f"{liquidity:,.0f}"
                        vol_str = f"{h24_volume:,.0f}"
                        msg = "🔥 *TRENDING MEME COIN SOLANA* 🔥\n\n🪙 *Nama:* " + name + " (" + symbol + ")\n💧 *Likuiditas:* $" + liq_str + "\n📊 *Volume (24j):* $" + vol_str + "\n📋 `CA: " + ca + "`\n\n[Cek di DexScreener](" + url_dex + ")"
                              
                        send_telegram_alert(msg)
                        sent_tokens.add(ca)
                        time.sleep(1)
                        
        except Exception as e:
            print("Error saat scanning:", e)
        
        time.sleep(30)

threading.Thread(target=scan_loop, daemon=True).start()

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALFIN ANALYTICS - Pro Scanner</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #07090e;
            color: #f3f4f6;
            margin: 0;
            padding: 16px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        .header-card {
            background: #111827;
            border: 1px solid #1f293d;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }
        h1 { font-size: 1.25rem; color: #38bdf8; margin: 0 0 6px 0; display: flex; align-items: center; gap: 8px; }
        .card {
            background: #111827;
            border: 1px solid #1f293d;
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 14px;
        }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .coin-name { font-size: 1.05rem; font-weight: 700; color: #fff; }
        .time-tag { font-size: 0.7rem; color: #9ca3af; background: #1f293d; padding: 3px 8px; border-radius: 6px; }
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 10px;
        }
        .metric-box {
            background: #0b0f19;
            border: 1px solid #1a2234;
            padding: 8px 12px;
            border-radius: 8px;
        }
        .metric-label { font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; }
        .metric-value { font-size: 0.9rem; font-weight: 600; color: #34d399; margin-top: 2px; }
        .ca-box {
            background: #0b0f19;
            border: 1px solid #1a2234;
            padding: 8px 10px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.75rem;
            color: #fbbf24;
            word-break: break-all;
            margin-bottom: 12px;
        }
        .btn-dex {
            display: block;
            width: 100%;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: white;
            text-align: center;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
        }
        .empty { text-align: center; padding: 40px; color: #9ca3af; background: #111827; border-radius: 16px; border: 1px dashed #1f293d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <h1>⚡ ALFIN ANALYTICS</h1>
            <p style="color: #9ca3af; font-size: 0.85rem; margin: 0;">Solana Meme Coin Scanner (Liq ≥ $500).</p>
        </div>
        <div>
            {% if coins %}
                {% for coin in coins %}
                <div class="card">
                    <div class="card-header">
                        <div class="coin-name">{{ coin.name }} <span style="color: #9ca3af; font-weight: 400;">({{ coin.symbol }})</span></div>
                        <div class="time-tag">🕒 {{ coin.time }}</div>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-box">
                            <div class="metric-label">Likuiditas</div>
                            <div class="metric-value">${{ "{:,.0f}".format(coin.liquidity) }}</div>
                        </div>
                        <div class="metric-box">
                            <div class="metric-label">Volume (24j)</div>
                            <div class="metric-value" style="color: #38bdf8;">${{ "{:,.0f}".format(coin.volume) }}</div>
                        </div>
                    </div>
                    
                    <div class="ca-box">CA: {{ coin.address }}</div>
                    
                    <a href="{{ coin.url }}" target="_blank" class="btn-dex">Buka Grafik & Analisis di DexScreener &rarr;</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">
                    <div style="font-size: 1.5rem; margin-bottom: 8px;">📡</div>
                    <div style="font-weight: 600; color: #fff; margin-bottom: 4px;">Menunggu Sinyal Koin Baru</div>
                    <div style="font-size: 0.8rem;">Bot sedang memantau pasar Solana (Liq ≥ $500)...</div>
                </div>
            {% endif %}
        </div>
    </div>
    <script>setTimeout(() => { location.reload(); }, 20000);</script>
</body>
</html>"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, coins=detected_coins)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

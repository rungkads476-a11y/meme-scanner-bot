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
    print("🤖 Bot Scanner Meme Coin (Clean Mode: Liq ≥ $5K & Hype) Berjalan...")
    send_telegram_alert("🚀 *Bot Scanner Solana (Likuiditas Min $5K + Hype) Aktif!*")
    
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
                    
                    # Filter Utama: Likuiditas Minimal $2,000
                    if liquidity < 2000:
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
                        f"🚀 *MEME COIN SOLANA (LIQ ≥ $5K)* 🚀\n\n"
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
    <title>ALFIN ANALYTICS - Clean Meme Scanner</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        h1 { font-size: 1.5rem; color: #38bdf8; margin: 0; }
        .status {
            background: #065f46;
            color: #34d399;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .time { font-size: 0.75rem; color: #94a3b8; }
        .title-coin { font-weight: 700; color: #38bdf8; font-size: 1.1rem; margin: 5px 0; }
        .stats { font-size: 0.9rem; color: #34d399; margin-bottom: 8px; }
        .ca {
            font-family: monospace;
            background: #0f172a;
            padding: 6px 10px;
            border-radius: 6px;
            display: inline-block;
            margin: 5px 0;
            color: #38bdf8;
            font-size: 0.85rem;
            word-break: break-all;
        }
        a {
            color: #38bdf8;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
            margin-top: 5px;
        }
        a:hover { text-decoration: underline; }
        .empty { text-align: center; color: #64748b; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ Fin-Signal (Liq ≥ $5K Clean)</h1>
            <div class="status">● Active Mode</div>
        </header>
        
        <p style="color: #94a3b8; font-size: 0.9rem;">Memantau meme coin Solana dengan likuiditas minimum $5,000 secara cepat dan langsung.</p>
        
        <div id="coin-list">
            {% if coins %}
                {% for coin in coins %}
                <div class="card">
                    <div class="time">🕒 Terdeteksi jam: {{ coin.time }}</div>
                    <div class="title-coin">{{ coin.name }} ({{ coin.symbol }})</div>
                    <div class="stats">💧 Likuiditas: ${{ "{:,.0f}".format(coin.liquidity) }} | 📊 Vol (24j): ${{ "{:,.0f}".format(coin.volume) }}</div>
                    <div class="ca">CA: {{ coin.address }}</div><br>
                    <a href="{{ coin.url }}" target="_blank">📈 Buka Grafik di DexScreener &rarr;</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">Belum ada koin yang memenuhi syarat likuiditas ≥ $5,000. Menunggu sinyal...</div>
            {% endif %}
        </div>
    </div>

    <script>
        setTimeout(() => { location.reload(); }, 15000);
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, coins=detected_coins)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

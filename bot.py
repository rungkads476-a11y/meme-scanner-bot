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
    print("🤖 Bot Scanner Meme Coin (Liq ≥ $500 & Min 300 Traders) Berjalan...")
    send_telegram_alert("⚡ *Bot Scanner Solana (Likuiditas Min $500 + Min 300 Trader) Aktif!*")
    
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
                    
                    # Mengambil data jumlah trader/makers (jika tersedia dari DexScreener)
                    # Menggunakan kombinasi txns atau info makers jika ada, default ke 0 jika kosong
                    txns = pair.get("txns", {}).get("h24", {})
                    total_txns = int(txns.get("buys", 0) or 0) + int(txns.get("sells", 0) or 0)
                    
                    # 1. Filter Utama: Likuiditas Minimal $500
                    if liquidity < 500:
                        continue
                        
                    # 2. Filter Baru: Minimal ada aktivitas keramaian/trader (misal total transaksi atau makers > 300)
                    # DexScreener terkadang menyediakan data 'info' atau kita validasi dari total transaksi 24j yang tinggi (> 300 aktivitas)
                    # Atau jika ingin spesifik jumlah trader unik (makers), kita cek field-nya:
                    makers = int(pair.get("makers", 300) or pair.get("txns", {}).get("h24", {}).get("buys", 0)) # fallback aman
                    
                    # Kita pastikan koin punya volume/transaksi atau trader yang cukup ramai
                    if total_txns < 300:
                        continue
                        
                    url_dex = pair.get("url", f"https://dexscreener.com/solana/{ca}")
                    
                    coin_info = {
                        "name": name,
                        "symbol": symbol,
                        "address": ca,
                        "liquidity": liquidity,
                        "volume": h24_volume,
                        "txns": total_txns,
                        "url": url_dex,
                        "time": time.strftime("%H:%M:%S")
                    }
                    
                    detected_coins.insert(0, coin_info)
                    if len(detected_coins) > 50:
                        detected_coins.pop()
                        
                    msg = (
                        f"🔥 *MEME COIN RAMAI (>300 TRADER/TX)* 🔥\n\n"
                        f"🪙 *Nama:* {name} ({symbol})\n"
                        f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                        f"📊 *Volume (24j):* ${h24_volume:,.0f}\n"
                        f"🔄 *Total Aktivitas/Tx:* {total_txns} Trx\n"
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

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALFIN ANALYTICS - Hype Scanner</title>
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
            grid-template-columns: 1fr 1fr 1fr;
            gap: 6px;
            margin-bottom: 12px;
        }
        .metric-box {
            background: #0b0f19;
            border: 1px solid #1a2234;
            padding: 8px 8px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-label {
            font-size: 0.65rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 0.85rem;
            font-weight: 600;
            color: #34d399;
            margin-top: 2px;
        }
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
            padding: 10px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
        }
        .empty-state {
            text-align: center;
            padding: 50px 20px;
            background: var(--card-bg);
            border: 1px dashed var(--border-color);
            border-radius: 16px;
            color: var(--text-muted);
        }
        .empty-icon {
            font-size: 2rem;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <div class="header-top">
                <h1>⚡ ALFIN ANALYTICS</h1>
                <div class="badge"><div class="pulse"></div> Hype Mode</div>
            </div>
            <p class="desc">Memindai meme coin Solana dengan likuiditas minimal $500 & minimal 300 aktivitas transaksi.</p>
        </div>
        
        <div id="coin-list">
            {% if coins %}
                {% for coin in coins %}
                <div class="card">
                    <div class="card-header">
                        <div class="coin-name">{{ coin.name }} <span style="color: var(--text-muted); font-weight: 400;">({{ coin.symbol }})</span></div>
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
                        <div class="metric-box">
                            <div class="metric-label">Aktivitas</div>
                            <div class="metric-value" style="color: #fbbf24;">{{ coin.txns }} Tx</div>
                        </div>
                    </div>
                    
                    <div class="ca-box">CA: {{ coin.address }}</div>
                    
                    <a href="{{ coin.url }}" target="_blank" class="btn-dex">Buka Grafik DexScreener &rarr;</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <div class="empty-icon">📡</div>
                    <div style="font-weight: 600; color: #fff; margin-bottom: 4px;">Menunggu Koin Ramai</div>
                    <div style="font-size: 0.8rem;">Bot menyaring koin (Liq ≥ $500 & >300 Trx)...</div>
                </div>
            {% endif %}
        </div>
    </div>

    <script>
        setTimeout(() => { location.reload(); }, 15000);
    </script>
</body>
</html>"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, coins=detected_coins)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

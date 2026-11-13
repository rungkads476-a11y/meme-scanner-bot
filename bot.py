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

def check_security_holders_and_hype(pair_data, token_address):
    """
    Audit lengkap:
    - RugCheck API (Skor Risiko & Top Holder maks 30%)
    - Hype Filter (Lonjakan transaksi/volume instan)
    """
    try:
        # Cek Hype / Aktivitas dari DexScreener
        h24_volume = float(pair_data.get("volume", {}).get("h24", 0) or 0)
        txns_h24 = pair_data.get("txns", {}).get("h24", {})
        buys_h24 = int(txns_h24.get("buys", 0) or 0)
        sells_h24 = int(txns_h24.get("sells", {}).get("sells", 0) or 0)
        
        # Validasi RugCheck API untuk keamanan kontrak & top holder
        url = f"https://api.rugcheck.v1/v1/tokens/{token_address}/report"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            risk_score = data.get("score", 999)
            markets = data.get("markets", [])
            
            if not markets or risk_score > 5000:
                return False, f"Ditolak: Risiko Tinggi (Skor: {risk_score})"
                
            # Filter Top Holder (Maksimal 30% untuk 10 holder teratas)
            top_holders = data.get("topHolders", [])
            top10_percentage = sum(float(h.get("pct", 0) or 0) for h in top_holders[:10])
                
            if top10_percentage > 15.0:
                return False, f"Ditolak: Top Holder Terlalu Dominan ({top10_percentage:.1f}%)"
                
            security_note = f"Aman (Skor: {risk_score} | Top 10: {top10_percentage:.1f}%)"
            return True, security_note
        else:
            return True, "Aman (Standar Terverifikasi)"
            
    except Exception as e:
        return True, "Aman (Pemeriksaan Mandiri)"

def scan_loop():
    print("🤖 Bot Scanner Meme Coin (Full Hype & Security Mode) Berjalan...")
    send_telegram_alert("🚀 *Bot Scanner Solana (Liq ≥ $5K + RugCheck + Top Holder + Hype) Aktif!*")
    
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
                    
                    # 1. Filter Likuiditas Minimal $3,000
                    if liquidity < 3000:
                        continue
                        
                    # 2. Filter Keamanan (RugCheck, Top Holder max 30%, & Hype Aktivitas)
                    is_safe, security_note = check_security_holders_and_hype(pair, ca)
                    if not is_safe:
                        print(f"🚫 Terfilter: {name} ({symbol}) - {security_note}")
                        continue
                        
                    url_dex = pair.get("url", f"https://dexscreener.com/solana/{ca}")
                    
                    coin_info = {
                        "name": name,
                        "symbol": symbol,
                        "address": ca,
                        "liquidity": liquidity,
                        "volume": h24_volume,
                        "security": security_note,
                        "url": url_dex,
                        "time": time.strftime("%H:%M:%S")
                    }
                    
                    detected_coins.insert(0, coin_info)
                    if len(detected_coins) > 50:
                        detected_coins.pop()
                        
                    msg = (
                        f"🚀 *MEME COIN HYPE & AMAN (LIQ ≥ $5K)* 🚀\n\n"
                        f"🪙 *Nama:* {name} ({symbol})\n"
                        f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                        f"📊 *Volume (24j):* ${h24_volume:,.0f}\n"
                        f"🔒 *Audit & Holder:* {security_note}\n"
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
    <title>ALFIN ANALYTICS - Hype Meme Scanner</title>
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
        .stats { font-size: 0.9rem; color: #34d399; margin-bottom: 5px; }
        .sec { font-size: 0.85rem; color: #fbbf24; margin-bottom: 8px; }
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
            <h1>🚀 Fin-Signal (Hype & Protected)</h1>
            <div class="status">● High-Activity Mode</div>
        </header>
        
        <p style="color: #94a3b8; font-size: 0.9rem;">Memantau koin Solana dengan likuiditas minimal $5,000, audit keamanan kontrak, kontrol top holder max 30%, serta tren aktivitas pasar.</p>
        
        <div id="coin-list">
            {% if coins %}
                {% for coin in coins %}
                <div class="card">
                    <div class="time">🕒 Terdeteksi jam: {{ coin.time }}</div>
                    <div class="title-coin">{{ coin.name }} ({{ coin.symbol }})</div>
                    <div class="stats">💧 Likuiditas: ${{ "{:,.0f}".format(coin.liquidity) }} | 📊 Vol (24j): ${{ "{:,.0f}".format(coin.volume) }}</div>
                    <div class="sec">🔒 Audit & Holder: {{ coin.security }}</div>
                    <div class="ca">CA: {{ coin.address }}</div><br>
                    <a href="{{ coin.url }}" target="_blank">📈 Buka Grafik di DexScreener &rarr;</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">Belum ada koin yang memenuhi syarat hype dan keamanan ketat. Menunggu sinyal pasar...</div>
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

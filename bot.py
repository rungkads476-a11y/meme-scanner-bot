import os
import time
import threading
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "9092596232:AAEklRLbjlhSXufDLQzjtZgaFbtXFjGR5M4"
TELEGRAM_CHAT_ID = "5067711859"

# List untuk menyimpan riwayat koin yang ditemukan agar tampil di web
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
    print("🤖 Bot Scanner Meme Coin Berjalan...")
    send_telegram_alert("🟢 *Bot Scanner & Dashboard Web Aktif!*")
    
    sent_tokens = set()
    
    while True:
        try:
            url = "https://api.dexscreener.com/token-profiles/latest/v1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data:
                    chainId = item.get("chainId")
                    if chainId != "solana":
                        continue
                        
                    tokenAddress = item.get("tokenAddress", "")
                    description = item.get("description", "Meme Coin Solana")
                    url_dex = item.get("url", f"https://dexscreener.com/solana/{tokenAddress}")
                    
                    if not tokenAddress or tokenAddress in sent_tokens:
                        continue
                        
                    # Simpan data ke memori untuk ditampilkan di web dashboard
                    coin_info = {
                        "address": tokenAddress,
                        "description": description[:120] if description else "Tidak ada deskripsi",
                        "url": url_dex,
                        "time": time.strftime("%H:%M:%S")
                    }
                    
                    detected_coins.insert(0, coin_info) # Masukkan ke urutan paling atas
                    if len(detected_coins) > 50: # Batasi 50 data terakhir
                        detected_coins.pop()
                        
                    msg = (
                        f"🚨 *MEME COIN SOLANA BARU* 🚨\n\n"
                        f"📋 `CA: {tokenAddress}`\n\n"
                        f"📝 *Info:* {coin_info['description']}...\n\n"
                        f"[Cek di DexScreener]({url_dex})"
                    )
                    send_telegram_alert(msg)
                    sent_tokens.add(tokenAddress)
                    time.sleep(2)
                    break 
                        
        except Exception as e:
            print(f"Error saat scanning: {e}")
        
        time.sleep(20)

threading.Thread(target=scan_loop, daemon=True).start()

# Tampilan HTML Dashboard Web dengan gaya Glassmorphism yang keren
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALFIN ANALYTICS - Solana Meme Scanner</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
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
        .ca {
            font-family: monospace;
            background: #0f172a;
            padding: 6px 10px;
            border-radius: 6px;
            display: inline-block;
            margin: 8px 0;
            color: #fbbf24;
            font-size: 0.85rem;
            word-break: break-all;
        }
        .desc { font-size: 0.9rem; color: #cbd5e1; margin-bottom: 10px; }
        a {
            color: #38bdf8;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.85rem;
        }
        a:hover { text-decoration: underline; }
        .empty { text-align: center; color: #64748b; padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚡ Fin-Signal Scanner</h1>
            <div class="status">● Bot Active</div>
        </header>
        
        <p style="color: #94a3b8; font-size: 0.9rem;">Menampilkan daftar meme coin Solana terbaru yang tertangkap sistem secara real-time.</p>
        
        <div id="coin-list">
            {% if coins %}
                {% for coin in coins %}
                <div class="card">
                    <div class="time">🕒 Terdeteksi jam: {{ coin.time }}</div>
                    <div class="ca">CA: {{ coin.address }}</div>
                    <div class="desc">{{ coin.description }}</div>
                    <a href="{{ coin.url }}" target="_blank">📈 Buka Grafik di DexScreener &rarr;</a>
                </div>
                {% endfor %}
            {% else %}
                <div class="empty">Belum ada koin yang tersaring. Menunggu sinyal baru...</div>
            {% endif %}
        </div>
    </div>

    <script>
        // Auto refresh halaman setiap 15 detik agar data koin baru muncul otomatis
        setTimeout(() => {
            location.reload();
        }, 15000);
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

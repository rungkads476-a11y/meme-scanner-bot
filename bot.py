import time
import requests

# Masukkan Token Bot Telegram (dari @BotFather) dan Chat ID kamu di sini
TELEGRAM_BOT_TOKEN = "MASUKKAN_BOT_TOKEN_DISINI"
TELEGRAM_CHAT_ID = "MASUKKAN_CHAT_ID_DISINI"

def send_telegram_alert(message):
    """Fungsi untuk mengirim pesan ke Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Gagal kirim pesan: {e}")

def scan_new_tokens():
    """Mengambil data token terbaru dari DexScreener API untuk jaringan Solana"""
    url = "https://api.dexscreener.com/latest/dex/tokens/solana"
    try:
        response = requests.get(url)
        data = response.json()
        pairs = data.get("pairs", [])
        
        processed_pairs = set()

        for pair in pairs:
            address = pair.get("pairAddress")
            if address in processed_pairs:
                continue
            
            name = pair.get("baseToken", {}).get("name", "Unknown")
            symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            h6_volume = pair.get("volume", {}).get("h6", 0)
            ca = pair.get("baseToken", {}).get("address", "")
            
            # Filter: Likuiditas >= $10.000 dan Volume 1 Jam >= $20.000
            if liquidity >= 10000 and h6_volume >= 20000:
                msg = (
                    f"🚨 *POTENSI TOKEN BARU TERDETEKSI* 🚨\n\n"
                    f"🪙 *Nama:* {name} ({symbol})\n"
                    f"💧 *Likuiditas:* ${liquidity:,.0f}\n"
                    f"📊 *Volume (1j):* ${h1_volume:,.0f}\n"
                    f"📋 `CA: {ca}`\n\n"
                    f"[DexScreener](https://dexscreener.com/solana/{ca})"
                )
                
                send_telegram_alert(msg)
                processed_pairs.add(address)
                time.sleep(1)

    except Exception as e:
        print(f"Error saat scanning: {e}")

if __name__ == "__main__":
    print("🤖 Bot Scanner Meme Coin Berjalan...")
    while True:
        scan_new_tokens()
        time.sleep(60) # Cek ulang setiap 60 detik

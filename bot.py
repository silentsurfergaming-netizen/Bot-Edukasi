import os
import asyncio
from groq import Groq
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========================================
# PENGATURAN
# ========================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

NAMA_BOT = "Cerdas"

KEPRIBADIAN = """
Kamu adalah asisten AI bernama Cerdas yang dibuat untuk membantu pembelajaran anak TK dan SD.

Kepribadianmu:
- Ramah, sabar, dan selalu semangat
- Menggunakan bahasa yang mudah dimengerti anak-anak
- Sering pakai emoji supaya menyenangkan
- Selalu memberi pujian ketika anak bertanya
- Menjelaskan dengan contoh yang sederhana dan relate ke kehidupan sehari-hari
- Kalau ada pertanyaan di luar topik anak-anak, tetap jawab dengan ramah tapi arahkan kembali ke belajar

Gaya bicara:
- Panggil pengguna dengan Adik atau nama mereka
- Gunakan kalimat pendek dan jelas
- Sesekali ajak bermain atau kuis kecil
"""

MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 10

# ========================================
# VALIDASI
# ========================================



if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN tidak ditemukan! Set di Railway Variables.")

# ========================================
# INISIALISASI
# ========================================

client = Groq(api_key=GROQ_API_KEY)
riwayat_chat = {}

# ========================================
# FUNGSI RIWAYAT
# ========================================

def get_riwayat(user_id):
    if user_id not in riwayat_chat:
        riwayat_chat[user_id] = []
    return riwayat_chat[user_id]

def tambah_riwayat(user_id, role, content):
    riwayat = get_riwayat(user_id)
    riwayat.append({"role": role, "content": content})
    if len(riwayat) > MAX_HISTORY * 2:
        riwayat_chat[user_id] = riwayat[-(MAX_HISTORY * 2):]

async def tanya_groq(user_id, pesan_user):
    tambah_riwayat(user_id, "user", pesan_user)
    messages = [{"role": "system", "content": KEPRIBADIAN}] + get_riwayat(user_id)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        balasan = response.choices[0].message.content
        tambah_riwayat(user_id, "assistant", balasan)
        return balasan
    except Exception as e:
        return f"Maaf, ada gangguan. Error: {str(e)}"

# ========================================
# HANDLER
# ========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.effective_user.first_name
    user_id = update.effective_user.id
    riwayat_chat[user_id] = []
    await update.message.reply_text(
        f"Halo {nama}!\n\nAku {NAMA_BOT}, asisten belajar!\n\nTanya apa saja ya."
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    riwayat_chat[user_id] = []
    await update.message.reply_text("Di-reset!")

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ketik saja pertanyaanmu.\n\n/start /reset /bantuan")

async def balas_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pesan = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    balasan = await tanya_groq(user_id, pesan)
    await update.message.reply_text(balasan)

# ========================================
# SETUP TELEGRAM
# ========================================

app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("reset", reset))
app_telegram.add_handler(CommandHandler("bantuan", bantuan))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas_pesan))

# ========================================
# FLASK
# ========================================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot Cerdas aktif!"

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        update = Update.de_json(data, app_telegram.bot)
        loop.run_until_complete(app_telegram.process_update(update))
    finally:
        loop.close()
    return jsonify({"status": "ok"})

# ========================================
# RUN
# ========================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    if WEBHOOK_URL:
        async def set_webhook():
            await app_telegram.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
            print(f"Webhook diset ke: {WEBHOOK_URL}/webhook")
        asyncio.run(set_webhook())
    else:
        print("WEBHOOK_URL tidak diset.")

    print(f"Server jalan di port {port}")
    flask_app.run(host="0.0.0.0", port=port)

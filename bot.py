<<<<<<< HEAD
import os
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========================================
# PENGATURAN UTAMA — BISA KAMU UBAH!
# ========================================

TELEGRAM_TOKEN = os.environ.get("TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# --- KEPRIBADIAN BOT (BEBAS KAMU UBAH!) ---
NAMA_BOT = "Cerdas"  # Ganti nama bot sesukamu

KEPRIBADIAN = """
Kamu adalah asisten AI bernama Cerdas yang dibuat untuk membantu pembelajaran anak TK dan SD.

Kepribadianmu:
- Ramah, sabar, dan selalu semangat
- Menggunakan bahasa yang mudah dimengerti anak-anak
- Sering pakai emoji supaya menyenangkan 😊
- Selalu memberi pujian ketika anak bertanya
- Menjelaskan dengan contoh yang sederhana dan relate ke kehidupan sehari-hari
- Kalau ada pertanyaan di luar topik anak-anak, tetap jawab dengan ramah tapi arahkan kembali ke belajar

Gaya bicara:
- Panggil pengguna dengan "Adik" atau nama mereka
- Gunakan kalimat pendek dan jelas
- Sesekali ajak bermain atau kuis kecil
"""

# Model Groq yang dipakai (bisa diganti)
# Pilihan: "llama3-8b-8192" / "llama3-70b-8192" / "mixtral-8x7b-32768"
MODEL = "llama-3.3-70b-versatile"

# Maksimal riwayat percakapan yang diingat (per user)
MAX_HISTORY = 10

# ========================================
# KODE BOT (TIDAK PERLU DIUBAH)
# ========================================

client = Groq(api_key=GROQ_API_KEY)

# Simpan riwayat chat tiap user
riwayat_chat = {}

def get_riwayat(user_id):
    if user_id not in riwayat_chat:
        riwayat_chat[user_id] = []
    return riwayat_chat[user_id]

def tambah_riwayat(user_id, role, content):
    riwayat = get_riwayat(user_id)
    riwayat.append({"role": role, "content": content})
    # Batasi riwayat supaya tidak terlalu panjang
    if len(riwayat) > MAX_HISTORY * 2:
        riwayat_chat[user_id] = riwayat[-(MAX_HISTORY * 2):]

async def tanya_groq(user_id, pesan_user):
    """Kirim pesan ke Groq dan dapat balasan AI"""
    tambah_riwayat(user_id, "user", pesan_user)
    
    messages = [{"role": "system", "content": KEPRIBADIAN}] + get_riwayat(user_id)
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,  # 0 = kaku, 1 = kreatif (bisa diubah)
        )
        balasan = response.choices[0].message.content
        tambah_riwayat(user_id, "assistant", balasan)
        return balasan
    except Exception as e:
        return f"Maaf, ada gangguan teknis 😅 Coba lagi ya! (Error: {str(e)})"

# ========================================
# COMMAND HANDLER
# ========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.effective_user.first_name
    user_id = update.effective_user.id
    # Reset riwayat saat /start
    riwayat_chat[user_id] = []
    
    await update.message.reply_text(
        f"Halo {nama}! 👋🌟\n\n"
        f"Aku *{NAMA_BOT}*, asisten belajar pintarmu!\n\n"
        "Aku bisa bantu kamu:\n"
        "📚 Belajar pelajaran sekolah\n"
        "🔢 Berhitung dan matematika\n"
        "📖 Bahasa Indonesia & Inggris\n"
        "🌍 Pengetahuan umum\n"
        "❓ Menjawab pertanyaanmu\n\n"
        "Langsung tanya aja ya, jangan malu! 😊\n\n"
        "Ketik /reset kalau mau mulai percakapan baru\n"
        "Ketik /bantuan untuk lihat panduan",
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    riwayat_chat[user_id] = []
    await update.message.reply_text(
        "Percakapan direset! 🔄\n"
        "Halo lagi! Ada yang mau ditanyakan? 😊"
    )

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Panduan Bot Cerdas*\n\n"
        "🗣️ *Cara pakai:*\n"
        "Langsung ketik pertanyaanmu!\n\n"
        "⌨️ *Perintah tersedia:*\n"
        "/start — Mulai ulang bot\n"
        "/reset — Hapus riwayat chat\n"
        "/bantuan — Tampilkan panduan ini\n\n"
        "💡 *Contoh pertanyaan:*\n"
        "• Berapa 24 x 6?\n"
        "• Apa itu fotosintesis?\n"
        "• Tolong jelaskan pecahan!\n"
        "• Apa ibu kota Jawa Tengah?\n\n"
        "Selamat belajar! 🌟",
        parse_mode="Markdown"
    )

async def balas_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pesan = update.message.text
    
    # Tampilkan "mengetik..." saat bot memproses
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    balasan = await tanya_groq(user_id, pesan)
    await update.message.reply_text(balasan)

# ========================================
# JALANKAN BOT
# ========================================

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("bantuan", bantuan))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas_pesan))
    
    print(f"✅ Bot {NAMA_BOT} berjalan dengan Groq AI!")
    app.run_polling()

if __name__ == "__main__":
    main()
=======
import os
import asyncio
from groq import Groq
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========================================
# PENGATURAN
# ========================================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Set di Railway: https://domain-kamu.railway.app

NAMA_BOT = "Cerdas"

KEPRIBADIAN = """
Kamu adalah asisten AI bernama Cerdas yang dibuat untuk membantu pembelajaran anak TK dan SD.

Kepribadianmu:
- Ramah, sabar, dan selalu semangat
- Menggunakan bahasa yang mudah dimengerti anak-anak
- Sering pakai emoji supaya menyenangkan 😊
- Selalu memberi pujian ketika anak bertanya
- Menjelaskan dengan contoh yang sederhana dan relate ke kehidupan sehari-hari
- Kalau ada pertanyaan di luar topik anak-anak, tetap jawab dengan ramah tapi arahkan kembali ke belajar

Gaya bicara:
- Panggil pengguna dengan "Adik" atau nama mereka
- Gunakan kalimat pendek dan jelas
- Sesekali ajak bermain atau kuis kecil
"""

MODEL = "llama-3.3-70b-versatile"
MAX_HISTORY = 10

# ========================================
# VALIDASI TOKEN (crash lebih awal dengan pesan jelas)
# ========================================

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN tidak ditemukan! Set di Railway Variables.")

if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY tidak ditemukan! Set di Railway Variables.")

# ========================================
# INISIALISASI CLIENT
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
        return f"Maaf, ada gangguan 😅\nError: {str(e)}"

# ========================================
# HANDLER
# ========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nama = update.effective_user.first_name
    user_id = update.effective_user.id
    riwayat_chat[user_id] = []
    await update.message.reply_text(
        f"Halo {nama}! 👋🌟\n\n"
        f"Aku *{NAMA_BOT}*, asisten belajar!\n\n"
        "Tanya apa saja ya 😊",
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    riwayat_chat[user_id] = []
    await update.message.reply_text("Di-reset! 🔄")

async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ketik saja pertanyaanmu 😊\n\n/start /reset /bantuan"
    )

async def balas_pesan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pesan = update.message.text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    balasan = await tanya_groq(user_id, pesan)
    await update.message.reply_text(balasan)

# ========================================
# SETUP TELEGRAM APPLICATION
# ========================================

app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("reset", reset))
app_telegram.add_handler(CommandHandler("bantuan", bantuan))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balas_pesan))

# ========================================
# FLASK APP
# ========================================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot Cerdas aktif 🚀"

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

    # Set webhook ke Railway URL
    if WEBHOOK_URL:
        async def set_webhook():
            await app_telegram.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
            print(f"✅ Webhook diset ke: {WEBHOOK_URL}/webhook")

        asyncio.run(set_webhook())
    else:
        print("⚠️  WEBHOOK_URL tidak diset, webhook tidak dikonfigurasi.")

    print(f"🚀 Server jalan di port {port}")
    flask_app.run(host="0.0.0.0", port=port)
>>>>>>> dc44b0d (fix bot Railway)

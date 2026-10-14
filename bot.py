import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from faker import Faker
import config
import database

# Inisialisasi database saat bot pertama kali jalan
database.init_db()
faker = Faker('id_ID')

def generate_task_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📝 Register a new account", callback_data="new_task")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Selamat datang di Bot Kandang Gmail!\nSilakan klik tombol di bawah untuk membuat tugas baru.",
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "new_task":
        # 1. CEK APAKAH USER MASIH PUNYA TASK AKTIF
        active_task = database.get_active_task(user_id)
        if active_task:
            await query.message.reply_text(
                "⚠️ **Peringatan!**\n\n"
                "Anda tidak boleh membuat tugas baru sebelum menyelesaikan atau membatalkan tugas yang sedang berjalan.\n\n"
                "Silakan klik tombol **✅ Done (Submit)** atau **❌ Cancel Registration** pada pesan tugas Anda sebelumnya.",
                parse_mode="Markdown"
            )
            return

        # 2. JIKA TIDAK ADA, BUAT TUGAS BARU
        task_id = generate_task_id()
        first_name = faker.first_name()
        last_name = faker.last_name()
        clean_email = (first_name + last_name).lower().replace("'", "").replace(" ", "")
        email = f"{clean_email}{random.randint(100, 999)}@gmail.com"
        password = "sgsg" + ''.join(random.choices(string.digits, k=4))
        birth_date = f"{random.randint(1, 28)} Oktober 1998"

        # Simpan ke database dengan status 'active'
        database.save_task(task_id, user_id, first_name, last_name, email, password, birth_date)

        text = (
            f"📋 **TASK-ID: {task_id}**\n\n"
            f"Daftarkan akun Gmail menggunakan data di bawah ini:\n\n"
            f"👤 Nama depan: {first_name}\n"
            f"👤 Nama belakang: {last_name}\n"
            f"📧 Email: `{email}`\n"
            f"🔑 Password: `{password}`\n"
            f"📅 Tanggal / Tahun lahir: {birth_date}\n\n"
            f"⚠️ **PERHATIAN !**\n"
            f"❗ Pastikan alamat email & password sesuai dengan data diatas.\n"
            f"❗ Otak-atik akun yg sudah disetor = banned permanen."
        )

        keyboard = [
            [InlineKeyboardButton("✅ Done (Submit)", callback_data=f"done_{task_id}")],
            [InlineKeyboardButton("❌ Cancel Registration", callback_data=f"cancel_{task_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(text, parse_reply_markup=True, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("done_"):
        task_id = query.data.split("_")[1]
        database.update_task_status(task_id, "completed")
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(f"✅ Tugas `{task_id}` berhasil diselesaikan dan disetor!", parse_mode="Markdown")

    elif query.data.startswith("cancel_"):
        task_id = query.data.split("_")[1]
        database.update_task_status(task_id, "cancelled")
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(f"❌ Tugas `{task_id}` telah dibatalkan.", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("Bot modular siap dijalankan...")
    app.run_polling()

if __name__ == "__main__":
    main()

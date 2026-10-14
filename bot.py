import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from faker import Faker
import config
import database

database.init_db()
faker = Faker('id_ID')

def generate_task_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Keyboard Menu Utama (Reply Keyboard di bawah chat)
def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📝 Register a new account"), KeyboardButton("💰 Balance")],
        [KeyboardButton("👤 My Account"), KeyboardButton("👥 My Referrals")],
        [KeyboardButton("❓ Help"), KeyboardButton("ℹ️ Info")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    database.get_or_create_user(user_id)
    
    inline_keyboard = [
        [InlineKeyboardButton("📝 Register a new account", callback_data="new_task")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    
    await update.message.reply_text(
        "Selamat datang di Bot Kandang Gmail!\n"
        "Silakan gunakan menu di bawah atau klik tombol untuk mulai membuat tugas.",
        reply_markup=get_main_menu_keyboard()
    )
    await update.message.reply_text("Aksi cepat:", reply_markup=reply_markup)

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    database.get_or_create_user(user_id)

    if text == "📝 Register a new account":
        # Panggil logika pembuatan tugas baru
        await create_new_task_process(update, user_id)
        
    elif text == "💰 Balance":
        stats = database.get_user_stats(user_id)
        balance = stats[0] if stats else 0
        await update.message.reply_text(
            f"💰 **Saldo Anda Saat Ini:**\nRp {balance:,}".replace(",", "."),
            parse_mode="Markdown"
        )
        
    elif text == "👤 My Account":
        stats = database.get_user_stats(user_id)
        balance = stats[0] if stats else 0
        completed = stats[1] if stats else 0
        await update.message.reply_text(
            f"👤 **Informasi Akun Anda:**\n\n"
            f"🆔 ID Telegram: `{user_id}`\n"
            f"✅ Akun Selesai Disetor: {completed}\n"
            f"💰 Saldo: Rp {balance:,}".replace(",", "."),
            parse_mode="Markdown"
        )
        
    elif text == "👥 My Referrals":
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        stats = database.get_user_stats(user_id)
        ref_count = stats[2] if stats else 0
        await update.message.reply_text(
            f"👥 **Program Referral**\n\n"
            f"Ajak teman Anda bergabung menggunakan link di bawah ini:\n"
            f"`{referral_link}`\n\n"
            f"📊 Total Referral: {ref_count} orang",
            parse_mode="Markdown"
        )
        
    elif text == "❓ Help":
        await update.message.reply_text("❓ Silakan ikuti instruksi pada menu pendaftaran atau hubungi admin jika mengalami kendala.")
        
    elif text == "ℹ️ Info":
        await update.message.reply_text("ℹ️ Bot Kandang Gmail v1.0. Pastikan mematuhi rules yang berlaku agar akun dibayar.")

async def create_new_task_process(update_or_query, user_id):
    # Cek tugas aktif
    active_task = database.get_active_task(user_id)
    if active_task:
        msg = (
            "⚠️ **Peringatan!**\n\n"
            "Anda tidak boleh membuat tugas baru sebelum menyelesaikan atau membatalkan tugas yang sedang berjalan.\n\n"
            "Silakan klik tombol **✅ Done (Submit)** atau **❌ Cancel Registration** pada pesan tugas sebelumnya."
        )
        if hasattr(update_or_query, 'message'):
            await update_or_query.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update_or_query.reply_text(msg, parse_mode="Markdown")
        return

    task_id = generate_task_id()
    first_name = faker.first_name()
    last_name = faker.last_name()
    clean_email = (first_name + last_name).lower().replace("'", "").replace(" ", "")
    email = f"{clean_email}{random.randint(100, 999)}@gmail.com"
    password = "sgsg" + ''.join(random.choices(string.digits, k=4))
    birth_date = f"{random.randint(1, 28)} Oktober 1998"

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

    target_obj = update_or_query.message if hasattr(update_or_query, 'message') else update_or_query
    await target_obj.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "new_task":
        await create_new_task_process(query, user_id)

    elif query.data.startswith("done_"):
        task_id = query.data.split("_")[1]
        database.update_task_status(task_id, "completed", user_id)
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(f"✅ Tugas `{task_id}` berhasil diselesaikan dan disetor! Saldo Anda bertambah.", parse_mode="Markdown")

    elif query.data.startswith("cancel_"):
        task_id = query.data.split("_")[1]
        database.update_task_status(task_id, "cancelled")
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(f"❌ Tugas `{task_id}` telah dibatalkan.", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(config.TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    
    print("Bot modular siap dijalankan...")
    app.run_polling()

if __name__ == "__main__":
    main()

import random
import string
from datetime import datetime
from faker import Faker
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from config import TOKEN, ADMIN_IDS, NAMA_BULAN
from database import init_db, get_db_connection, get_setting, set_setting

init_db()
fake = Faker('id_ID')

def main_menu_keyboard(user_id):
    keyboard = [
        ["Register a new account", "❓ Help"],
        ["👤 My Account", "💰 Balance"],
        ["👥 My Referrals", "ℹ️ Info"]
    ]
    if user_id in ADMIN_IDS:
        keyboard.append(["🛠️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, balance) VALUES (?, ?, 0)", 
                   (user.id, user.username))
    conn.commit()
    conn.close()
    
    welcome_text = (
        f"Halo <b>{user.first_name}</b>!\n\n"
        "Selamat datang di Petani Gmail Bot. "
        "Silakan gunakan tombol di bawah untuk mulai mengerjakan tugas membuat akun Gmail!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=main_menu_keyboard(user.id))

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id in ADMIN_IDS and context.user_data.get('awaiting_input'):
        setting_type = context.user_data.get('awaiting_input')
        set_setting(setting_type, text.strip())
        context.user_data['awaiting_input'] = None
        conn.close()
        await update.message.reply_text(f"✅ **{setting_type.upper()}** berhasil diperbarui menjadi: `{text.strip()}`", parse_mode="Markdown")
        return

    if text == "Register a new account":
        task_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        clean_first = ''.join(e for e in first_name if e.isalnum()).lower()
        clean_last = ''.join(e for e in last_name if e.isalnum()).lower()
        three_digits = ''.join(random.choices(string.digits, k=3))
        email = f"{clean_first}{clean_last}{three_digits}@gmail.com"
        
        password = get_setting('password_pattern') or "fineirga"
        rand_day = random.randint(1, 28)
        rand_month = random.choice(NAMA_BULAN)
        admin_year = get_setting('birth_year')
        birth_date = f"{rand_day} {rand_month} {admin_year}"

        cursor.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, 'active', '')",
                       (task_id, user_id, email, password, f"{first_name} {last_name}", birth_date))
        conn.commit()
        conn.close()

        msg = (
            f"📋 **TASK-ID: {task_id}**\n\n"
            f"Daftarkan akun Gmail menggunakan data di bawah ini dan dapatkan **Rp 3.000** untuk setiap akun.\n\n"
            f"👤 **Nama depan:** {first_name}\n"
            f"👤 **Nama belakang:** {last_name}\n"
            f"📧 **Email:** `{email}`\n"
            f"🔑 **Password:** `{password}`\n"
            f"📅 **Tanggal / Tahun lahir:** {birth_date}\n\n"
            f"⚠️ **PERHATIAN !**\n"
            f"❗ Pastikan alamat email & password sesuai dengan data diatas.\n"
            f"❗ Otak-atik akun yg sudah disetor = banned permanen."
        )
        keyboard = [
            [InlineKeyboardButton("✅ Done (Submit)", callback_data=f"done_{task_id}")],
            [InlineKeyboardButton("❌ Cancel Registration", callback_data=f"cancel_{task_id}")]
        ]
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "💰 Balance":
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        res = cursor.fetchone()
        conn.close()
        balance = res[0] if res else 0
        await update.message.reply_text(f"💰 Saldo Anda saat ini: **Rp {balance:,}**", parse_mode="Markdown")

    elif text == "👤 My Account":
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        b_res = cursor.fetchone()
        balance = b_res[0] if b_res else 0

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
        total_processed = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'", (user_id,))
        accounts_registered = cursor.fetchone()[0]
        hold_balance = accounts_registered * 3000

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'approved'", (user_id,))
        accounts_approved = cursor.fetchone()[0]
        total_earned = accounts_approved * 3000

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'rejected'", (user_id,))
        accounts_rejected = cursor.fetchone()[0]
        conn.close()

        stats_text = (
            f"Your Stats:\n"
            f"-----------------------------------\n\n"
            f"💰 Balance: Rp {balance:,}\n"
            f"⏳ Hold Balance: Rp {hold_balance:,}\n"
            f"🏆 Score: 0 (Rank: N/A)\n"
            f"🏅 Total Earned: Rp {total_earned:,}\n\n"
            f"📝 Accounts Processed: {total_processed}\n"
            f"🎩 Accounts Registered (Pending): {accounts_registered}\n"
            f"✅ Accounts Approved: {accounts_approved}\n"
            f"❌ Accounts Rejected: {accounts_rejected}\n"
            f"⚠️ Accounts Complained: 0"
        )
        await update.message.reply_text(stats_text)

    elif text == "❓ Help":
        conn.close()
        await update.message.reply_text("Silakan pilih 'Register a new account' untuk mendapatkan tugas membuat email baru.")

    elif text == "🛠️ Admin Panel" and user_id in ADMIN_IDS:
        conn.close()
        current_year = get_setting('birth_year')
        current_pass = get_setting('password_pattern')

        txt = (
            f"🛠️ **ADMIN PANEL**\n\n"
            f"⚙️ **Pengaturan Saat Ini:**\n"
            f"• Tahun Lahir Default: `{current_year}`\n"
            f"• Password Default: `{current_pass}`\n\n"
            f"Pilih menu di bawah ini:"
        )
        keyboard = [
            [InlineKeyboardButton("📋 Review Tugas Pending", callback_data="adm_menu_pending")],
            [
                InlineKeyboardButton("⚙️ Set Tahun Lahir", callback_data="adm_set_year"),
                InlineKeyboardButton("⚙️ Set Password", callback_data="adm_set_pass")
            ]
        ]
        await update.message.reply_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        conn.close()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    if data.startswith("done_"):
        task_id = data.split("_")[1]
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE tasks SET status = 'pending', created_at = ? WHERE task_id = ? AND user_id = ?", (now_str, task_id, user_id))
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            await query.edit_message_text(f"⏳ Tugas {task_id} berhasil diserahkan dan masuk antrean review!")
        else:
            conn.close()
            await query.edit_message_text("❌ Tugas tidak ditemukan.")

    elif data.startswith("cancel_"):
        task_id = data.split("_")[1]
        cursor.execute("UPDATE tasks SET status = 'cancelled' WHERE task_id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        conn.close()
        await query.edit_message_text(f"❌ Registrasi dengan Task-ID {task_id} telah dibatalkan.")

    elif data == "adm_set_year" and user_id in ADMIN_IDS:
        conn.close()
        context.user_data['awaiting_input'] = 'birth_year'
        await query.message.reply_text("✏️ Silakan ketik **Tahun Lahir** baru yang ingin digunakan (contoh: `1995`):", parse_mode="Markdown")

    elif data == "adm_set_pass" and user_id in ADMIN_IDS:
        conn.close()
        context.user_data['awaiting_input'] = 'password_pattern'
        await query.message.reply_text("✏️ Silakan ketik **Password Default** baru yang ingin digunakan:", parse_mode="Markdown")

    elif data == "adm_menu_pending" and user_id in ADMIN_IDS:
        cursor.execute("SELECT DISTINCT date(created_at) FROM tasks WHERE status = 'pending'")
        dates = cursor.fetchall()
        conn.close()

        if not dates or not dates[0][0]:
            await query.edit_message_text("📭 Tidak ada tugas yang menunggu review saat ini.")
            return
        
        keyboard = []
        for d in dates:
            date_str = d[0]
            conn_sub = get_db_connection()
            cur_sub = conn_sub.cursor()
            cur_sub.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending' AND date(created_at) = ?", (date_str,))
            count = cur_sub.fetchone()[0]
            conn_sub.close()
            keyboard.append([InlineKeyboardButton(f"📅 Tanggal: {date_str} ({count} Tugas)", callback_data=f"adm_date_{date_str}")])
        
        await query.edit_message_text("🛠️ **Admin Panel - Pilih Tanggal:**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_date_") and user_id in ADMIN_IDS:
        selected_date = data.replace("adm_date_", "")
        cursor.execute("SELECT DISTINCT user_id FROM tasks WHERE status = 'pending' AND date(created_at) = ?", (selected_date,))
        members = cursor.fetchall()

        keyboard = []
        for m in members:
            m_id = m[0]
            cursor.execute("SELECT username FROM users WHERE user_id = ?", (m_id,))
            u_res = cursor.fetchone()
            uname = f"@{u_res[0]}" if u_res and u_res[0] else f"ID: {m_id}"

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending' AND user_id = ? AND date(created_at) = ?", (m_id, selected_date))
            t_count = cursor.fetchone()[0]
            keyboard.append([InlineKeyboardButton(f"👤 {uname} ({t_count} Tugas)", callback_data=f"adm_user_{selected_date}_{m_id}")])

        conn.close()
        keyboard.append([InlineKeyboardButton("🔙 Kembali ke Tanggal", callback_data="adm_menu_pending")])
        await query.edit_message_text(f"📅 **Tanggal: {selected_date}**\nPilih member di bawah:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_user_") and user_id in ADMIN_IDS:
        parts = data.split("_")
        selected_date = parts[2]
        selected_user = int(parts[3])

        cursor.execute("SELECT task_id FROM tasks WHERE status = 'pending' AND user_id = ? AND date(created_at) = ?", (selected_user, selected_date))
        tasks = cursor.fetchall()

        cursor.execute("SELECT username FROM users WHERE user_id = ?", (selected_user,))
        u_res = cursor.fetchone()
        uname = f"@{u_res[0]}" if u_res and u_res[0] else f"ID: {selected_user}"
        conn.close()

        keyboard = []
        for t in tasks:
            t_id = t[0]
            keyboard.append([InlineKeyboardButton(f"📌 Task ID: {t_id}", callback_data=f"adm_view_{t_id}_{selected_date}_{selected_user}")])

        keyboard.append([InlineKeyboardButton("🔙 Kembali ke List Member", callback_data=f"adm_date_{selected_date}")])
        await query.edit_message_text(f"👤 Member: **{uname}**\n📅 Tanggal: **{selected_date}**\n\nPilih tugas:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("adm_view_") and user_id in ADMIN_IDS:
        parts = data.split("_")
        task_id = parts[2]
        selected_date = parts[3]
        selected_user = parts[4]

        cursor.execute("SELECT task_id, user_id, email, password, birth_date, created_at FROM tasks WHERE task_id = ? AND status = 'pending'", (task_id,))
        res = cursor.fetchone()
        if res:
            t_id, u_id, email, pwd, b_date, created_at = res
            cursor.execute("SELECT username FROM users WHERE user_id = ?", (u_id,))
            u_res = cursor.fetchone()
            uname = f"@{u_res[0]}" if u_res and u_res[0] else f"ID: {u_id}"
            conn.close()

            txt = (
                f"📌 **Task ID:** {t_id}\n"
                f"👤 **User:** {uname} (`{u_id}`)\n"
                f"📅 **Waktu Submit:** {created_at}\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Password:** `{pwd}`\n"
                f"🎂 **Tgl Lahir:** {b_date}"
            )
            kb = [
                [
                    InlineKeyboardButton("Approve ✅", callback_data=f"adm_approve_{t_id}_{selected_date}_{selected_user}"),
                    InlineKeyboardButton("Reject ❌", callback_data=f"adm_reject_{t_id}_{selected_date}_{selected_user}")
                ],
                [InlineKeyboardButton("🔙 Kembali", callback_data=f"adm_user_{selected_date}_{selected_user}")]
            ]
            await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        else:
            conn.close()
            await query.edit_message_text("❌ Tugas sudah diproses.")

    elif data.startswith("adm_approve_") and user_id in ADMIN_IDS:
        parts = data.split("_")
        task_id = parts[2]
        selected_date = parts[3]
        selected_user = parts[4]

        cursor.execute("SELECT user_id, email FROM tasks WHERE task_id = ? AND status = 'pending'", (task_id,))
        res = cursor.fetchone()
        if res:
            target_user_id, email = res
            cursor.execute("UPDATE tasks SET status = 'approved' WHERE task_id = ?", (task_id,))
            cursor.execute("UPDATE users SET balance = balance + 3000 WHERE user_id = ?", (target_user_id,))
            conn.commit()
            conn.close()
            
            kb = [[InlineKeyboardButton("🔙 Kembali ke List Tugas", callback_data=f"adm_user_{selected_date}_{selected_user}")]]
            await query.edit_message_text(f"✅ Tugas {task_id} (Email: {email}) telah di-**APPROVE**. Saldo user ditambah Rp 3.000.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
            try:
                await context.bot.send_message(chat_id=target_user_id, text=f"🎉 Selamat! Tugas Gmail Anda dengan Task ID `{task_id}` disetujui admin. Saldo Rp 3.000 ditambahkan.", parse_mode="Markdown")
            except Exception:
                pass
        else:
            conn.close()
            await query.edit_message_text("❌ Tugas sudah diproses.")

    elif data.startswith("adm_reject_") and user_id in ADMIN_IDS:
        parts = data.split("_")
        task_id = parts[2]
        selected_date = parts[3]
        selected_user = parts[4]

        cursor.execute("SELECT user_id, email FROM tasks WHERE task_id = ? AND status = 'pending'", (task_id,))
        res = cursor.fetchone()
        if res:
            target_user_id, email = res
            cursor.execute("UPDATE tasks SET status = 'rejected' WHERE task_id = ?", (task_id,))
            conn.commit()
            conn.close()

            kb = [[InlineKeyboardButton("🔙 Kembali ke List Tugas", callback_data=f"adm_user_{selected_date}_{selected_user}")]]
            await query.edit_message_text(f"❌ Tugas {task_id} (Email: {email}) telah di-**REJECT** (Ditolak).", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
            try:
                await context.bot.send_message(chat_id=target_user_id, text=f"❌ Mohon maaf, tugas Gmail Anda dengan Task ID `{task_id}` ditolak admin.", parse_mode="Markdown")
            except Exception:
                pass
        else:
            conn.close()
            await query.edit_message_text("❌ Tugas sudah diproses.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot modular siap dijalankan...")
    app.run_polling()

if __name__ == '__main__':
    main()

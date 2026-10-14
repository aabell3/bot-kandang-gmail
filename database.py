import sqlite3

DB_NAME = "bot_gmail.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabel tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            password TEXT,
            birth_date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Tabel users untuk menyimpan saldo, total tugas selesai, dan referral
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            completed_tasks INTEGER DEFAULT 0,
            referred_by INTEGER,
            referral_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def get_or_create_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
    conn.close()
    return user

def get_active_task(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'active'", (user_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def save_task(task_id, user_id, first_name, last_name, email, password, birth_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (task_id, user_id, first_name, last_name, email, password, birth_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
    ''', (task_id, user_id, first_name, last_name, email, password, birth_date))
    conn.commit()
    conn.close()

def update_task_status(task_id, status, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id))
    
    # Jika tugas selesai, tambahkan saldo (misal: 3000 per akun) dan increment completed_tasks
    if status == "completed" and user_id:
        cursor.execute('''
            UPDATE users 
            SET balance = balance + 3000, completed_tasks = completed_tasks + 1 
            WHERE user_id = ?
        ''', (user_id,))
        
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, completed_tasks, referral_count FROM users WHERE user_id = ?", (user_id,))
    stats = cursor.fetchone()
    conn.close()
    return stats

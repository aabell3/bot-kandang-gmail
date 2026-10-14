import sqlite3

DB_NAME = "bot_gmail.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Tabel tugas dengan status: 'active', 'completed', 'cancelled'
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
    conn.commit()
    conn.close()

def get_active_task(user_id):
    """Mengecek apakah user memiliki task yang masih aktif (belum submit/cancel)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND status = 'active'",
        (user_id,)
    )
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

def update_task_status(task_id, status):
    """Mengubah status task menjadi 'completed' atau 'cancelled'"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = ? WHERE task_id = ?",
        (status, task_id)
    )
    conn.commit()
    conn.close()

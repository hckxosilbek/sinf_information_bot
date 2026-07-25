import aiosqlite
import logging

DB_NAME = "database.sqlite"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Create users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id BIGINT UNIQUE,
                full_name TEXT NOT NULL,
                is_agreed BOOLEAN DEFAULT 0,
                is_admin BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create files table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                user_id INTEGER NULLABLE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        await db.commit()
        logging.info("Database initialized.")

async def get_user_by_tg_id(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_by_name(full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        # Case insensitive partial match
        query = 'SELECT * FROM users WHERE full_name LIKE ? COLLATE NOCASE'
        async with db.execute(query, (f"%{full_name}%",)) as cursor:
            return await cursor.fetchall()

async def add_user(tg_id: int, full_name: str, is_admin: bool = False):
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute(
                'INSERT INTO users (tg_id, full_name, is_admin) VALUES (?, ?, ?)',
                (tg_id, full_name, is_admin)
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def update_user_agreement(tg_id: int, is_agreed: bool):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET is_agreed = ? WHERE tg_id = ?', (is_agreed, tg_id))
        await db.commit()

async def add_file(file_id: str, title: str, category: str, user_id: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO files (file_id, title, category, user_id) VALUES (?, ?, ?, ?)',
            (file_id, title, category, user_id)
        )
        await db.commit()

async def get_files_by_category_and_user(category: str, user_id: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        if user_id:
            query = 'SELECT * FROM files WHERE category = ? AND (user_id = ? OR user_id IS NULL)'
            async with db.execute(query, (category, user_id)) as cursor:
                return await cursor.fetchall()
        else:
            query = 'SELECT * FROM files WHERE category = ? AND user_id IS NULL'
            async with db.execute(query, (category,)) as cursor:
                return await cursor.fetchall()
async def get_all_class_files():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, title FROM class_files") as cursor:
            return await cursor.fetchall()

async def get_file_by_id(file_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT id, title, file_id, file_type FROM class_files WHERE id = ?", (file_id,)) as cursor:
            return await cursor.fetchone()
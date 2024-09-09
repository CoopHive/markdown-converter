import sqlite3


def create_api_keys_db():
    conn = sqlite3.connect('api_keys.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            api_key TEXT NOT NULL UNIQUE
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_api_keys_db()
    print("Database and table created successfully.")

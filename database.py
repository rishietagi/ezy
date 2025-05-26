import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rishisujan1234",
        database="ezy"
    )

def insert_user(first_name, last_name, phone, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (first_name, last_name, phone, email, password) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, phone, email, password)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] Insert failed: {e}")
        return False


def validate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = %s AND password = %s",
        (email, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, phone, email FROM users WHERE email=%s", (email,))
    result = cursor.fetchone()
    conn.close()
    return result

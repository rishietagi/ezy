import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rishisujan1234",
        database="medical_history"
    )

def insert_user(first_name, last_name, phone, email, password, age, gender):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, phone_number, email, password, age, gender)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (first_name, last_name, phone, email, password, age, gender)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        import traceback
        print(f"[DB ERROR] Insert failed: {e}")
        traceback.print_exc()
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
    cursor.execute("SELECT first_name, last_name, phone_number, email, id FROM users WHERE email=%s", (email,))
    result = cursor.fetchone()
    conn.close()
    return result


def log_login_time(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        current_time = datetime.now()
        cursor.execute(
            "INSERT INTO login_history (user_id, login_time) VALUES (%s, %s)",
            (user_id, current_time)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] Failed to log login time: {e}")


def get_login_history(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT login_time FROM login_history WHERE user_id = %s ORDER BY login_time DESC",
            (user_id,)
        )
        history = cursor.fetchall()
        conn.close()
        return history
    except Exception as e:
        print(f"[DB ERROR] Failed to fetch login history: {e}")
        return []

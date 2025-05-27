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


def save_report(user_id, filename, report_content, analysis):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO report_sessions (user_id, filename, report_content, analysis) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (user_id, filename, report_content, analysis))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_reports(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, filename, created_at FROM report_sessions WHERE user_id = %s ORDER BY created_at DESC"
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_report_by_id(report_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM report_sessions WHERE id = %s"
    cursor.execute(query, (report_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_db_connection():
    import sqlite3
    from sqlite3 import Error

    conn = None
    try:
        conn = sqlite3.connect('ip_log.db')
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn):
    try:
        sql_create_ip_table = """ CREATE TABLE IF NOT EXISTS ip_log (
                                        id integer PRIMARY KEY,
                                        ip_address text NOT NULL,
                                        timestamp text NOT NULL
                                    ); """
        cursor = conn.cursor()
        cursor.execute(sql_create_ip_table)
    except Error as e:
        print(e)


def log_ip(conn, ip_address):
    from datetime import datetime

    sql = ''' INSERT INTO ip_log(ip_address, timestamp)
              VALUES(?,?) '''
    cursor = conn.cursor()
    cursor.execute(sql, (ip_address, datetime.now()))
    conn.commit()
    return cursor.lastrowid


def get_ip_history(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ip_log ORDER BY timestamp DESC")

    rows = cursor.fetchall()
    return rows


def close_connection(conn):
    if conn:
        conn.close()
import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        host='aurasolutions.c1yaeyakumzl.us-east-2.rds.amazonaws.com',
        database='DB_Test',
        user='AdminAura',
        password='Aur4S0lu71oN!'
    )
    return conn

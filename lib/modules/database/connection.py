import psycopg2

def connect_db(url):
    conn = psycopg2.connect(url)
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()


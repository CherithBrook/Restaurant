import psycopg2

def get_conn():
    return psycopg2.connect(
        host="aws-1-ap-south-1.pooler.supabase.com",
        port=6543,
        database="postgres",
        user="postgres.awtlaajmbwpamhygvjus",
        password="bea123!bea1",
        sslmode="require"
    )

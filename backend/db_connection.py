# #db_connection.py

# import psycopg2

# def connect_db(connection_string: str):
#     """
#     Establishes and returns a PostgreSQL connection.

#     Args:
#         connection_string (str): PostgreSQL connection string.

#     Returns:
#         connection: psycopg2 connection object or None if error.
#     """
#     try:
#         conn = psycopg2.connect(connection_string)
#         return conn
#     except Exception as e:
#         print("Database connection error:", e)
#         return None

import os
from supabase import create_client, Client
from typing import Optional

def connect_db() -> Optional[Client]:
    """
    Establishes and returns a Supabase client connection.

    Returns:
        Client: Supabase client object or None if error.
    """
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY not set in environment variables")
        supabase: Client = create_client(supabase_url, supabase_key)
        return supabase
    except Exception as e:
        print("Supabase connection error:", e)
        return None
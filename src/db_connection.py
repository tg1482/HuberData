from dotenv import load_dotenv
import os
import mysql.connector


def connect_to_db():
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve variables from environment
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    # Connect to the database
    db = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )

    return db

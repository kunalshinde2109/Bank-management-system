import mysql.connector


def create_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="",
            database="bank managment"
        )

        return connection

    except mysql.connector.Error as error:
        print("Database connection failed!")
        print("Error:", error)
        return None
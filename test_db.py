
from database import create_connection

connection = create_connection()

if connection:
    print("Database Connected Successfully!")
    connection.close()
else:
    print("Connection Failed!")

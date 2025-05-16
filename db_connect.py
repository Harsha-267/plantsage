import mysql.connector
from mysql.connector import Error
import traceback

print("Script started")
print("Importing MySQL connector...")

try:
    print("Import successful!")
    print("Attempting to connect...")

    connection = mysql.connector.connect(
        host='localhost',
        database='plantsage_db',
        user='plantapp',
        password='Khv@0151'
    )

    if connection.is_connected():
        print("Connection to MySQL was successful!")

except Error as e:
    print("MySQL-specific error:")
    print(e)

except Exception as ex:
    print("General error:")
    traceback.print_exc()

finally:
    try:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection is closed")
    except:
        pass

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
import mysql.connector
import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key
socketio = SocketIO(app)

# MySQL Database Configuration (using environment variables)
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

def get_db_connection():
    try:
        mydb = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return mydb
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def get_new_data():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)

            # Example: Querying multiple tables
            data = {}  # Dictionary to store data from different tables

            # Query table 1: activity_log
            cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 10")
            data['activity_log'] = cursor.fetchall()

            # Query table 2: access_logs
            cursor.execute("SELECT * FROM access_logs ORDER BY timestamp DESC LIMIT 10")
            data['access_logs'] = cursor.fetchall()

            # Query table 3: access_attempts
            cursor.execute("SELECT * FROM access_attempts ORDER BY timestamp DESC LIMIT 10")
            data['access_attempts'] = cursor.fetchall()

            # Query table 4: alerts
            cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10")
            data['alerts'] = cursor.fetchall()

	    # Query table 4: alerts
            cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10")
            data['alerts'] = cursor.fetchall()

            conn.close()
            return data  # Return a dictionary containing data from all tables

        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
            return None
    else:
        return None

@socketio.on('connect')  # Handle client connections
def handle_connect():
    print('Client connected')
    new_data = get_new_data()  # Get initial data
    if new_data:
        emit('data_update', new_data)  # Send data to the client

@socketio.on('disconnect')  # Handle client disconnections
def handle_disconnect():
    print('Client disconnected')

def update_data_periodically():  # Function to periodically update data
    while True:
        new_data = get_new_data()
        if new_data:
            socketio.emit('data_update', new_data)  # Send data updates via WebSocket
        time.sleep(5)  # Adjust the update interval as needed

thread = threading.Thread(target=update_data_periodically)  # Start update thread
thread.daemon = True
thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)  # Run with SocketIO
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pymysql
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return jsonify({"message": "Tailored Travels Backend Running!"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get("email")
    password = generate_password_hash(data.get("password"))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"message": "User already exists"}), 400

        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        connection.commit()

    return jsonify({"message": "Registration successful"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user'] = {"email": user["email"], "id": user["id"]}
            return jsonify({"message": "Login successful", "user": session['user']}), 200

    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/session', methods=['GET'])
def get_session():
    if 'user' in session:
        return jsonify({"user": session['user']}), 200
    return jsonify({"user": None}), 401

@app.route('/api/trips', methods=['GET'])
def get_trips():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user_id = session['user']['id']
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM trips WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        trips = cursor.fetchall()

    return jsonify({"trips": trips}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

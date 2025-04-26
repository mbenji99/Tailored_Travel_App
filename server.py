#!/usr/bin/env python3
import os
import sys
import logging
import asyncio
import pandas as pd
import pymysql
from flask import Flask, request, jsonify, session, abort
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import python_weather
from currency_converter import CurrencyConverter
from skyscanner.skyscanner import Flights

# ─── Make ai_model/src importable ───────────────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
AI_SRC   = os.path.join(BASE_DIR, "ai_model", "src")
sys.path.insert(0, AI_SRC)

from inference import predict  # your hybrid/pure-CF inference function

# ─── Environment & Model Paths ─────────────────────────────────────────────────
load_dotenv()
MODEL_DIR         = os.getenv("MODEL_DIR", os.path.join(BASE_DIR, "ai_model", "outputs", "models"))
MODEL_PATH        = os.path.join(MODEL_DIR, os.getenv("HYBRID_MODEL_FILE", "hybrid_travel_recommender_model.keras"))
SCALER_PATH       = os.path.join(MODEL_DIR, os.getenv("SCALER_FILE",            "scaler.joblib"))
ENCODER_PATH      = os.path.join(MODEL_DIR, os.getenv("ENCODER_FILE",         "encoder.joblib"))
CF_PATH           = os.path.join(MODEL_DIR, os.getenv("CF_FILE",              "cf_model.joblib"))
CB_PATH           = os.path.join(MODEL_DIR, os.getenv("CB_FILE",              "cb_recommender.joblib"))
CLUSTER_PATH      = os.path.join(MODEL_DIR, os.getenv("CLUSTER_FILE",         "clusters.joblib"))
FEATURE_LIST_PATH = os.path.join(BASE_DIR, "ai_model", "hybrid_feature_list.csv")

# ─── Flask App Setup ────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")
CORS(app, supports_credentials=True, origins=os.getenv("CORS_ORIGINS","").split(","))
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
app.logger.setLevel(logging.DEBUG)

# ─── Database Helper ───────────────────────────────────────────────────────────
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        cursorclass=pymysql.cursors.DictCursor
    )

# ─── External Service Clients ──────────────────────────────────────────────────
cc = CurrencyConverter()
sky_key = os.getenv("SKY_API_KEY","").strip()
sky_service = Flights(sky_key) if sky_key else None

# ─── Auth Endpoints ────────────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    email, pw = data.get("email",""), data.get("password","")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            return jsonify({"message":"User exists"}), 400
        cur.execute(
            "INSERT INTO users (email,password_hash) VALUES (%s,%s)",
            (email, generate_password_hash(pw))
        )
        conn.commit()
    return jsonify({"message":"Registered"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email, pw = data.get("email",""), data.get("password","")
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cur.fetchone()
    if user and check_password_hash(user['password_hash'], pw):
        session['user'] = {"id": user["id"], "email": user["email"]}
        return jsonify({"message":"Logged in","user":session['user']}),200
    return jsonify({"message":"Invalid credentials"}),401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message":"Logged out"}),200

@app.route('/api/session', methods=['GET'])
def get_session():
    user = session.get('user')
    return jsonify({"user": user or None}), (200 if user else 401)

# ─── Trip Endpoints ────────────────────────────────────────────────────────────
@app.route('/api/trips', methods=['GET'])
def list_trips():
    if 'user' not in session:
        return jsonify({"message":"Unauthorized"}),401
    uid = session['user']['id']
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM trips WHERE user_id=%s ORDER BY created_at DESC",(uid,))
        trips = cur.fetchall()
    return jsonify({"trips":trips}),200

@app.route('/api/trips', methods=['POST'])
def create_trip():
    if 'user' not in session:
        return jsonify({"message":"Unauthorized"}),401
    data = request.json or {}
    dest   = data.get("destination","")
    budget = float(data.get("budget",0) or 0)
    wpref  = data.get("weather_preference","")
    epref  = data.get("environment_preference","")
    apref  = data.get("activity_preference","")
    if not dest or budget <= 0:
        return jsonify({"message":"Invalid payload"}),400

    uid = session['user']['id']
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO trips
               (user_id,destination,budget,remaining_budget,
                weather_preference,environment_preference,activity_preference)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (uid, dest, budget, budget, wpref, epref, apref)
        )
        conn.commit()
        trip_id = cur.lastrowid

    trip = {
        "id": trip_id,
        "destination": dest,
        "budget": budget,
        "remaining_budget": budget,
        "status": "planning",
        "weather_preference": wpref,
        "environment_preference": epref,
        "activity_preference": apref
    }
    return jsonify({"trip":trip}),201

@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    if 'user' not in session:
        return jsonify({"message":"Unauthorized"}),401
    uid = session['user']['id']
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM trips WHERE id=%s AND user_id=%s",(trip_id,uid))
        trip = cur.fetchone()
    if not trip:
        abort(404, description="Trip not found")
    return jsonify({"trip":trip}),200

# ─── Feature Builder ───────────────────────────────────────────────────────────
def build_numeric_features(destination: str) -> dict:
    nf = {
        "temperature": 0.0,
        "currency_rate": 1.0,
        "flight_price": 0.0,
        "booking_price": 0.0,
        "num_arrivals": 0
    }
    # Weather
    try:
        weather = asyncio.run(_get_weather(destination))
        nf["temperature"] = weather.current.temperature or 0.0
    except Exception:
        app.logger.warning("🌤️ Weather fetch failed for %s", destination)
    # Currency
    try:
        nf["currency_rate"] = cc.convert(1, "USD", "USD")
    except Exception:
        app.logger.warning("💱 Currency conversion failed for %s", destination)
    # Flight price stub
    if sky_service:
        try:
            nf["flight_price"] = 0.0
        except Exception:
            app.logger.warning("✈️ Flight price fetch failed for %s", destination)
    return nf

async def _get_weather(loc: str):
    client = python_weather.Client()
    res = await client.find(loc)
    await client.close()
    return res

# ─── Trip-Scoped Recommendations ───────────────────────────────────────────────
@app.route('/api/trips/<int:trip_id>/recommendations', methods=['GET'])
def recs_for_trip(trip_id):
    if 'user' not in session:
        return jsonify({"message":"Unauthorized"}),401
    uid = session['user']['id']

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM trips WHERE id=%s AND user_id=%s", (trip_id, uid))
        trip = cur.fetchone()
    if not trip:
        return jsonify({"message":"Trip not found"}),404

    nf = build_numeric_features(trip["destination"])
    app.logger.debug("⚙️ Numeric features for trip %s: %s", trip_id, nf)

    try:
        score = predict(
            uid,
            str(trip_id),
            model_path=MODEL_PATH,
            scaler_path=SCALER_PATH,
            encoder_path=ENCODER_PATH,
            cf_path=CF_PATH,
            cb_path=CB_PATH,
            cluster_path=CLUSTER_PATH,
            feature_list_path=FEATURE_LIST_PATH,
            numeric_features=nf
        )
        recs = [{
            "destination_id": str(trip_id),
            "predicted_rating": float(score),
            "external_features": nf
        }]
        return jsonify({"recommendations": recs}),200

    except Exception as e:
        app.logger.error("❌ Trip-scoped inference error for trip %s: %s", trip_id, e, exc_info=True)
        fallback = {
            "destination_id": str(trip_id),
            "predicted_rating": 3.0,
            "external_features": nf,
            "message": "Fallback score due to inference error"
        }
        return jsonify({"recommendations": [fallback]}),200

# ─── Single-Destination Recommendation ────────────────────────────────────────
@app.route('/api/recommend', methods=['GET'])
def recommend_dest():
    dest = request.args.get("destination_id","").strip()
    if not dest:
        return jsonify({"message":"Missing destination_id"}),400

    nf = build_numeric_features(dest)
    app.logger.debug("⚙️ Numeric features for single dest %s: %s", dest, nf)

    try:
        score = predict(
            session.get('user',{}).get('id',''),
            dest,
            model_path=MODEL_PATH,
            scaler_path=SCALER_PATH,
            encoder_path=ENCODER_PATH,
            cf_path=CF_PATH,
            cb_path=CB_PATH,
            cluster_path=CLUSTER_PATH,
            feature_list_path=FEATURE_LIST_PATH,
            numeric_features=nf
        )
        return jsonify({
            "destination_id": dest,
            "predicted_rating": float(score),
            "external_features": nf
        }),200

    except Exception as e:
        app.logger.error("❌ Single-dest inference error for %s: %s", dest, e, exc_info=True)
        fallback_score = 3.0
        return jsonify({
            "destination_id": dest,
            "predicted_rating": fallback_score,
            "external_features": nf,
            "message": "Fallback score due to inference error"
        }),200

# ─── Health Check ──────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return jsonify({"message":"Tailored Travels Backend Running!"}),200

# ─── Run Server ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

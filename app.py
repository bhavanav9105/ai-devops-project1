from flask import Flask, render_template, request, jsonify, redirect, url_for
import pickle
import numpy as np
import pandas as pd
import os
import json
import sqlite3
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# ─── Environment Detection ───────────────────────────────────────────────────
ENV = os.environ.get("ENV", "DEV")

# ─── Storage: pluggable backend (SQLite default; swap for Postgres/MySQL etc.) ─
DB_PATH = os.environ.get("DB_PATH", "sales_data.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            env TEXT,
            marketing REAL,
            visits REAL,
            price REAL,
            season TEXT,
            region TEXT,
            discount REAL,
            ad_channel TEXT,
            predicted_sales REAL,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month INTEGER,
            revenue REAL,
            market_share REAL,
            growth_rate REAL,
            industry_avg REAL
        )
    """)
    # Seed historical market data if empty
    c.execute("SELECT COUNT(*) FROM market_data")
    if c.fetchone()[0] == 0:
        random.seed(42)
        for year in [2022, 2023, 2024]:
            base = 80000 if year == 2022 else (95000 if year == 2023 else 115000)
            for month in range(1, 13):
                rev = base + random.uniform(-8000, 12000) + (month * 1200)
                c.execute("INSERT INTO market_data VALUES (NULL,?,?,?,?,?,?)",
                    (year, month, round(rev,2),
                     round(random.uniform(18,28),2),
                     round(random.uniform(2,14),2),
                     round(rev * random.uniform(0.85,0.92), 2)))
        conn.commit()
    conn.close()

init_db()

# ─── Load model ──────────────────────────────────────────────────────────────
model = pickle.load(open("sales_model.pkl", "rb"))

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    """Company marketing landing page."""
    return render_template("landing.html", env=ENV)

@app.route("/dashboard")
def dashboard():
    """Main analytics dashboard (env=dev/test/prod)."""
    return render_template("dashboard.html", env=ENV)

@app.route("/predict", methods=["POST"])
def predict():
    marketing  = float(request.form["marketing"])
    visits     = float(request.form["visits"])
    price      = float(request.form["price"])
    season     = request.form.get("season", "Q1")
    region     = request.form.get("region", "North")
    discount   = float(request.form.get("discount", 0))
    ad_channel = request.form.get("ad_channel", "Social Media")

    season_map = {"Q1": 0.9, "Q2": 1.0, "Q3": 1.15, "Q4": 1.3}
    region_map = {"North": 1.0, "South": 1.05, "East": 0.95, "West": 1.1, "Central": 1.0}
    channel_map = {"Social Media": 1.1, "TV": 1.05, "Email": 0.95,
                   "SEO/SEM": 1.08, "Influencer": 1.12, "Print": 0.9}

    adjusted_marketing = marketing * season_map.get(season, 1.0) * channel_map.get(ad_channel, 1.0)
    adjusted_price     = price * (1 - discount / 100)
    adjusted_visits    = visits * region_map.get(region, 1.0)

    base_prediction = model.predict([[adjusted_marketing, adjusted_visits, adjusted_price]])[0]
    predicted_sales = round(base_prediction, 2)

    # persist to DB
    conn = get_db()
    conn.execute(
        "INSERT INTO predictions (env,marketing,visits,price,season,region,discount,ad_channel,predicted_sales,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (ENV, marketing, visits, price, season, region, discount, ad_channel, predicted_sales, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    # Build insights
    insights = []
    if marketing < 2000:
        insights.append({"icon": "📢", "text": "Increasing marketing spend by 20% could boost sales by ~$1,200"})
    if discount > 20:
        insights.append({"icon": "⚠️", "text": f"High discount ({discount}%) may erode margins — try bundling instead"})
    if ad_channel == "Print":
        insights.append({"icon": "💡", "text": "Switching from Print to Social Media typically yields 15–20% higher reach"})
    if visits < 150:
        insights.append({"icon": "🚀", "text": "Invest in UX improvements; low visits may indicate poor discoverability"})
    if season == "Q4":
        insights.append({"icon": "🎄", "text": "Q4 holiday boost detected — consider seasonal promotions to maximize revenue"})

    # Scenario comparisons
    scenarios = []
    for extra_mkt in [0, 500, 1000, 2000]:
        s_pred = model.predict([[adjusted_marketing + extra_mkt, adjusted_visits, adjusted_price]])[0]
        scenarios.append({"label": f"+${extra_mkt} Marketing", "value": round(s_pred, 2)})

    return jsonify({
        "predicted_sales": predicted_sales,
        "insights": insights,
        "scenarios": scenarios,
        "inputs": {
            "marketing": marketing, "visits": visits, "price": price,
            "season": season, "region": region, "discount": discount, "ad_channel": ad_channel
        }
    })

@app.route("/api/historical")
def historical():
    year = request.args.get("year", None)
    conn = get_db()
    if year:
        rows = conn.execute("SELECT * FROM market_data WHERE year=? ORDER BY month", (year,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM market_data ORDER BY year, month").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/predictions/history")
def prediction_history():
    conn = get_db()
    rows = conn.execute("SELECT * FROM predictions WHERE env=? ORDER BY created_at DESC LIMIT 50", (ENV,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/kpis")
def kpis():
    conn = get_db()
    rows = conn.execute("SELECT * FROM market_data ORDER BY year, month").fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    if not data:
        return jsonify({})
    total_revenue = sum(d["revenue"] for d in data)
    avg_growth    = sum(d["growth_rate"] for d in data) / len(data)
    max_revenue   = max(d["revenue"] for d in data)
    avg_market_share = sum(d["market_share"] for d in data) / len(data)
    return jsonify({
        "total_revenue": round(total_revenue, 2),
        "avg_growth": round(avg_growth, 2),
        "max_revenue": round(max_revenue, 2),
        "avg_market_share": round(avg_market_share, 2),
        "env": ENV
    })

@app.route("/api/stock_trend")
def stock_trend():
    """Simulate share market trend data for the company."""
    random.seed(10)
    labels, prices, volumes = [], [], []
    price = 142.0
    for i in range(30):
        day = (datetime.now() - timedelta(days=29-i)).strftime("%b %d")
        price += random.uniform(-4, 5)
        labels.append(day)
        prices.append(round(price, 2))
        volumes.append(random.randint(800000, 3000000))
    return jsonify({"labels": labels, "prices": prices, "volumes": volumes})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=(ENV == "DEV"))

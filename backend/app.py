from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Initialize Flask with static folder
app = Flask(__name__, static_folder="static")
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL')


# 🔌 DB CONNECTION
def get_db_connection():
    is_postgres = DATABASE_URL and 'postgresql://' in DATABASE_URL and '@host:' not in DATABASE_URL
    
    if is_postgres:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        db_path = os.path.join(os.path.dirname(__file__), 'database.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn


# 🔍 SEARCH API
@app.route('/api/search', methods=['GET'])
def search_medicine():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    cur = conn.cursor()

    if isinstance(conn, sqlite3.Connection):
        sql = """
            SELECT 
                b.brand_name, 
                m.generic_name, 
                m.salt, 
                m.dosage, 
                m.form, 
                b.mrp as brand_price, 
                m.jan_price as generic_price
            FROM brands b
            JOIN medicines m ON b.generic_id = m.id
            WHERE b.brand_name LIKE ? OR m.generic_name LIKE ?
        """
        search_term = f"%{query}%"
        cur.execute(sql, (search_term, search_term))
    else:
        sql = """
            SELECT 
                b.brand_name, 
                m.generic_name, 
                m.salt, 
                m.dosage, 
                m.form, 
                b.mrp as brand_price, 
                m.jan_price as generic_price
            FROM brands b
            JOIN medicines m ON b.generic_id = m.id
            WHERE b.brand_name ILIKE %s OR m.generic_name ILIKE %s
        """
        search_term = f"%{query}%"
        cur.execute(sql, (search_term, search_term))

    results = cur.fetchall()

    output = []
    for row in results:
        savings = row['brand_price'] - row['generic_price']
        savings_percent = (savings / row['brand_price']) * 100 if row['brand_price'] > 0 else 0

        output.append({
            'brand_name': row['brand_name'],
            'generic_name': row['generic_name'],
            'salt': row['salt'],
            'dosage': row['dosage'],
            'form': row['form'],
            'brand_price': row['brand_price'],
            'generic_price': row['generic_price'],
            'savings_percent': round(savings_percent, 1)
        })

    cur.close()
    conn.close()

    return jsonify(output)


# 🏪 STORES API
@app.route('/api/stores', methods=['GET'])
def get_stores():
    pincode = request.args.get('pincode', '').strip()
    lat = request.args.get('lat', '').strip()
    lng = request.args.get('lng', '').strip()

    conn = get_db_connection()
    cur = conn.cursor()

    param_marker = '?' if isinstance(conn, sqlite3.Connection) else '%s'

    if pincode:
        cur.execute(f"SELECT * FROM stores WHERE pincode = {param_marker}", (pincode,))
        results = cur.fetchall()

    elif lat and lng:
        cur.execute("SELECT * FROM stores")
        results = cur.fetchall()

        user_lat = float(lat)
        user_lng = float(lng)

        output = []
        for row in results:
            d_lat = user_lat - row['lat']
            d_lng = user_lng - row['lng']
            distance = ((d_lat * 111)**2 + (d_lng * 85)**2)**0.5

            store = dict(row)
            store['distance'] = distance
            output.append(store)

        output.sort(key=lambda x: x['distance'])

        cur.close()
        conn.close()

        return jsonify(output[:5])

    else:
        cur.execute("SELECT * FROM stores LIMIT 10")
        results = cur.fetchall()

    output = [dict(row) for row in results]

    cur.close()
    conn.close()

    return jsonify(output)


# 🌐 SERVE FRONTEND
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


# ▶️ RUN (LOCAL ONLY)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/search', methods=['GET'])
def search_medicine():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fuzzy search on brand name or generic name
    # We join brands with medicines to show comparison
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
    results = cur.execute(sql, (search_term, search_term)).fetchall()
    
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
    
    conn.close()
    return jsonify(output)

@app.route('/api/stores', methods=['GET'])
def get_stores():
    pincode = request.args.get('pincode', '').strip()
    lat = request.args.get('lat', '').strip()
    lng = request.args.get('lng', '').strip()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if pincode:
        results = cur.execute("SELECT * FROM stores WHERE pincode = ?", (pincode,)).fetchall()
    elif lat and lng:
        # Simple distance calculation (Euclidean approximation for local search)
        # In a real app, use Haversine or a spatial extension like SpatiaLite
        results = cur.execute("SELECT * FROM stores").fetchall()
        user_lat = float(lat)
        user_lng = float(lng)
        
        output = []
        for row in results:
            d_lat = user_lat - row['lat']
            d_lng = user_lng - row['lng']
            # Approx distance in km (very rough)
            distance = ((d_lat * 111)**2 + (d_lng * 85)**2)**0.5
            store_dict = dict(row)
            store_dict['distance'] = distance
            output.append(store_dict)
            
        # Sort by distance
        output.sort(key=lambda x: x['distance'])
        conn.close()
        return jsonify(output[:5]) # Return nearest 5
    else:
        results = cur.execute("SELECT * FROM stores LIMIT 10").fetchall()
        
    output = [dict(row) for row in results]
    conn.close()
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

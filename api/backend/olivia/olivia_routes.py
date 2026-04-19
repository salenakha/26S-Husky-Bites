from flask import Blueprint, jsonify, request
from backend.db_connection import db

olivia = Blueprint('olivia', __name__)

# add one route for each of 6 user stories below

# 1.1 GET student recommendations

@olivia.route('/restaurants/recommendations', methods=['GET'])
def get_student_recommendations():
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT DISTINCT r.name, r.location, r.dist_from_campus, rv.rating, rv.review_text
        FROM Restaurant r
        JOIN Review rv ON r.restaurant_id = rv.restaurant_id
        JOIN User u ON rv.user_id = u.user_id
        WHERE u.role = 'student'
        AND rv.review_status = 'approved'
        AND r.status = 'open'
        ORDER BY rv.rating DESC, r.dist_from_campus ASC
    ''')
    return jsonify(cursor.fetchall())

# 1.2 GET filtered restaurants

@olivia.route('/restaurants/filter', methods=['GET'])
def filter_restaurants():
    cuisine = request.args.get('cuisine')
    price = request.args.get('price_range')
    atmosphere = request.args.get('atmosphere')
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT r.name, c.cuisine_name, r.location, r.price_range, r.atmosphere, r.avg_rating
        FROM Restaurant r
        JOIN Cuisine c ON r.cuisine_id = c.cuisine_id
        WHERE c.cuisine_name = %s
        AND r.price_range <= %s
        AND r.atmosphere = %s
        AND r.status = 'open'
        ORDER BY r.avg_rating DESC
    ''', (cuisine, price, atmosphere))
    return jsonify(cursor.fetchall())

# 1.3 GET local/student favorites

@olivia.route('/restaurants/favorites-feed', methods=['GET'])
def get_local_favorites():
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT r.name, r.location, r.local_fav_tag, r.student_fav_tag, r.avg_rating
        FROM Restaurant r
        WHERE (r.local_fav_tag IS NOT NULL OR r.student_fav_tag IS NOT NULL)
        AND r.status = 'open'
        ORDER BY r.avg_rating DESC
    ''')
    return jsonify(cursor.fetchall())

# 1.4 GET wait times

@olivia.route('/restaurants/wait-times', methods=['GET'])
def get_wait_times():
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT r.name, r.location, r.dist_from_campus, 
               w.estimated_wait_time, w.wait_minutes, w.day_type, w.recorded_at
        FROM Restaurant r
        JOIN Wait_Time_Record w ON r.restaurant_id = w.restaurant_id
        WHERE r.dist_from_campus <= 1.0
        AND r.status = 'open'
        ORDER BY w.wait_minutes ASC, r.dist_from_campus ASC
    ''')
    return jsonify(cursor.fetchall())


# 1.5 GET compare restaurants

@olivia.route('/restaurants/compare', methods=['GET'])
def compare_restaurants():
    cursor = db.get_db().cursor()
    cursor.execute('''
        SELECT r.name, r.location, r.avg_rating, r.price_range, r.dist_from_campus
        FROM Restaurant r
        WHERE r.status = 'open'
        ORDER BY r.avg_rating DESC, r.price_range ASC, r.dist_from_campus ASC
    ''')
    return jsonify(cursor.fetchall())

# 1.6 POST save to favorites

@olivia.route('/favorites', methods=['POST'])
def save_favorite():
    data = request.json
    cursor = db.get_db().cursor()
    cursor.execute('''
        INSERT INTO Favorite (user_id, restaurant_id, saved_date)
        VALUES (%s, %s, CURDATE())
    ''', (data['user_id'], data['restaurant_id']))
    db.get_db().commit()
    return jsonify({'message': 'Restaurant saved to favorites'}), 201

# then register blueprint in rest_entry.py
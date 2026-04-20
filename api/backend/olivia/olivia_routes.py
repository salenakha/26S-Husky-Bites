from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# blueprint setup mirrors the ngos blueprint pattern from ngo_routes.py
olivia = Blueprint('olivia', __name__)


# 1.1 GET student recommendations
@olivia.route('/restaurants/recommendations', methods=['GET'])
def get_student_recommendations():
    # dictionary=True returns rows as dicts instead of tuples, same as ngo_routes
    cursor = get_db().cursor(dictionary=True)
    try:
        # logger pattern copied from ngo_routes.py
        current_app.logger.info('GET /olivia/restaurants/recommendations')
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
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        # cursor.close() in finally block ensures cleanup even if an exception is raised
        cursor.close()


# 1.2 GET filtered restaurants
@olivia.route('/restaurants/filter', methods=['GET'])
def filter_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /olivia/restaurants/filter')
        cuisine = request.args.get('cuisine')
        price = request.args.get('price_range')
        atmosphere = request.args.get('atmosphere')

        # where 1=1 from ngo_routes.py lets us append and clauses cleanly
        query = '''
            SELECT r.name, c.cuisine_name, r.location, r.price_range, r.atmosphere, r.avg_rating
            FROM Restaurant r
            JOIN Cuisine c ON r.cuisine_id = c.cuisine_id
            WHERE 1=1
            AND r.status = 'open'
        '''
        params = []

        if cuisine:
            query += ' AND c.cuisine_name = %s'
            params.append(cuisine)
        if price:
            query += ' AND r.price_range <= %s'
            params.append(price)
        if atmosphere:
            query += ' AND r.atmosphere = %s'
            params.append(atmosphere)

        query += ' ORDER BY r.avg_rating DESC'
        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 1.3 GET local/student favorites feed
@olivia.route('/restaurants/favorites-feed', methods=['GET'])
def get_local_favorites():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /olivia/restaurants/favorites-feed')
        cursor.execute('''
            SELECT r.name, r.location, r.local_fav_tag, r.student_fav_tag, r.avg_rating
            FROM Restaurant r
            WHERE (r.local_fav_tag IS NOT NULL OR r.student_fav_tag IS NOT NULL)
            AND r.status = 'open'
            ORDER BY r.avg_rating DESC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 1.4 GET wait times at nearby restaurants
@olivia.route('/restaurants/wait-times', methods=['GET'])
def get_wait_times():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /olivia/restaurants/wait-times')
        cursor.execute('''
            SELECT r.name, r.location, r.dist_from_campus,
                   w.estimated_wait_time, w.wait_minutes, w.day_type, w.recorded_at
            FROM Restaurant r
            JOIN Wait_Time_Record w ON r.restaurant_id = w.restaurant_id
            WHERE r.dist_from_campus <= 1.0
            AND r.status = 'open'
            ORDER BY w.wait_minutes ASC, r.dist_from_campus ASC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 1.5 GET compare restaurants
@olivia.route('/restaurants/compare', methods=['GET'])
def compare_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /olivia/restaurants/compare')
        cursor.execute('''
            SELECT r.name, r.location, r.avg_rating, r.price_range, r.dist_from_campus
            FROM Restaurant r
            WHERE r.status = 'open'
            ORDER BY r.avg_rating DESC, r.price_range ASC, r.dist_from_campus ASC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# 1.6 POST save restaurant to favorites
@olivia.route('/favorites', methods=['POST'])
def save_favorite():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /olivia/favorites')
        # request.get_json() mirrors the pattern used in create_ngo in ngo_routes.py
        data = request.get_json()

        if not data or 'user_id' not in data or 'restaurant_id' not in data:
            return jsonify({'error': 'Missing required fields: user_id and restaurant_id'}), 400

        cursor.execute('''
            INSERT INTO Favorite (user_id, restaurant_id, saved_date)
            VALUES (%s, %s, CURDATE())
        ''', (data['user_id'], data['restaurant_id']))
        # cursor.lastrowid mirrors the create_ngo pattern for returning the new record's id
        get_db().commit()
        return jsonify({'message': 'Restaurant saved to favorites', 'favorite_id': cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
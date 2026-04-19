########################################################
# olivia_routes.py
# Blueprint: Olivia — International Student (Persona 1)
#
# Routes:
#   GET    /olivia/restaurants                              [Olivia-1,2,5]
#   GET    /olivia/restaurants/favorites                    [Olivia-3]
#   GET    /olivia/restaurants/<id>                         [Olivia-5]
#   GET    /olivia/restaurants/<id>/wait-time               [Olivia-4]
#   GET    /olivia/students/<id>/favorites                  [Olivia-6]
#   POST   /olivia/students/<id>/favorites                  [Olivia-6]
#   DELETE /olivia/students/<id>/favorites/<restaurant_id>  [Olivia-6]
########################################################

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Blueprint object — registered in rest_entry.py as url_prefix='/olivia'
olivia = Blueprint('olivia', __name__)


# ── [Olivia-1, Olivia-2, Olivia-5] GET /olivia/restaurants ───────────────────
# Return all open restaurants. Supports optional filters:
#   ?cuisine=Vietnamese  ?max_price=2  ?atmosphere=casual
@olivia.route('/restaurants', methods=['GET'])
def get_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /olivia/restaurants')

        cuisine    = request.args.get('cuisine',    None)
        max_price  = request.args.get('max_price',  None)
        atmosphere = request.args.get('atmosphere', None)

        # WHERE 1=1 lets us append AND clauses cleanly without
        # special-casing the first filter — same pattern as ngo_routes.py
        query = '''
            SELECT  r.restaurant_id,
                    r.name,
                    r.location,
                    r.status,
                    c.cuisine_name,
                    r.price_range,
                    r.avg_rating,
                    r.dist_from_campus,
                    r.atmosphere,
                    r.halal_certified,
                    r.local_fav_tag,
                    r.student_fav_tag,
                    r.last_updated
            FROM    Restaurant r
            JOIN    Cuisine c ON c.cuisine_id = r.cuisine_id
            WHERE   1=1
            AND     r.status = 'open'
        '''
        params = []

        if cuisine:
            query += ' AND c.cuisine_name = %s'
            params.append(cuisine)
        if max_price:
            query += ' AND r.price_range <= %s'
            params.append(float(max_price))
        if atmosphere:
            query += ' AND r.atmosphere = %s'
            params.append(atmosphere)

        query += ' ORDER BY r.avg_rating DESC'

        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurants: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# ── [Olivia-3] GET /olivia/restaurants/favorites ─────────────────────────────
# Return restaurants tagged as local or student favorites.
# MUST be registered BEFORE /restaurants/<id> so Flask does not
# treat the literal string "favorites" as an integer restaurant_id.
@olivia.route('/restaurants/favorites', methods=['GET'])
def get_favorite_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /olivia/restaurants/favorites')
        cursor.execute('''
            SELECT  r.restaurant_id,
                    r.name,
                    r.location,
                    r.avg_rating,
                    r.price_range,
                    r.dist_from_campus,
                    r.local_fav_tag,
                    r.student_fav_tag,
                    c.cuisine_name
            FROM    Restaurant r
            JOIN    Cuisine c ON c.cuisine_id = r.cuisine_id
            WHERE   r.status = 'open'
              AND   (r.local_fav_tag IS NOT NULL OR r.student_fav_tag IS NOT NULL)
            ORDER BY r.avg_rating DESC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_favorite_restaurants: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# ── [Olivia-5] GET /olivia/restaurants/<id> ──────────────────────────────────
# Return full detail for a single restaurant including neighborhood
@olivia.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /olivia/restaurants/{restaurant_id}')
        cursor.execute('''
            SELECT  r.*,
                    c.cuisine_name,
                    n.neighborhood_name
            FROM    Restaurant r
            JOIN    Cuisine      c ON c.cuisine_id      = r.cuisine_id
            JOIN    Neighborhood n ON n.neighborhood_id = r.neighborhood_id
            WHERE   r.restaurant_id = %s
        ''', (restaurant_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Restaurant not found'}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# ── [Olivia-4] GET /olivia/restaurants/<id>/wait-time ────────────────────────
# Return the most recent wait time record for a specific restaurant
@olivia.route('/restaurants/<int:restaurant_id>/wait-time', methods=['GET'])
def get_wait_time(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /olivia/restaurants/{restaurant_id}/wait-time')
        cursor.execute('''
            SELECT  wait_time_id,
                    estimated_wait_time,
                    wait_minutes,
                    day_type,
                    recorded_at,
                    updated_time
            FROM    Wait_Time_Record
            WHERE   restaurant_id = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        ''', (restaurant_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'No wait time data found'}), 404
        return jsonify(result), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_wait_time: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# ── [Olivia-6] GET /olivia/students/<id>/favorites ───────────────────────────
# Return the saved favorites list for a specific student
@olivia.route('/students/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /olivia/students/{user_id}/favorites')
        cursor.execute('''
            SELECT  f.favorite_id,
                    f.saved_date,
                    r.restaurant_id,
                    r.name,
                    r.location,
                    r.avg_rating,
                    r.price_range,
                    r.dist_from_campus,
                    c.cuisine_name
            FROM    Favorite f
            JOIN    Restaurant r ON r.restaurant_id = f.restaurant_id
            JOIN    Cuisine    c ON c.cuisine_id    = r.cuisine_id
            WHERE   f.user_id = %s
            ORDER BY f.saved_date DESC
        ''', (user_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_favorites: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# ── [Olivia-6] POST /olivia/students/<id>/favorites ──────────────────────────
# Save a restaurant to a student's favorites list
# Expected JSON body: { "restaurant_id": 7 }
@olivia.route('/students/<int:user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'POST /olivia/students/{user_id}/favorites')
        data = request.get_json()

        if not data or 'restaurant_id' not in data:
            return jsonify({'error': 'restaurant_id is required'}), 400

        cursor.execute('''
            INSERT INTO Favorite (user_id, restaurant_id, saved_date)
            VALUES (%s, %s, CURDATE())
        ''', (user_id, data['restaurant_id']))
        get_db().commit()
        return jsonify({'message': 'Saved to favorites',
                        'favorite_id': cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in add_favorite: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# ── [Olivia-6] DELETE /olivia/students/<id>/favorites/<restaurant_id> ────────
# Remove a specific restaurant from a student's favorites list
@olivia.route('/students/<int:user_id>/favorites/<int:restaurant_id>', methods=['DELETE'])
def remove_favorite(user_id, restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /olivia/students/{user_id}/favorites/{restaurant_id}')
        cursor.execute(
            'DELETE FROM Favorite WHERE user_id = %s AND restaurant_id = %s',
            (user_id, restaurant_id)
        )
        get_db().commit()
        return jsonify({'message': 'Removed from favorites'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in remove_favorite: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

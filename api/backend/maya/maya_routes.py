from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

maya = Blueprint('maya', __name__)


# [Maya-1] GET /maya/restaurants/wait-times
# Return wait times for all nearby open restaurants ordered by wait_minutes ASC
@maya.route('/restaurants/wait-times', methods=['GET'])
def get_all_wait_times():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /maya/restaurants/wait-times')
        cursor.execute('''
            SELECT  r.restaurant_id,
                    r.name,
                    r.location,
                    r.dist_from_campus,
                    w.wait_minutes,
                    w.estimated_wait_time,
                    w.day_type,
                    w.recorded_at
            FROM    Restaurant r
            JOIN    Wait_Time_Record w ON w.restaurant_id = r.restaurant_id
            WHERE   r.status = 'open'
              AND   r.dist_from_campus <= 1.0
              AND   w.recorded_at = (
                        SELECT MAX(w2.recorded_at)
                        FROM   Wait_Time_Record w2
                        WHERE  w2.restaurant_id = r.restaurant_id
                    )
            ORDER BY w.wait_minutes ASC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_wait_times: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-2] GET /maya/restaurants/allergen-filter
# Return open restaurants tagged with a given dietary tag
# Required query param: ?tag=nut-free
@maya.route('/restaurants/allergen-filter', methods=['GET'])
def get_allergen_filter():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /maya/restaurants/allergen-filter')
        tag = request.args.get('tag', None)

        if not tag:
            return jsonify({'error': '?tag= query param is required. Example: ?tag=nut-free'}), 400

        cursor.execute('''
            SELECT  r.restaurant_id,
                    r.name,
                    r.location,
                    r.avg_rating,
                    r.price_range,
                    r.dist_from_campus,
                    r.halal_certified,
                    dt.dietary_tag_name,
                    dt.dietary_tag_category
            FROM    Restaurant r
            JOIN    Restaurant_Dietary_Tag rdt ON rdt.restaurant_id = r.restaurant_id
            JOIN    Dietary_Tag dt             ON dt.dietary_tag_id = rdt.dietary_tag_id
            WHERE   dt.dietary_tag_name = %s
              AND   r.status = 'open'
            ORDER BY r.avg_rating DESC
        ''', (tag,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_allergen_filter: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-3] GET /maya/restaurants/halal
# Return open halal-certified restaurants ordered by distance from campus
@maya.route('/restaurants/halal', methods=['GET'])
def get_halal_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /maya/restaurants/halal')
        cursor.execute('''
            SELECT  r.restaurant_id,
                    r.name,
                    r.location,
                    r.dist_from_campus,
                    r.avg_rating,
                    r.price_range,
                    r.hours,
                    r.halal_certified
            FROM    Restaurant r
            WHERE   r.halal_certified = TRUE
              AND   r.status = 'open'
            ORDER BY r.dist_from_campus ASC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_halal_restaurants: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-4] GET /maya/restaurants/between-class
# Return top 5 fastest meal options ranked by walk time + wait time
# dist_from_campus in miles x 12 = estimated walking minutes
# Optional: ?halal_only=true
@maya.route('/restaurants/between-class', methods=['GET'])
def get_between_class():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /maya/restaurants/between-class')
        halal_only = request.args.get('halal_only', 'false').lower() == 'true'

        # WHERE 1=1 lets us append AND clauses cleanly — same pattern as ngo_routes.py
        query = '''
            SELECT  r.restaurant_id,
                    r.name,
                    r.location,
                    r.dist_from_campus,
                    w.wait_minutes,
                    ROUND((r.dist_from_campus * 12) + w.wait_minutes, 1) AS estimated_total_minutes,
                    r.halal_certified,
                    r.avg_rating
            FROM    Restaurant r
            JOIN    Wait_Time_Record w ON w.restaurant_id = r.restaurant_id
            WHERE   1=1
            AND     r.status = 'open'
            AND     w.recorded_at = (
                        SELECT MAX(w2.recorded_at)
                        FROM   Wait_Time_Record w2
                        WHERE  w2.restaurant_id = r.restaurant_id
                    )
        '''
        params = []
        if halal_only:
            query += ' AND r.halal_certified = TRUE'

        query += ' ORDER BY estimated_total_minutes ASC LIMIT 5'
        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_between_class: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-5] GET /maya/leaderboard
# Return top-ranked restaurants from Leaderboard_Entry joined with Restaurant
@maya.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /maya/leaderboard')
        cursor.execute('''
            SELECT  le.entry_id,
                    le.rank_num,
                    le.score_avg,
                    r.restaurant_id,
                    r.name,
                    r.location,
                    r.dist_from_campus,
                    r.avg_rating,
                    r.halal_certified,
                    r.price_range
            FROM    Leaderboard_Entry le
            JOIN    Restaurant r ON r.restaurant_id = le.restaurant_id
            WHERE   r.status = 'open'
            ORDER BY le.rank_num ASC
            LIMIT 10
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_leaderboard: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-6] POST /maya/reviews
# Submit a new quick review with a numeric rating (1-5) and short text
# Required JSON body: { "user_id": 42, "restaurant_id": 7, "rating": 4.5 }
@maya.route('/reviews', methods=['POST'])
def submit_review():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /maya/reviews')
        data = request.get_json()

        required = ['user_id', 'restaurant_id', 'rating']
        for field in required:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        cursor.execute('''
            INSERT INTO Review
                (user_id, restaurant_id, rating, review_text, review_date, review_status)
            VALUES (%s, %s, %s, %s, CURDATE(), 'approved')
        ''', (
            data['user_id'],
            data['restaurant_id'],
            data['rating'],
            data.get('review_text', ''),
        ))
        get_db().commit()
        return jsonify({'message': 'Review submitted',
                        'review_id': cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in submit_review: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-6] PUT /maya/reviews/<id>
# Update an existing review's rating or review_text
@maya.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /maya/reviews/{review_id}')
        data = request.get_json()

        set_parts = []
        params    = []

        if 'rating' in data:
            set_parts.append('rating = %s')
            params.append(data['rating'])
        if 'review_text' in data:
            set_parts.append('review_text = %s')
            params.append(data['review_text'])

        if not set_parts:
            return jsonify({'error': 'Provide rating or review_text to update'}), 400

        params.append(review_id)
        cursor.execute(
            f'UPDATE Review SET {", ".join(set_parts)} WHERE review_id = %s',
            tuple(params)
        )
        get_db().commit()
        return jsonify({'message': 'Review updated'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_review: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Maya-6] DELETE /maya/reviews/<id>
# Permanently delete a review that Maya submitted
@maya.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /maya/reviews/{review_id}')
        cursor.execute('DELETE FROM Review WHERE review_id = %s', (review_id,))
        get_db().commit()
        return jsonify({'message': 'Review deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_review: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

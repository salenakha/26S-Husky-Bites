from flask import Blueprint, request, jsonify, current_app
from backend.db_connection import get_db

maya = Blueprint('maya', __name__)


# GET /maya/restaurants/<id>/wait_time
@maya.route('/restaurants/<int:id>/wait_time', methods=['GET'])
def get_wait_time(id):
    current_app.logger.info(f'GET /maya/restaurants/{id}/wait_time')
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT r.name, r.location, w.estimated_wait_time, w.wait_minutes, w.day_type, w.recorded_at
        FROM Restaurant r
        JOIN Wait_Time_Record w ON r.restaurant_id = w.restaurant_id
        WHERE r.restaurant_id = %s
        ORDER BY w.recorded_at DESC
        LIMIT 1
    ''', (id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(row), 200
 
 
# GET /maya/restaurants/allergen-filter
@maya.route('/restaurants/allergen-filter', methods=['GET'])
def get_allergen_filter():
    current_app.logger.info('GET /maya/restaurants/allergen-filter')
    tag = request.args.get('tag', 'nut-free')
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT r.name, r.location, r.avg_rating, r.price_range,
               dt.dietary_tag_name, dt.dietary_tag_category
        FROM Restaurant r
        JOIN Restaurant_Dietary_Tag rdt ON r.restaurant_id = rdt.restaurant_id
        JOIN Dietary_Tag dt ON rdt.dietary_tag_id = dt.dietary_tag_id
        WHERE dt.dietary_tag_name = %s AND r.status = 'open'
        ORDER BY r.avg_rating DESC
    ''', (tag,))
    rows = cursor.fetchall()
    return jsonify(rows), 200
 
 
# GET /maya/restaurants/halal
@maya.route('/restaurants/halal', methods=['GET'])
def get_halal():
    current_app.logger.info('GET /maya/restaurants/halal')
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT name, location, dist_from_campus, halal_certified, avg_rating, price_range, hours
        FROM Restaurant
        WHERE halal_certified = TRUE AND status = 'open'
        ORDER BY dist_from_campus ASC
    ''')
    rows = cursor.fetchall()
    return jsonify(rows), 200
 
 
# GET /maya/restaurants/between-class
@maya.route('/restaurants/between-class', methods=['GET'])
def get_between_class():
    current_app.logger.info('GET /maya/restaurants/between-class')
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT r.name, r.location, r.dist_from_campus, w.wait_minutes,
               (r.dist_from_campus * 12 + w.wait_minutes) AS estimated_total_minutes,
               r.halal_certified, r.avg_rating
        FROM Restaurant r
        JOIN Wait_Time_Record w ON r.restaurant_id = w.restaurant_id
        WHERE r.status = 'open'
        AND w.recorded_at = (
            SELECT MAX(w2.recorded_at)
            FROM Wait_Time_Record w2
            WHERE w2.restaurant_id = r.restaurant_id
        )
        ORDER BY estimated_total_minutes ASC
        LIMIT 5
    ''')
    rows = cursor.fetchall()
    return jsonify(rows), 200
 
 
# GET /maya/leaderboard
@maya.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    current_app.logger.info('GET /maya/leaderboard')
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT le.rank_num, r.name, r.location, r.dist_from_campus,
               le.score_avg, r.avg_rating, r.halal_certified, r.price_range
        FROM Leaderboard_Entry le
        JOIN Restaurant r ON le.restaurant_id = r.restaurant_id
        WHERE r.status = 'open'
        ORDER BY le.rank_num ASC
    ''')
    rows = cursor.fetchall()
    return jsonify(rows), 200
 
 
# POST /maya/reviews
@maya.route('/reviews', methods=['POST'])
def submit_review():
    current_app.logger.info('POST /maya/reviews')
    data = request.json
    cursor = get_db().cursor()
    cursor.execute('''
        INSERT INTO Review (user_id, restaurant_id, rating, review_text, review_date, review_status)
        VALUES (%s, %s, %s, %s, CURDATE(), 'approved')
    ''', (data['user_id'], data['restaurant_id'], data['rating'], data['review_text']))
    get_db().commit()
    return jsonify({'message': 'Review submitted'}), 201
 
 
# PUT /maya/reviews/<id>
@maya.route('/reviews/<int:id>', methods=['PUT'])
def update_review(id):
    current_app.logger.info(f'PUT /maya/reviews/{id}')
    data = request.json
    cursor = get_db().cursor()
    cursor.execute('''
        UPDATE Review SET rating = %s, review_text = %s WHERE review_id = %s
    ''', (data['rating'], data['review_text'], id))
    get_db().commit()
    return jsonify({'message': 'Review updated'}), 200
 
 
# DELETE /maya/reviews/<id>
@maya.route('/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    current_app.logger.info(f'DELETE /maya/reviews/{id}')
    cursor = get_db().cursor()
    cursor.execute('DELETE FROM Review WHERE review_id = %s', (id,))
    get_db().commit()
    return jsonify({'message': 'Review deleted'}), 200
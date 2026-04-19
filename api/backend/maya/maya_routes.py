########################################################
# maya_routes.py
# Blueprint: Maya — Pre-Med Student (Persona 4)
#
# Routes:
#   GET    /maya/restaurants/wait-times        [Maya-1]
#   GET    /maya/restaurants/allergen-filter   [Maya-2]
#   GET    /maya/restaurants/halal             [Maya-3]
#   GET    /maya/restaurants/between-class     [Maya-4]
#   GET    /maya/leaderboard                   [Maya-5]
#   POST   /maya/reviews                       [Maya-6]
#   PUT    /maya/reviews/<id>                  [Maya-6]
#   DELETE /maya/reviews/<id>                  [Maya-6]
########################################################

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

# Blueprint object — registered in rest_entry.py as url_prefix='/maya'
maya = Blueprint('maya', __name__)


# ── [Maya-1] GET /maya/restaurants/wait-times ────────────────────────────────
# Return wait times for all nearby open restaurants ordered by wait_minutes ASC
# so Maya can see the quickest option at a glance before class.
@maya.route('/restaurants/wait-times', methods=['GET'])
def get_all_wait_times():
    current_app.logger.info('GET /maya/restaurants/wait-times')
    # Correlated subquery ensures we only pull the most recent record per restaurant
    query = '''
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
    '''
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Maya-2] GET /maya/restaurants/allergen-filter ───────────────────────────
# Return open restaurants tagged with a given dietary tag (e.g. nut-free)
# Required query param: ?tag=nut-free
@maya.route('/restaurants/allergen-filter', methods=['GET'])
def get_allergen_filter():
    current_app.logger.info('GET /maya/restaurants/allergen-filter')
    tag = request.args.get('tag', None)

    # tag is required — return 400 if missing
    if not tag:
        return make_response(jsonify({'error': '?tag= query param is required. '
                                               'Example: ?tag=nut-free'}), 400)
    query = '''
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
    '''
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query, (tag,))
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Maya-3] GET /maya/restaurants/halal ─────────────────────────────────────
# Return open halal-certified restaurants ordered by distance from campus
# so Maya doesn't have to call ahead or guess about certification.
@maya.route('/restaurants/halal', methods=['GET'])
def get_halal_restaurants():
    current_app.logger.info('GET /maya/restaurants/halal')
    query = '''
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
    '''
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Maya-4] GET /maya/restaurants/between-class ─────────────────────────────
# Return top 5 fastest meal options ranked by walk time + wait time combined.
# dist_from_campus is in miles; multiplying by 12 estimates walking minutes
# (assumes roughly 5 mph walking pace → 12 min/mile).
# Optional: ?halal_only=true to restrict to halal-certified restaurants
@maya.route('/restaurants/between-class', methods=['GET'])
def get_between_class():
    current_app.logger.info('GET /maya/restaurants/between-class')
    halal_only = request.args.get('halal_only', 'false').lower() == 'true'

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
        WHERE   r.status = 'open'
          AND   w.recorded_at = (
                    SELECT MAX(w2.recorded_at)
                    FROM   Wait_Time_Record w2
                    WHERE  w2.restaurant_id = r.restaurant_id
                )
    '''
    params = []

    # Only add the halal filter if the caller explicitly asked for it
    if halal_only:
        query += ' AND r.halal_certified = TRUE'

    query += ' ORDER BY estimated_total_minutes ASC LIMIT 5'

    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Maya-5] GET /maya/leaderboard ───────────────────────────────────────────
# Return top-ranked restaurants from Leaderboard_Entry joined with Restaurant
# so Maya knows what's worth ordering without digging through dozens of reviews.
@maya.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    current_app.logger.info('GET /maya/leaderboard')
    query = '''
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
    '''
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Maya-6] POST /maya/reviews ──────────────────────────────────────────────
# Submit a new quick review with a numeric rating (1-5) and short text.
# Expected JSON body: { "user_id": 42, "restaurant_id": 7,
#                       "rating": 4.5, "review_text": "Great wrap!" }
@maya.route('/reviews', methods=['POST'])
def submit_review():
    current_app.logger.info('POST /maya/reviews')
    data = request.json

    # Validate that required fields are present before hitting the DB
    required = ['user_id', 'restaurant_id', 'rating']
    for field in required:
        if field not in data:
            return make_response(jsonify({'error': f'{field} is required'}), 400)

    query = '''
        INSERT INTO Review
            (user_id, restaurant_id, rating, review_text, review_date, review_status)
        VALUES (%s, %s, %s, %s, CURDATE(), 'approved')
    '''
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query, (
        data['user_id'],
        data['restaurant_id'],
        data['rating'],
        data.get('review_text', ''),   # review_text is optional
    ))
    get_db().commit()
    return make_response(jsonify({'message': 'Review submitted',
                                  'review_id': cursor.lastrowid}), 201)


# ── [Maya-6] PUT /maya/reviews/<id> ──────────────────────────────────────────
# Update an existing review's rating or review_text.
# Only updates the fields that are actually sent in the body.
@maya.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    current_app.logger.info(f'PUT /maya/reviews/{review_id}')
    data = request.json

    # Build the SET clause dynamically so we only touch provided fields
    set_parts = []
    params    = []

    if 'rating' in data:
        set_parts.append('rating = %s')
        params.append(data['rating'])
    if 'review_text' in data:
        set_parts.append('review_text = %s')
        params.append(data['review_text'])

    # Nothing to update — return early with a helpful message
    if not set_parts:
        return make_response(jsonify({'error': 'Provide rating or review_text to update'}), 400)

    # Append the WHERE clause param last
    params.append(review_id)
    query = f'UPDATE Review SET {", ".join(set_parts)} WHERE review_id = %s'

    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    get_db().commit()
    return make_response(jsonify({'message': 'Review updated'}), 200)


# ── [Maya-6] DELETE /maya/reviews/<id> ───────────────────────────────────────
# Permanently delete a review that Maya submitted
@maya.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    current_app.logger.info(f'DELETE /maya/reviews/{review_id}')
    query = 'DELETE FROM Review WHERE review_id = %s'
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query, (review_id,))
    get_db().commit()
    return make_response(jsonify({'message': 'Review deleted'}), 200)

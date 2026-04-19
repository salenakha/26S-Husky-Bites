########################################################
# jordan.py
# Blueprint: Jordan Patel — System Admin (Persona 2)
#
# Fixed:
#   - import changed from `db` to `get_db` (matches template)
#   - db.get_db().cursor() → get_db().cursor(dictionary=True)
#   - db.get_db().commit() → get_db().commit()
########################################################

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

# Blueprint object — registered in rest_entry.py as url_prefix='/jordan'
jordan = Blueprint('jordan', __name__)


# ── [Jordan-1] GET /jordan/restaurants ───────────────────────────────────────
# Return all restaurants with name, location, status, cuisine, last_updated
@jordan.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    current_app.logger.info('GET /jordan/restaurants')
    # dictionary=True means rows come back as dicts, not tuples
    cursor = get_db().cursor(dictionary=True)
    query = '''
        SELECT r.restaurant_id, r.name, r.location, r.status,
               c.cuisine_name, r.last_updated, r.halal_certified,
               r.price_range, r.avg_rating, r.dist_from_campus
        FROM Restaurant r
        JOIN Cuisine c ON r.cuisine_id = c.cuisine_id
        ORDER BY r.name ASC
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Jordan-1] POST /jordan/restaurants ──────────────────────────────────────
# Add a new restaurant record
@jordan.route('/restaurants', methods=['POST'])
def add_restaurant():
    current_app.logger.info('POST /jordan/restaurants')
    data = request.json
    cursor = get_db().cursor(dictionary=True)
    query = '''
        INSERT INTO Restaurant (cuisine_id, neighborhood_id, name, location,
                                status, hours, halal_certified, price_range,
                                dist_from_campus, atmosphere, dietary_options,
                                working_hours, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
    '''
    cursor.execute(query, (
        data.get('cuisine_id'),
        data.get('neighborhood_id'),
        data.get('name'),
        data.get('location'),
        data.get('status', 'open'),
        data.get('hours'),
        data.get('halal_certified', False),
        data.get('price_range'),
        data.get('dist_from_campus'),
        data.get('atmosphere'),
        data.get('dietary_options'),
        data.get('working_hours')
    ))
    # Commit uses get_db() directly — no db object
    get_db().commit()
    return make_response(jsonify({'message': 'Restaurant added successfully',
                                  'restaurant_id': cursor.lastrowid}), 201)


# ── [Jordan-2] GET /jordan/restaurants/<id> ──────────────────────────────────
# Return full detail for a single restaurant
@jordan.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    current_app.logger.info(f'GET /jordan/restaurants/{restaurant_id}')
    cursor = get_db().cursor(dictionary=True)
    query = '''
        SELECT r.*, c.cuisine_name, n.neighborhood_name
        FROM Restaurant r
        JOIN Cuisine c ON r.cuisine_id = c.cuisine_id
        JOIN Neighborhood n ON r.neighborhood_id = n.neighborhood_id
        WHERE r.restaurant_id = %s
    '''
    cursor.execute(query, (restaurant_id,))
    result = cursor.fetchone()
    if not result:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    return make_response(jsonify(result), 200)


# ── [Jordan-2] PUT /jordan/restaurants/<id> ──────────────────────────────────
# Update restaurant info: location, hours, dietary_options, halal_certified
@jordan.route('/restaurants/<int:restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    current_app.logger.info(f'PUT /jordan/restaurants/{restaurant_id}')
    data = request.json
    cursor = get_db().cursor(dictionary=True)
    query = '''
        UPDATE Restaurant
        SET location        = %s,
            hours           = %s,
            working_hours   = %s,
            dietary_options = %s,
            halal_certified = %s,
            price_range     = %s,
            atmosphere      = %s,
            last_updated    = CURDATE()
        WHERE restaurant_id = %s
    '''
    cursor.execute(query, (
        data.get('location'),
        data.get('hours'),
        data.get('working_hours'),
        data.get('dietary_options'),
        data.get('halal_certified'),
        data.get('price_range'),
        data.get('atmosphere'),
        restaurant_id
    ))
    get_db().commit()
    return make_response(jsonify({'message': 'Restaurant updated successfully'}), 200)


# ── [Jordan-3] DELETE /jordan/restaurants/<id> ───────────────────────────────
# Soft-delete a restaurant (sets status = 'deleted') to preserve FK integrity
@jordan.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    current_app.logger.info(f'DELETE /jordan/restaurants/{restaurant_id}')
    cursor = get_db().cursor(dictionary=True)
    # Soft delete: update status rather than removing the row so that
    # linked Reviews, Favorites, and Wait_Time_Records are not orphaned
    query = '''
        UPDATE Restaurant
        SET status = 'deleted', last_updated = CURDATE()
        WHERE restaurant_id = %s
    '''
    cursor.execute(query, (restaurant_id,))
    get_db().commit()
    return make_response(jsonify({'message': 'Restaurant deleted successfully'}), 200)


# ── [Jordan-3, Jordan-5] PUT /jordan/restaurants/<id>/status ─────────────────
# Set restaurant status to open, closed, inactive, or deleted
@jordan.route('/restaurants/<int:restaurant_id>/status', methods=['PUT'])
def update_restaurant_status(restaurant_id):
    current_app.logger.info(f'PUT /jordan/restaurants/{restaurant_id}/status')
    data = request.json
    new_status = data.get('status')
    # Validate the value before hitting the DB
    allowed = ['open', 'closed', 'inactive', 'deleted']
    if new_status not in allowed:
        return make_response(jsonify({'error': f'Status must be one of {allowed}'}), 400)
    cursor = get_db().cursor(dictionary=True)
    query = '''
        UPDATE Restaurant
        SET status = %s, last_updated = CURDATE()
        WHERE restaurant_id = %s
    '''
    cursor.execute(query, (new_status, restaurant_id))
    get_db().commit()
    return make_response(jsonify({'message': f'Restaurant status set to {new_status}'}), 200)


# ── [Jordan-4] GET /jordan/reviews ───────────────────────────────────────────
# Return all reviews; optionally filter by ?status=approved|removed|pending
@jordan.route('/reviews', methods=['GET'])
def get_all_reviews():
    current_app.logger.info('GET /jordan/reviews')
    # Optional query param: ?status=removed
    status_filter = request.args.get('status')
    cursor = get_db().cursor(dictionary=True)
    if status_filter:
        query = '''
            SELECT rv.review_id, rv.rating, rv.review_text, rv.review_date,
                   rv.review_status, u.username, r.name AS restaurant_name
            FROM Review rv
            JOIN User u ON rv.user_id = u.user_id
            JOIN Restaurant r ON rv.restaurant_id = r.restaurant_id
            WHERE rv.review_status = %s
            ORDER BY rv.review_date DESC
        '''
        cursor.execute(query, (status_filter,))
    else:
        query = '''
            SELECT rv.review_id, rv.rating, rv.review_text, rv.review_date,
                   rv.review_status, u.username, r.name AS restaurant_name
            FROM Review rv
            JOIN User u ON rv.user_id = u.user_id
            JOIN Restaurant r ON rv.restaurant_id = r.restaurant_id
            ORDER BY rv.review_date DESC
        '''
        cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Jordan-4] PUT /jordan/reviews/<id>/status ───────────────────────────────
# Soft-flag a review by setting review_status to 'removed'
@jordan.route('/reviews/<int:review_id>/status', methods=['PUT'])
def update_review_status(review_id):
    current_app.logger.info(f'PUT /jordan/reviews/{review_id}/status')
    data = request.json
    new_status = data.get('status')
    allowed = ['approved', 'removed', 'pending']
    if new_status not in allowed:
        return make_response(jsonify({'error': f'Status must be one of {allowed}'}), 400)
    cursor = get_db().cursor(dictionary=True)
    query = 'UPDATE Review SET review_status = %s WHERE review_id = %s'
    cursor.execute(query, (new_status, review_id))
    get_db().commit()
    return make_response(jsonify({'message': f'Review status updated to {new_status}'}), 200)


# ── [Jordan-4] DELETE /jordan/reviews/<id> ───────────────────────────────────
# Permanently hard-delete a fake or inappropriate review
@jordan.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    current_app.logger.info(f'DELETE /jordan/reviews/{review_id}')
    cursor = get_db().cursor(dictionary=True)
    query = 'DELETE FROM Review WHERE review_id = %s'
    cursor.execute(query, (review_id,))
    get_db().commit()
    return make_response(jsonify({'message': 'Review permanently deleted'}), 200)


# ── [Jordan-6] GET /jordan/analytics/activity-metrics ────────────────────────
# Return Activity_Metric rows so Jordan can monitor DB growth over time
@jordan.route('/analytics/activity-metrics', methods=['GET'])
def get_activity_metrics():
    current_app.logger.info('GET /jordan/analytics/activity-metrics')
    cursor = get_db().cursor(dictionary=True)
    query = '''
        SELECT metric_id, metric_date, reviews_count,
               active_users_count, restaurant_count
        FROM Activity_Metric
        ORDER BY metric_date DESC
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)

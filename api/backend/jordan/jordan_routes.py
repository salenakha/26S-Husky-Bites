from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

jordan = Blueprint('jordan', __name__)


# [Jordan-1] GET /jordan/restaurants
# Return a list of all restaurants with name, location, status, cuisine, last_updated
@jordan.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /jordan/restaurants')
        cursor.execute('''
            SELECT r.restaurant_id, r.name, r.location, r.status,
                   c.cuisine_name, r.last_updated, r.halal_certified,
                   r.price_range, r.avg_rating, r.dist_from_campus
            FROM Restaurant r
            JOIN Cuisine c ON r.cuisine_id = c.cuisine_id
            ORDER BY r.name ASC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_restaurants: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-1] POST /jordan/restaurants
# Add a new restaurant record
@jordan.route('/restaurants', methods=['POST'])
def add_restaurant():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /jordan/restaurants')
        data = request.get_json()

        required_fields = ['name', 'location', 'cuisine_id', 'neighborhood_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        cursor.execute('''
            INSERT INTO Restaurant (cuisine_id, neighborhood_id, name, location,
                                    status, hours, halal_certified, price_range,
                                    dist_from_campus, atmosphere, dietary_options,
                                    working_hours, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
        ''', (
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
        get_db().commit()
        return jsonify({'message': 'Restaurant added successfully',
                        'restaurant_id': cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f'Database error in add_restaurant: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-2] GET /jordan/restaurants/<id>
# Return full detail for a single restaurant
@jordan.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /jordan/restaurants/{restaurant_id}')
        cursor.execute('''
            SELECT r.*, c.cuisine_name, n.neighborhood_name
            FROM Restaurant r
            JOIN Cuisine c ON r.cuisine_id = c.cuisine_id
            JOIN Neighborhood n ON r.neighborhood_id = n.neighborhood_id
            WHERE r.restaurant_id = %s
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


# [Jordan-2] PUT /jordan/restaurants/<id>
# Update restaurant info: location, hours, dietary_options, halal_certified
@jordan.route('/restaurants/<int:restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /jordan/restaurants/{restaurant_id}')
        data = request.get_json()
        cursor.execute('''
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
        ''', (
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
        return jsonify({'message': 'Restaurant updated successfully'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_restaurant: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-3] DELETE /jordan/restaurants/<id>
# Soft-delete a restaurant to preserve FK integrity
@jordan.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /jordan/restaurants/{restaurant_id}')
        cursor.execute('''
            UPDATE Restaurant
            SET status = 'deleted', last_updated = CURDATE()
            WHERE restaurant_id = %s
        ''', (restaurant_id,))
        get_db().commit()
        return jsonify({'message': 'Restaurant deleted successfully'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_restaurant: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-3, Jordan-5] PUT /jordan/restaurants/<id>/status
# Set restaurant status to open, closed, inactive, or deleted
@jordan.route('/restaurants/<int:restaurant_id>/status', methods=['PUT'])
def update_restaurant_status(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /jordan/restaurants/{restaurant_id}/status')
        data = request.get_json()
        new_status = data.get('status')

        allowed = ['open', 'closed', 'inactive', 'deleted']
        if new_status not in allowed:
            return jsonify({'error': f'Status must be one of {allowed}'}), 400

        cursor.execute('''
            UPDATE Restaurant
            SET status = %s, last_updated = CURDATE()
            WHERE restaurant_id = %s
        ''', (new_status, restaurant_id))
        get_db().commit()
        return jsonify({'message': f'Restaurant status set to {new_status}'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_restaurant_status: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-4] GET /jordan/reviews
# Return all reviews; optionally filter by ?status=approved|removed|pending
@jordan.route('/reviews', methods=['GET'])
def get_all_reviews():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /jordan/reviews')
        status_filter = request.args.get('status')

        # WHERE 1=1 lets us append AND clauses cleanly — same pattern as ngo_routes.py
        query = '''
            SELECT rv.review_id, rv.rating, rv.review_text, rv.review_date,
                   rv.review_status, u.username, r.name AS restaurant_name
            FROM Review rv
            JOIN User u ON rv.user_id = u.user_id
            JOIN Restaurant r ON rv.restaurant_id = r.restaurant_id
            WHERE 1=1
        '''
        params = []
        if status_filter:
            query += ' AND rv.review_status = %s'
            params.append(status_filter)

        query += ' ORDER BY rv.review_date DESC'
        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_reviews: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-4] PUT /jordan/reviews/<id>/status
# Soft-flag a review by setting review_status to removed
@jordan.route('/reviews/<int:review_id>/status', methods=['PUT'])
def update_review_status(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /jordan/reviews/{review_id}/status')
        data = request.get_json()
        new_status = data.get('status')

        allowed = ['approved', 'removed', 'pending']
        if new_status not in allowed:
            return jsonify({'error': f'Status must be one of {allowed}'}), 400

        cursor.execute(
            'UPDATE Review SET review_status = %s WHERE review_id = %s',
            (new_status, review_id)
        )
        get_db().commit()
        return jsonify({'message': f'Review status updated to {new_status}'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in update_review_status: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-4] DELETE /jordan/reviews/<id>
# Permanently hard-delete a fake or inappropriate review
@jordan.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /jordan/reviews/{review_id}')
        cursor.execute('DELETE FROM Review WHERE review_id = %s', (review_id,))
        get_db().commit()
        return jsonify({'message': 'Review permanently deleted'}), 200
    except Error as e:
        current_app.logger.error(f'Database error in delete_review: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Jordan-6] GET /jordan/analytics/activity-metrics
# Return Activity_Metric rows so Jordan can monitor DB growth over time
@jordan.route('/analytics/activity-metrics', methods=['GET'])
def get_activity_metrics():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /jordan/analytics/activity-metrics')
        cursor.execute('''
            SELECT metric_id, metric_date, reviews_count,
                   active_users_count, restaurant_count
            FROM Activity_Metric
            ORDER BY metric_date DESC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_activity_metrics: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

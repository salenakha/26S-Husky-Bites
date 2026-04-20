from flask import Blueprint, jsonify, request, current_app
from mysql.connector import Error

from backend.db_connection import get_db

marcus_routes = Blueprint('marcus_routes', __name__)


# [Marcus-1] GET /marcus/trends
# Return avg rating trends across all restaurants or a summary
# Optional: ?restaurant_id=7 to filter to one restaurant
@marcus_routes.route('/trends', methods=['GET'])
def get_rating_trends_summary():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/trends')
        restaurant_id = request.args.get('restaurant_id', None)

        query = '''
            SELECT  review_date,
                    ROUND(AVG(rating), 2) AS avg_rating,
                    COUNT(*)              AS total_reviews
            FROM    Review
            WHERE   review_status = 'approved'
        '''
        params = []
        if restaurant_id:
            query += ' AND restaurant_id = %s'
            params.append(restaurant_id)

        query += '''
            GROUP BY review_date
            ORDER BY review_date ASC
        '''
        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_rating_trends_summary: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Marcus-2] GET /marcus/waittime-ratings
# Return avg wait time vs avg rating per restaurant for correlation analysis
# Optional: ?restaurant_id=7 to filter to one restaurant
@marcus_routes.route('/waittime-ratings', methods=['GET'])
def get_wait_vs_rating():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/waittime-ratings')
        restaurant_id = request.args.get('restaurant_id', None)

        query = '''
            SELECT  r.restaurant_id,
                    r.name,
                    COALESCE(ROUND(AVG(w.wait_minutes), 1), 0) AS avg_wait_minutes,
                    COALESCE(ROUND(AVG(rv.rating), 2), 0)       AS avg_rating,
                    COUNT(rv.review_id)                        AS total_reviews
            FROM    Restaurant r
            LEFT JOIN Wait_Time_Record w ON w.restaurant_id  = r.restaurant_id
            LEFT JOIN Review rv          ON rv.restaurant_id = r.restaurant_id
                                       AND rv.review_status = 'approved'
        '''
        params = []
        if restaurant_id:
            query += ' WHERE r.restaurant_id = %s'
            params.append(restaurant_id)

        query += '''
            GROUP BY r.restaurant_id, r.name
            ORDER BY avg_wait_minutes DESC
        '''
        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_waittime_ratings: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Marcus-3] GET /marcus/export
# Return anonymized approved reviews (no user_id) for external analysis
# Optional: ?restaurant_id=7 to filter to one restaurant
@marcus_routes.route('/export', methods=['GET'])
def export_reviews():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/export')
        restaurant_id = request.args.get('restaurant_id', None)

        query = '''
            SELECT  rv.review_id,
                    rv.restaurant_id,
                    r.name     AS restaurant_name,
                    rv.rating,
                    rv.review_text,
                    rv.review_date
            FROM    Review rv
            JOIN    Restaurant r ON r.restaurant_id = rv.restaurant_id
            WHERE   rv.review_status = 'approved'
        '''
        params = []
        if restaurant_id:
            query += ' AND rv.restaurant_id = %s'
            params.append(restaurant_id)

        query += ' ORDER BY rv.review_date DESC'
        cursor.execute(query, params)
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in export_reviews: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Marcus-4] GET /marcus/dietary-coverage
# Count open restaurants per dietary tag to find underserved accommodations
@marcus_routes.route('/dietary-coverage', methods=['GET'])
def get_dietary_coverage():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/dietary-coverage')
        cursor.execute('''
            SELECT  dt.dietary_tag_name,
                    dt.dietary_tag_category,
                    COUNT(DISTINCT rdt.restaurant_id) AS restaurant_count
            FROM    Dietary_Tag dt
            LEFT JOIN Restaurant_Dietary_Tag rdt
                   ON rdt.dietary_tag_id = dt.dietary_tag_id
            LEFT JOIN Restaurant r
                   ON r.restaurant_id = rdt.restaurant_id
                  AND r.status = 'open'
            GROUP BY dt.dietary_tag_id, dt.dietary_tag_name, dt.dietary_tag_category
            ORDER BY restaurant_count ASC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_dietary_coverage: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Marcus-5] GET /marcus/restaurant-performance
# Return restaurants ranked by avg rating with price and cuisine breakdown
@marcus_routes.route('/restaurant-performance', methods=['GET'])
def get_restaurant_performance():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/restaurant-performance')
        limit = int(request.args.get('limit', 10))
        cursor.execute('''
            SELECT  r.restaurant_id,
                    r.name,
                    c.cuisine_name,
                    r.price_range,
                    ROUND(r.avg_rating, 2) AS avg_rating,
                    r.dist_from_campus,
                    r.halal_certified,
                    COUNT(rv.review_id)    AS total_reviews
            FROM    Restaurant r
            JOIN    Cuisine c     ON c.cuisine_id     = r.cuisine_id
            LEFT JOIN Review rv   ON rv.restaurant_id = r.restaurant_id
                                 AND rv.review_status = 'approved'
            WHERE   r.status = 'open'
            GROUP BY r.restaurant_id, r.name, c.cuisine_name,
                     r.price_range, r.avg_rating, r.dist_from_campus, r.halal_certified
            ORDER BY avg_rating DESC
            LIMIT %s
        ''', (limit,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_restaurant_performance: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

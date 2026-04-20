from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

marcus_routes = Blueprint('marcus_routes', __name__)


# [Marcus-1] GET /marcus/restaurants/<id>/rating-trends
# Return avg rating grouped by date so Marcus can track quality over time
@marcus_routes.route('/restaurants/<int:restaurant_id>/rating-trends', methods=['GET'])
def get_rating_trends(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /marcus/restaurants/{restaurant_id}/rating-trends')
        cursor.execute('''
            SELECT  review_date,
                    ROUND(AVG(rating), 2) AS avg_rating,
                    COUNT(*)              AS review_count
            FROM    Review
            WHERE   restaurant_id = %s
              AND   review_status = 'approved'
            GROUP BY review_date
            ORDER BY review_date ASC
        ''', (restaurant_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_rating_trends: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Marcus-2] GET /marcus/restaurants/<id>/crowd-levels
# Return crowd level records broken down by hour and day name
@marcus_routes.route('/restaurants/<int:restaurant_id>/crowd-levels', methods=['GET'])
def get_crowd_levels(restaurant_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /marcus/restaurants/{restaurant_id}/crowd-levels')
        cursor.execute('''
            SELECT  crowd_record_id,
                    crowd_level,
                    recorded_at,
                    HOUR(recorded_at)    AS hour_of_day,
                    DAYNAME(recorded_at) AS day_name
            FROM    Crowd_Level_Record
            WHERE   restaurant_id = %s
            ORDER BY recorded_at ASC
        ''', (restaurant_id,))
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_crowd_levels: {e}')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


# [Marcus-3] GET /marcus/wait-time-vs-rating
# Return avg wait time vs avg rating per restaurant for correlation analysis
@marcus_routes.route('/wait-time-vs-rating', methods=['GET'])
def get_wait_vs_rating():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/wait-time-vs-rating')
        cursor.execute('''
            SELECT  r.restaurant_id,
                    r.name,
                    ROUND(AVG(w.wait_minutes), 1) AS avg_wait_minutes,
                    ROUND(AVG(rv.rating), 2)       AS avg_rating,
                    COUNT(rv.review_id)            AS total_reviews
            FROM    Restaurant r
            JOIN    Wait_Time_Record w  ON w.restaurant_id  = r.restaurant_id
            JOIN    Review rv           ON rv.restaurant_id = r.restaurant_id
            WHERE   rv.review_status = 'approved'
            GROUP BY r.restaurant_id, r.name
            ORDER BY avg_wait_minutes DESC
        ''')
        return jsonify(cursor.fetchall()), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_wait_vs_rating: {e}')
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


# [Marcus-5] GET /marcus/reviews/export
# Return anonymized approved reviews (no user_id) for external analysis
# Optional: ?restaurant_id=7 to filter to one restaurant
@marcus_routes.route('/reviews/export', methods=['GET'])
def export_reviews():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /marcus/reviews/export')
        restaurant_id = request.args.get('restaurant_id', None)

        # WHERE 1=1 lets us append AND clauses cleanly — same pattern as ngo_routes.py
        query = '''
            SELECT  rv.review_id,
                    rv.restaurant_id,
                    r.name     AS restaurant_name,
                    rv.rating,
                    rv.review_text,
                    rv.review_date
            FROM    Review rv
            JOIN    Restaurant r ON r.restaurant_id = rv.restaurant_id
            WHERE   1=1
            AND     rv.review_status = 'approved'
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


# [Marcus-6] GET /marcus/restaurant-performance
# Return restaurants ranked by avg rating with price and cuisine breakdown
# Optional: ?limit=N (default 10)
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

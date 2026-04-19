########################################################
# marcus_routes.py
# Blueprint: Marcus Webb — Data Analyst (Persona 3)
#
# Fixed:
#   - import changed from `db` to `get_db` (matches template)
#   - db.get_db().cursor() → get_db().cursor(dictionary=True)
#   - added current_app.logger calls to match template style
#
# Routes:
#   GET /marcus/restaurants/<id>/rating-trends   [Marcus-1]
#   GET /marcus/restaurants/<id>/crowd-levels    [Marcus-2]
#   GET /marcus/wait-time-vs-rating              [Marcus-3]
#   GET /marcus/dietary-coverage                 [Marcus-4]
#   GET /marcus/reviews/export                   [Marcus-5]
#   GET /marcus/restaurant-performance           [Marcus-6]
########################################################

from flask import Blueprint, request, jsonify, make_response, current_app
from backend.db_connection import get_db

# Blueprint object — registered in rest_entry.py as url_prefix='/marcus'
marcus_routes = Blueprint('marcus_routes', __name__)


# ── [Marcus-1] GET /marcus/restaurants/<id>/rating-trends ────────────────────
# Return avg rating grouped by date so Marcus can track quality over time
@marcus_routes.route('/restaurants/<int:restaurant_id>/rating-trends', methods=['GET'])
def get_rating_trends(restaurant_id):
    current_app.logger.info(f'GET /marcus/restaurants/{restaurant_id}/rating-trends')
    # dictionary=True returns rows as dicts so jsonify can serialize them
    cursor = get_db().cursor(dictionary=True)
    query = '''
        SELECT  review_date,
                ROUND(AVG(rating), 2) AS avg_rating,
                COUNT(*)              AS review_count
        FROM    Review
        WHERE   restaurant_id = %s
          AND   review_status = 'approved'
        GROUP BY review_date
        ORDER BY review_date ASC
    '''
    cursor.execute(query, (restaurant_id,))
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Marcus-2] GET /marcus/restaurants/<id>/crowd-levels ─────────────────────
# Return crowd level records broken down by hour and day name
@marcus_routes.route('/restaurants/<int:restaurant_id>/crowd-levels', methods=['GET'])
def get_crowd_levels(restaurant_id):
    current_app.logger.info(f'GET /marcus/restaurants/{restaurant_id}/crowd-levels')
    cursor = get_db().cursor(dictionary=True)
    query = '''
        SELECT  crowd_record_id,
                crowd_level,
                recorded_at,
                HOUR(recorded_at)    AS hour_of_day,
                DAYNAME(recorded_at) AS day_name
        FROM    Crowd_Level_Record
        WHERE   restaurant_id = %s
        ORDER BY recorded_at ASC
    '''
    cursor.execute(query, (restaurant_id,))
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Marcus-3] GET /marcus/wait-time-vs-rating ───────────────────────────────
# Return avg wait time vs avg rating per restaurant for correlation analysis
@marcus_routes.route('/wait-time-vs-rating', methods=['GET'])
def get_wait_vs_rating():
    current_app.logger.info('GET /marcus/wait-time-vs-rating')
    cursor = get_db().cursor(dictionary=True)
    query = '''
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
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Marcus-4] GET /marcus/dietary-coverage ──────────────────────────────────
# Count open restaurants per dietary tag to find underserved accommodations
@marcus_routes.route('/dietary-coverage', methods=['GET'])
def get_dietary_coverage():
    current_app.logger.info('GET /marcus/dietary-coverage')
    cursor = get_db().cursor(dictionary=True)
    query = '''
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
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Marcus-5] GET /marcus/reviews/export ────────────────────────────────────
# Return anonymized approved reviews (no user_id) for external analysis
# Optional: ?restaurant_id=7 to filter to one restaurant
@marcus_routes.route('/reviews/export', methods=['GET'])
def export_reviews():
    current_app.logger.info('GET /marcus/reviews/export')
    # Pull optional filter from query string
    restaurant_id = request.args.get('restaurant_id', None)
    cursor = get_db().cursor(dictionary=True)
    # Deliberately omit user_id to anonymize the export
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
    # Append restaurant filter only if the caller provided one
    if restaurant_id:
        query += ' AND rv.restaurant_id = %s'
        params.append(restaurant_id)
    query += ' ORDER BY rv.review_date DESC'
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


# ── [Marcus-6] GET /marcus/restaurant-performance ────────────────────────────
# Return restaurants ranked by avg rating with price and cuisine breakdown
# Optional: ?limit=N  (default 10)
@marcus_routes.route('/restaurant-performance', methods=['GET'])
def get_restaurant_performance():
    current_app.logger.info('GET /marcus/restaurant-performance')
    # Cast to int so we can safely pass it as a SQL param
    limit = int(request.args.get('limit', 10))
    cursor = get_db().cursor(dictionary=True)
    query = '''
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
    '''
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)

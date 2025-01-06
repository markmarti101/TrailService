from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
import pyodbc
from datetime import datetime

# Flask and Flask-RESTX setup
app = Flask(__name__)
api = Api(app, title="Trail Service API", description="A micro-service for managing trails", version="1.0")

# Database Connection Function
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=dist-6-505.uopnet.plymouth.ac.uk;"
        "DATABASE=COMP2001_MMartirosyan;"
        "UID=MMartirosyan;"  # Replace with your database username
        "PWD=FcxR807*;"  # Replace with your database password
    )
    return conn

# API Models
trail_model = api.model('Trail', {
    'TrailID': fields.Integer(required=True, description='The unique ID of the trail'),
    'Title': fields.String(required=True, description='The title of the trail'),
    'Description': fields.String(description='The description of the trail'),
    'Duration': fields.Integer(description='Duration in minutes'),
    'Elevation': fields.Float(description='Elevation of the trail'),
    'RouteType': fields.String(description='Type of the trail route (e.g., loop, point-to-point)'),
    'Length': fields.Float(description='Length of the trail in kilometers'),
    'LocationID': fields.Integer(required=True, description='The ID of the trail location')
})

# Helper function to validate LocationID
def validate_location(location_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT LocationID FROM CW2.TrailLocation WHERE LocationID = ?", (location_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Helper function to validate TrailID uniqueness
def validate_trail_id(trail_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TrailID FROM CW2.Trail WHERE TrailID = ?", (trail_id,))
    result = cursor.fetchone()
    conn.close()
    return result is None

# API Endpoints

# GET all trails
@api.route('/trails')
class TrailsList(Resource):
    @api.doc('get_trails')
    def get(self):
        """Retrieve all trails"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CW2.Trail")
        rows = cursor.fetchall()

        # Map results to dictionary
        columns = [column[0] for column in cursor.description]
        trails = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return jsonify(trails)

    @api.expect(trail_model)
    @api.doc('create_trail')
    def post(self):
        """Create a new trail"""
        data = request.get_json()

        # Validate TrailID uniqueness
        if not validate_trail_id(data['TrailID']):
            return {"error": "TrailID already exists. Please use a unique TrailID."}, 400

        # Validate LocationID
        if not validate_location(data['LocationID']):
            return {"error": "Invalid LocationID. Ensure the location exists in the TrailLocation table."}, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO CW2.Trail (TrailID, Title, Description, Duration, Elevation, RouteType, Length, LocationID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (
                data['TrailID'], data['Title'], data['Description'], data['Duration'],
                data['Elevation'], data['RouteType'], data['Length'], data['LocationID']
            ))
            conn.commit()
        except pyodbc.Error as e:
            conn.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        finally:
            conn.close()

        return {'message': 'Trail created successfully!'}, 201

# GET, PUT, DELETE a single trail
@api.route('/trails/<int:trail_id>')
class Trail(Resource):
    @api.doc('get_trail')
    def get(self, trail_id):
        """Retrieve a single trail by its ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CW2.Trail WHERE TrailID = ?", (trail_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            columns = [column[0] for column in cursor.description]
            trail = dict(zip(columns, row))
            return jsonify(trail)
        else:
            return {'error': 'Trail not found'}, 404

    @api.expect(trail_model)
    @api.doc('update_trail')
    def put(self, trail_id):
        """Update a trail by its ID"""
        data = request.get_json()

        # Validate LocationID
        if not validate_location(data['LocationID']):
            return {"error": "Invalid LocationID. Ensure the location exists in the TrailLocation table."}, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            UPDATE CW2.Trail
            SET Title = ?, Description = ?, Duration = ?, Elevation = ?, RouteType = ?, Length = ?, LocationID = ?
            WHERE TrailID = ?
        """
        try:
            cursor.execute(query, (
                data['Title'], data['Description'], data['Duration'], data['Elevation'],
                data['RouteType'], data['Length'], data['LocationID'], trail_id
            ))
            conn.commit()
        except pyodbc.Error as e:
            conn.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        finally:
            conn.close()

        return {'message': 'Trail updated successfully!'}

    @api.doc('delete_trail')
    def delete(self, trail_id):
        """Delete a trail by its ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM CW2.Trail WHERE TrailID = ?", (trail_id,))
            conn.commit()
        except pyodbc.Error as e:
            conn.rollback()
            return {"error": f"Database error: {str(e)}"}, 500
        finally:
            conn.close()

        return {'message': 'Trail deleted successfully!'}

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True, port=5001)
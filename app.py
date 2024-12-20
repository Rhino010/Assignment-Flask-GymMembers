from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    member_id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ('name', 'age', 'member_id')

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


def get_db_connection():
    db_name = "gym_db"
    user = "root"
    password = "Opal!2024"
    host = "localhost"

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        print("Connected to MySQL database successfully.")
        return conn

    except Error as e:
        print(f"Error: {e}")


@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed."}), 500
        cursor = conn.cursor(dictionary = True)

        new_member = (member_data['name'], member_data['age'])

        query = 'INSERT INTO members(name, age) VALUES (%s, %s)'

        cursor.execute(query, new_member)
        conn.commit()
        return jsonify({'message': 'Member added successfully.'}),201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed."}), 500
        cursor = conn.cursor(dictionary=True)

        selected_member = (member_id, )

        query = "SELECT name, age, member_id FROM members WHERE member_id = %s"

        cursor.execute(query, selected_member)

        found_member = cursor.fetchone()

        if not found_member:
            return jsonify({"error": "Member not found."}), 404

        return member_schema.jsonify(found_member)
    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal server errror."}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members', methods=['GET'])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed."}), 500
        cursor = conn.cursor(dictionary = True)

        query = 'SELECT * FROM members'

        cursor.execute(query)

        members = cursor.fetchall()

        return members_schema.jsonify(members)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)
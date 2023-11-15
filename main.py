from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    # Validate input
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType')

    if not username or not email or not password or not user_type:
        return jsonify({'message': 'Missing data for required fields'}), 400

    # Check for existing user
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already in use'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, passwordHash=hashed_password, userType=user_type)

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Could not process your request'}), 500

    return jsonify({'message': 'User created successfully', 'userId': new_user.userId}), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(userId=user_id).first_or_404(description='User not found')
    return jsonify({
        'userId': user.userId,
        'username': user.username,
        'email': user.email,
        'userType': user.userType
    })


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.filter_by(userId=user_id).first_or_404(description='User not found')
    data = request.get_json()

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.userType = data.get('userType', user.userType)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Could not update user'}), 500

    return jsonify({'message': 'User updated successfully'})


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(userId=user_id).first_or_404(description='User not found')
    db.session.delete(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Could not delete user'}), 500

    return jsonify({'message': 'User deleted successfully'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': error.description}), 404


# Create the database tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)



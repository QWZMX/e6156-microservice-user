from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from sqlalchemy.exc import IntegrityError
from auth import auth_bp, oauth

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret_key'
app.config['GOOGLE_CLIENT_ID'] = '116074870166-il6t2nbr91d0d9sb39gal9q9mbcspe9h.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
app.config['GOOGLE_CLIENT_CONFIG'] = {
    'client_id': app.config['GOOGLE_CLIENT_ID'],
    'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
    'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
    'authorize_params': None,
    'access_token_url': 'https://accounts.google.com/o/oauth2/token',
    'access_token_params': None,
    'refresh_token_url': None,
    'redirect_uri': 'http://ec2-18-221-153-218.us-east-2.compute.amazonaws.com:8012/auth/login/authorize',
    'client_kwargs': {
        'scope': 'openid email profile',
    },
    'jwks_uri': 'https://www.googleapis.com/oauth2/v3/certs',
}

oauth.init_app(app)
oauth.register('google', **app.config['GOOGLE_CLIENT_CONFIG'])


app.register_blueprint(auth_bp, url_prefix='/auth')


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


@app.route('/users', methods=['GET'])
def get_users():
    query = User.query

    email_filter = request.args.get('email')
    user_type_filter = request.args.get('userType')
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)

    if email_filter:
        query = query.filter(User.email == email_filter)
    if user_type_filter:
        query = query.filter(User.userType == user_type_filter)

    users = query.offset(offset).limit(limit).all()

    return jsonify([{
        'userId': user.userId,
        'username': user.username,
        'email': user.email,
        'userType': user.userType
    } for user in users]), 200


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


@app.route('/')
def index():
    return 'Welcome to the app'


# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)

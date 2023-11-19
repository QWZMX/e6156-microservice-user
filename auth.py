import os
import base64
from flask import Blueprint, redirect, url_for, session, current_app, jsonify, request, render_template
from authlib.integrations.flask_client import OAuth
from models import db, User

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()


def get_google_oauth_client():
    return oauth.create_client('google')


def generate_nonce(length=16):
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')


@auth_bp.route('/login')
def login():
    if 'user_id' in session:
        user_id = session['user_id']
        target_url = f'http://qwzmx.s3-website.us-east-2.amazonaws.com/#/profile/{user_id}'
        return redirect(target_url)

    google = get_google_oauth_client()
    nonce = generate_nonce()
    session['nonce'] = nonce
    redirect_uri = url_for('.authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    target_url = f'http://qwzmx.s3-website.us-east-2.amazonaws.com'
    return redirect(target_url)


@auth_bp.route('/login/authorize')
def authorize():
    try:
        google = get_google_oauth_client()
        token = google.authorize_access_token()
        nonce = session.pop('nonce', None)
        user_info = google.parse_id_token(token, nonce=nonce)

        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            session['email'] = user_info['email']
            return redirect(url_for('.complete_registration'))
        else:
            session['user_id'] = user.userId
            user_id = session['user_id']
            target_url = f'http://qwzmx.s3-website.us-east-2.amazonaws.com/#/profile/{user_id}'
            return redirect(target_url)
    except Exception as e:
        current_app.logger.error(f'OAuth authorization error: {e}')
        return jsonify({'error': 'An error occurred during the login process'}), 500


@auth_bp.route('/complete-registration', methods=['GET', 'POST'])
def complete_registration():
    if request.method == 'POST':
        username = request.form.get('username')
        usertype = request.form.get('usertype')
        email = session.get('email', None)

        if not email:
            return jsonify({'error': 'Session expired or invalid.'}), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User already exists.'}), 400

        new_user = User(username=username, email=email, passwordHash="default", userType=usertype)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('.login'))
    return render_template('registration_form.html')


@auth_bp.route('/get-user')
def get_user():
    if 'user_id' in session:
        return jsonify({'userId': session['user_id']})
    else:
        return jsonify({'error': 'User not logged in'}), 401


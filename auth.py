import os
import base64
from flask import Blueprint, redirect, url_for, session, current_app
from authlib.integrations.flask_client import OAuth

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()

def get_google_oauth_client():
    return oauth.create_client('google')

def generate_nonce(length=16):
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')

@auth_bp.route('/login')
def login():
    google = get_google_oauth_client()
    nonce = generate_nonce()
    session['nonce'] = nonce
    redirect_uri = url_for('.authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@auth_bp.route('/login/authorize')
def authorize():
    try:
        google = get_google_oauth_client()
        token = google.authorize_access_token()
        nonce = session.get('nonce')
        user = google.parse_id_token(token, nonce=nonce)
        session['user'] = user
        return redirect(url_for('index'))
    except Exception as e:
        current_app.logger.error(f'OAuth authorization error: {e}')
        raise


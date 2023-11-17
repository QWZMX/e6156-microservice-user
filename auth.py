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
    # 检查session中是否已经有用户信息
    if 'user_id' in session:
        return jsonify({'userId': session['user_id']})

    google = get_google_oauth_client()
    nonce = generate_nonce()
    session['nonce'] = nonce
    redirect_uri = url_for('.authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('.login'))


@auth_bp.route('/login/authorize')
def authorize():
    try:
        google = get_google_oauth_client()
        token = google.authorize_access_token()
        nonce = session.pop('nonce', None)
        user_info = google.parse_id_token(token, nonce=nonce)

        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            # 将 email 保存到 session 中，稍后创建用户
            session['email'] = user_info['email']
            # 重定向到注册表单
            return redirect(url_for('.complete_registration'))
        else:
            # 用户已存在，直接返回用户 ID 并保存到session中
            session['user_id'] = user.userId
            return jsonify({'userId': user.userId})
    except Exception as e:
        current_app.logger.error(f'OAuth authorization error: {e}')
        return jsonify({'error': 'An error occurred during the login process'}), 500


@auth_bp.route('/complete-registration', methods=['GET', 'POST'])
def complete_registration():
    # 如果是表单提交
    if request.method == 'POST':
        username = request.form.get('username')
        usertype = request.form.get('usertype')
        email = session.get('email', None)

        # 确保email存在于session中
        if not email:
            return jsonify({'error': 'Session expired or invalid.'}), 400

        # 检查用户是否已经存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # 用户已存在，返回错误信息
            return jsonify({'error': 'User already exists.'}), 400

        # 创建新用户并保存到数据库
        new_user = User(username=username, email=email, passwordHash="default", userType=usertype)
        db.session.add(new_user)
        db.session.commit()

        # 重定向回登录页面，可以附带一些消息如用户创建成功
        return redirect(url_for('.login'))

    # 如果是GET请求，显示注册表单
    return render_template('registration_form.html')


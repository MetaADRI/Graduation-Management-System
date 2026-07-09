# backend/auth.py
import jwt, datetime, functools
from flask import request, jsonify

SECRET  = 'GPMS_CUZ_SECRET_CHANGE_IN_PROD'
EXPIRY  = 8  # hours

def create_token(user: dict) -> str:
    payload = {
        'id':    user['id'],
        'name':  user['name'],
        'email': user['email'],
        'role':  user['role'],
        'exp':   datetime.datetime.utcnow() + datetime.timedelta(hours=EXPIRY),
    }
    return jwt.encode(payload, SECRET, algorithm='HS256')

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_request() -> str | None:
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    # Check query parameter for iframe requests
    token = request.args.get('token')
    if token:
        return token
    return None

def require_auth(allowed_roles=None):
    """Decorator — protects a route. Pass a list of allowed roles, or None for any."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            token = get_token_from_request()
            if not token:
                return jsonify({'success': False, 'message': 'Unauthorized: No token provided'}), 401

            payload = decode_token(token)
            if not payload:
                return jsonify({'success': False, 'message': 'Unauthorized: Invalid or expired token'}), 401

            if allowed_roles and payload['role'] not in allowed_roles:
                return jsonify({'success': False, 'message': 'Forbidden: Insufficient permissions'}), 403

            request.user = payload
            return fn(*args, **kwargs)
        return wrapper
    return decorator

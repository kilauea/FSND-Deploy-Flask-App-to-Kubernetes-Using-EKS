"""
A simple app to create a JWT token.
"""
import sys
import os
import logging
import datetime
import functools
import jwt

# pylint: disable=import-error
from flask import Flask, jsonify, request, abort


JWT_SECRET = os.environ.get('JWT_SECRET', 'abc123abc1234')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


def _logger():
    '''
    Setup logger format, level, and handler.

    RETURNS: log object
    '''
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log = logging.getLogger(__name__)
    log.setLevel(LOG_LEVEL)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    log.addHandler(stream_handler)
    return log


LOG = _logger()
LOG.debug("Starting with log level: %s" % LOG_LEVEL )
APP = Flask(__name__)

def require_jwt(function):
    """
    Decorator to check valid jwt is present.
    """
    @functools.wraps(function)
    def decorated_function(*args, **kws):
        if not 'Authorization' in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = str.replace(str(data), 'Bearer ', '')
        try:
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except: # pylint: disable=bare-except
            abort(401)

        return function(*args, **kws)
    return decorated_function


@APP.route('/', methods=['POST', 'GET'])
def health():
    return jsonify("Healthy")


@APP.route('/auth', methods=['POST'])
def auth():
    """
    Create JWT token based on email.
    """
    request_data = request.get_json()
    email = request_data.get('email')
    password = request_data.get('password')
    if not email:
        LOG.error("No email provided")
        return jsonify({"message": "Missing parameter: email"}, 400)
    if not password:
        LOG.error("No password provided")
        return jsonify({"message": "Missing parameter: password"}, 400)
    body = {'email': email, 'password': password}

    user_data = body

    return jsonify(token=_get_jwt(user_data).decode('utf-8'))


@APP.route('/contents', methods=['GET'])
def decode_jwt():
    """
    Check user token and return non-secret data
    """
    if not 'Authorization' in request.headers:
        abort(401)
    data = request.headers['Authorization']
    token = str.replace(str(data), 'Bearer ', '')
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except Exception as e: # pylint: disable=bare-except
        print(sys.exc_info())
        abort(401)


    response = {'email': data['email'],
                'exp': data['exp'],
                'nbf': data['nbf'] }
    return jsonify(**response)


def _get_jwt(user_data):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(weeks=2)
    payload = {'exp': exp_time,
               'nbf': datetime.datetime.utcnow(),
               'email': user_data['email']}
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

if __name__ == '__main__':
    try:
        # To use debug=True must remove exec permisions from main.py as follows:
        # chmod -x main.py
        APP.run(host='127.0.0.1', port=8080, debug=True)
    except OSError as e:
        print('OSError: %s' % str(e))
    except Exception as e:
        print(sys.exc_info())

'''
First install jq:
- brew install jq 
Test the endpoints with:
- /auth:
  export TOKEN=`curl -d '{"email":"myemail@gmail.com","password":"#MyPassw0rd!"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8080/auth  | jq -r '.token'`
  echo $TOKEN
- /contents:
  curl --request GET 'http://127.0.0.1:8080/contents' -H "Authorization: Bearer ${TOKEN}" | jq .

'''
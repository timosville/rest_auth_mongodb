from flask import Flask
from flask_mongoengine import MongoEngine
from flask_httpauth import HTTPBasicAuth
from mongoengine import Document, StringField
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort, request, jsonify, url_for, g
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)

SECRET_KEY = 'sdafdkjhsfmcvbbasjjsafghghgsd\sa'
DB_NAME = 'myrestfulapi2'
MONGO_URI = 'mongodb://localhost/' + DB_NAME
PORT = 27017
MONGODB_SETTINGS = {'db': DB_NAME,
                    }

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS
auth = HTTPBasicAuth()
db = MongoEngine(app)


class User(Document):
    username = StringField(max_length=32)
    password_hash = StringField()

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.objects.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        try:
            user = User.objects.get(username=username_or_token)
            if check_password_hash(user.password_hash, password) is True:
                user['id'] = str(user['id'])
                g.user = user
                return g.user
            else:
                return False
        except User.DoesNotExist:
            return False


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    try:
        User.objects.get(username=username)
        abort(400)
    except User.DoesNotExist:
        user = User(username=username)
        user.hash_password(password)
        user.save()
    return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}


@app.route('/api/users/<id>')
def get_user(id):
    user = User.objects.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, {}!'.format(g.user.username)})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=80,
            debug=True,
            use_reloader=True)
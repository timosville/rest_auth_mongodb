from flask import Flask
from flask_mongoengine import MongoEngine
from flask_httpauth import HTTPTokenAuth
from mongoengine import Document, StringField
from werkzeug.security import generate_password_hash
from flask import abort, request, jsonify, url_for
from itsdangerous import TimedJSONWebSignatureSerializer as JWT


app = Flask(__name__)

SECRET_KEY = 'sdafdkjhsfmcvbbasjjsafghghgsd\sa'
DB_NAME = 'myrestfulapi2'
MONGO_URI = 'mongodb://localhost/' + DB_NAME
PORT = 27017
MONGODB_SETTINGS = {'db': DB_NAME,
                    }

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS
auth = HTTPTokenAuth('Bearer')
db = MongoEngine(app)
jwt = JWT(app.config['SECRET_KEY'], expires_in=3600)


class User(Document):
    username = StringField(max_length=32)
    password_hash = StringField()

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

for user in User.objects:
    token = jwt.dumps({'username': user.username})
    print('*** token for {}: {}\n'.format(user, token))


@auth.verify_token
def verify_token(token):
    try:
        data = jwt.loads(token)
    except:
        return False
    if 'username' in data:
        return True
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
    return jsonify({'data': 'Hello, {}!'.format(auth.username())})


@app.route('/api/token/test')
@auth.login_required
def token_auth_test():
    return 'It works!'


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=80,
            debug=True,
            use_reloader=True)
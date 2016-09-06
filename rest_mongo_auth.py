from flask import Flask
from mongoframes import Frame
from pymongo import MongoClient
from flask import request, abort, jsonify, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

DB_NAME = 'myrestfulapi3'
MONGO_URI = 'mongodb://localhost:27017/' + DB_NAME

app.mongo = MongoClient(MONGO_URI)
Frame._client = app.mongo
auth = HTTPBasicAuth()


class User(Frame):
    _fields = {
        'username',
        'password_hash'
    }


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if User.one({'username': username}) is not None:
        abort(400)
    password_hash = generate_password_hash(password)
    user = User(
        username=username,
        password_hash=password_hash
    )

    user.insert()
    return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', _id=user._id, _external=True)}


@app.route('/api/users/<_id>')
def get_user(_id):
    user = User.one({'id': _id})
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@auth.verify_password
def verify_password(username, password):
    user = User.one({'username': username})
    if not user or not check_password_hash(user.password_hash, password):
        return False
    g.user = user
    return True


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, {}!'.format(g.user.username)})

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=80,
            debug=True,
            use_reloader=True)

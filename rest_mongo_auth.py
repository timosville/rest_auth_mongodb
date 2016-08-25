from flask import Flask
from flask_mongoengine import MongoEngine
from flask_httpauth import HTTPBasicAuth
from mongoengine import Document, StringField
from werkzeug.security import generate_password_hash, check_password_hash

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

    def verify_password(self, password):
        return check_password_hash(password, self.password_hash)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=80,
            debug=True,
            use_reloader=True)
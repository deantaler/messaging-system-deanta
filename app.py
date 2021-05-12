import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pymysql
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])
# s3.access_key['CLEARDB_DATABASE_URL']

pymysql.install_as_MySQLdb()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bfe492d145dddb:9cc666f7@us-cdbr-east-03.cleardb.com/heroku_075cd3d1f9bda9e?reconnect=true'

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    public_user_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(8))

# class Message(db.Model):
#     message_id = db.Column(db.Integer, primary_key=True)
#     sender_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
#     receiver_id = db.Column(db.Integer, db.ForeignKey(User.user_id))
#     subject = db.Column(db.String(20))
#     text = db.Column(db.String(100))
#     date = db.Column(db.DateTime)
#     read = db.Column(db.Boolean)  # True - read, False - unread


# @app.route('/user', method=['GET'])
# def get_all_users():
#     return ''
#
# @app.route('/user/<user_id>', method=['GET'])
# def get_one_user():
#     return ''

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    public_user_id = str(uuid.uuid4())
    name = data['name']
    password = generate_password_hash(data['password'], method='sha256')
    user = User(public_user_id=public_user_id, name=name, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Welcome {}'.format(name)})

# @app.route('/user/<user_id>', method=['DELETE'])
# def delete_user():
#     return ''


if __name__ == '__main__':
    app.run(debug=True)

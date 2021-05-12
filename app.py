from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////C:/Users/דין טלר/PycharmProjects/messaging_system.db'

db = SQLAlchemy(app)


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(8))
    # admin = db.Column(db.Boolean)


class Messages(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, ForeignKey(Users.user_id))
    receiver_id = db.Column(db.Integer, ForeignKey(Users.user_id))
    subject = db.Column(db.String(20))
    text = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    read = db.Column(db.Boolean)  # True - read, False - unread


# @app.route('/')
# def hello_world():
#     return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)

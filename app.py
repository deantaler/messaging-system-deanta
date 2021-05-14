from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import pymysql
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

pymysql.install_as_MySQLdb()
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bfe492d145dddb:9cc666f7@us-cdbr-east-03.cleardb.com' \
                                        '/heroku_075cd3d1f9bda9e? '

db = SQLAlchemy(app)


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    password = db.Column(db.String(8))


class Messages(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey(Users.user_id))
    receiver_id = db.Column(db.Integer, db.ForeignKey(Users.user_id))
    subject = db.Column(db.String(50))
    text = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    read = db.Column(db.Boolean)  # True - read, False - unread


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing.'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Users.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid.'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/user', methods=['POST'])
def create_user():
    with app.app_context():
        data = request.get_json()
        name = data['name']
        password = data['password']

        if len(name) > 20:
            return jsonify({'message': 'name {} is too long, please select name up to 20 characters.'.format(name)})
        if len(password) > 8:
            return jsonify({'message': 'password is too long, please select password up to 8 characters.'.format(name)})

        if Users.query.filter_by(name=data['name']).first():
            return jsonify({'message': 'name {} already exist. please select different name.'.format(name)})
        user = Users(name=name, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Welcome {}'.format(name)})


@app.route('/user/<user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    user = Users.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'message': 'No user found.'})

    user_data = {'user_id': user.user_id, 'name': user.name, 'password': user.password}
    return jsonify({'user': user_data})


@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = Users.query.all()
    output = []

    for user in users:
        user_data = {'user_id': user.user_id, 'name': user.name, 'password': user.password}
        output.append(user_data)

    return jsonify({'users': output})


# current_user = Users.query.filter_by(name='Saul').first()


@app.route('/message', methods=['POST'])
@token_required
def write_message(current_user):
    data = request.get_json()
    receiver_name = data['receiver']
    subject = data['subject']
    text = data['text']
    receiver_user = Users.query.filter_by(name=receiver_name).first()
    if not receiver_user:
        return jsonify({'message': '{} not found.'.format(receiver_name)})
    receiver_id = receiver_user.user_id

    if len(text) > 100:
        return jsonify({'message': 'subject is too long.'})
    if len(text) > 100:
        return jsonify({'message': 'text is too long.'})

    new_message = Messages(sender_id=current_user.user_id, receiver_id=receiver_id, subject=subject, text=text,
                           date=datetime.datetime.now(), read=False)
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'massage sent'})


@app.route('/message/<message_id>', methods=['GET'])
@token_required
def get_message(current_user, message_id):
    message = Messages.query.filter_by(message_id=message_id).first()
    if not message:
        return jsonify({'message': 'No message found.'})
    if message.receiver_id != current_user.user_id:
        return jsonify({'message': 'You are not the receiver of this message.'})
    message_data = {'message_id': message.message_id,
                    'sender': Users.query.filter_by(user_id=message.sender_id).first().name,
                    'subject': message.subject,
                    'text': message.text,
                    'date': message.date,
                    'read': message.read}
    return jsonify({'message': message_data})


@app.route('/read_messages/<read_all>', methods=['GET'])
@token_required
def get_all_messages(current_user, read_all):
    if read_all == 'True':  # all massages
        messages = Messages.query.filter_by(receiver_id=current_user.user_id).all()
    else:  # only unread massages
        messages = Messages.query.filter_by(receiver_id=current_user.user_id, read=False).all()
    if not messages:
        return jsonify({'message': 'messages not found.'})
    output = []

    for message in messages:
        message_data = {'message_id': message.message_id,
                        'sender': Users.query.filter_by(user_id=message.sender_id).first().name,
                        'subject': message.subject,
                        'text': message.text,
                        'date': message.date,
                        'read': message.read}
        output.append(message_data)
        message.read = True
        db.session.commit()

    return jsonify({'messages': output})


@app.route('/message/<message_id>', methods=['DELETE'])
@token_required
def delete_message(current_user, message_id):
    message = Messages.query.filter_by(message_id=message_id).first()
    if not message:
        return jsonify({'message': 'No message found.'})
    if message.receiver_id != current_user.user_id:
        return jsonify({'message': 'You are not the receiver of this message.'})
    Messages.query.filter_by(message_id=message_id).delete()
    db.session.commit()
    return jsonify({'message': 'message has been deleted'})


@app.route('/login')
def login():
    auth = request.authorization
    if not (auth and auth.username and auth.password):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})
    user = Users.query.filter_by(name=auth.username).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})

    if user.password == auth.password:
        token = jwt.encode(
            {'user_id': user.user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)},
            app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})


@app.route('/')
def hello():
    return 'Welcome to my messaging system!'


if __name__ == '__main__':
    app.run(debug=True)

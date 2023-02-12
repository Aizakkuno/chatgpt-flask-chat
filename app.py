from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/chat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-SocketIO and SQLAlchemy
socketio = SocketIO(app)
db = SQLAlchemy(app)

# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create database tables
db.create_all()

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    user = User.query.filter_by(name=username).first()
    if not user:
        user = User(name=username)
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('chat', username=username))

@app.route('/chat/<username>')
def chat(username):
    user = User.query.filter_by(name=username).first_or_404()
    messages = Message.query.order_by(Message.id.desc()).limit(50).all()
    return render_template('chat.html', username=username, messages=messages)

# Define SocketIO events
@socketio.on('send_message')
def handle_send_message_event(data):
    user = User.query.filter_by(name=data['username']).first()
    message = Message(text=data['message'], user=user)
    db.session.add(message)
    db.session.commit()
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/chatdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    media_url = db.Column(db.String(500))

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{"sender": msg.sender, "content": msg.content, "media_url": msg.media_url} for msg in messages])

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    new_msg = Message(sender=data['sender'], content=data['content'], media_url=data['media_url'])
    db.session.add(new_msg)
    db.session.commit()
    return jsonify({"status": "success"}), 201

@socketio.on('send_message')
def handle_message(data):
    new_msg = Message(sender=data['sender'], content=data['message'], media_url=data.get('media', None))
    db.session.add(new_msg)
    db.session.commit()
    
    emit('message', {
        'message': data['message'],
        'sender': data['sender'],
        'media': data.get('media', None)
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

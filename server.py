from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route("/")
def index():
    return render_template("index.html")

users = {}  # sid → username

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("join")
def handle_join(data):
    username = data["username"]
    users[request.sid] = username
    join_room(username)

    emit("user_list", list(users.values()), broadcast=True)
    emit("system_message", f"{username} joined the chat", broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        emit("user_list", list(users.values()), broadcast=True)
        emit("system_message", f"{username} left the chat", broadcast=True)

@socketio.on("message")
def handle_message(data):
    emit("message", data, broadcast=True)

@socketio.on("dm")
def handle_dm(data):
    sender = data["from"]
    receiver = data["to"]
    message = data["message"]

    emit("dm", {
        "from": sender,
        "message": message
    }, room=receiver)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)

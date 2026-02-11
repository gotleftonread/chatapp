from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
from collections import defaultdict
from flask import request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

connected_users = {}
rooms = defaultdict(set)
DEFAULT_ROOM = "general"


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(data):
    username = data.get("username")
    room = data.get("room", DEFAULT_ROOM)
    if not username:
        return

    connected_users[request.sid] = {"username": username, "room": room}
    rooms[room].add(username)
    join_room(room)

    emit("system_message", {"message": f"{username} joined {room}."}, room=room)
    emit("user_list", list(rooms[room]), room=room)


@socketio.on("send_message")
def handle_send_message(data):
    msg = data.get("message", "").strip()
    user_info = connected_users.get(request.sid)
    if not user_info or not msg:
        return

    username = user_info["username"]
    room = user_info["room"]
    emit("chat_message", {"username": username, "message": msg}, room=room)


@socketio.on("disconnect")
def handle_disconnect():
    user_info = connected_users.pop(request.sid, None)
    if not user_info:
        return

    username = user_info["username"]
    room = user_info["room"]
    if username in rooms[room]:
        rooms[room].remove(username)

    emit("system_message", {"message": f"{username} left {room}."}, room=room)
    emit("user_list", list(rooms[room]), room=room)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
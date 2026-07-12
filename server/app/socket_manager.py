import socketio

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="http://localhost:5173",
    cors_credentials=True,
)


@sio.event
async def connect(sid, environ, auth=None):
    print("Client connected")


@sio.event
async def join(sid, user_id):
    await sio.enter_room(sid, f"user_{user_id}")


@sio.event
async def disconnect(sid):
    print("Client disconnected")


async def emit_notification(user_id, message: dict):
    await sio.emit("notification", message, room=f"user_{user_id}")


socket_app = socketio.ASGIApp(sio, socketio_path="socket.io")

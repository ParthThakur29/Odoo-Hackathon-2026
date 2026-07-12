import socketio

from .main import app
from .socket_manager import sio

# Wrap the FastAPI app with the Socket.IO ASGI app. Requests to /socket.io/*
# are handled by Socket.IO; everything else is forwarded to FastAPI.
# This is the app that should be pointed to by uvicorn, e.g.:
#   uvicorn app.asgi:asgi_app --host 0.0.0.0 --port 3000
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="socket.io")

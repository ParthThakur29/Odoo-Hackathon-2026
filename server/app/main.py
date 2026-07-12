import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import Base, engine
from .routers import (
    auth,
    assets,
    allocations,
    bookings,
    maintenance,
    audits,
    departments,
    categories,
    employees,
    activity,
    notifications,
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AssetFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(allocations.router)
app.include_router(bookings.router)
app.include_router(maintenance.router)
app.include_router(audits.router)
app.include_router(departments.router)
app.include_router(categories.router)
app.include_router(employees.router)
app.include_router(activity.router)
app.include_router(notifications.router)

# Serve uploaded files
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Serve built React client (client/dist), matching the original Express static setup
CLIENT_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client", "dist"))
if os.path.isdir(CLIENT_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(CLIENT_DIST, "assets")), name="client-assets")

    @app.get("/{full_path:path}")
    def serve_client(full_path: str):
        return FileResponse(os.path.join(CLIENT_DIST, "index.html"))

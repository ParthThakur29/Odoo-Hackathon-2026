# AssetFlow

Backend converted from Node.js/Express + Prisma to **Python FastAPI + SQLAlchemy**.
The React client is unchanged.

## Backend (FastAPI)

```bash
cd server
python -m venv venv && source venv/bin/activate   # optional
pip install -r requirements.txt
cp .env.example .env    # edit JWT_SECRET as needed
python seed.py          # creates dev.db and seed data
uvicorn app.asgi:asgi_app --reload --port 8000
```

Seeded accounts (password `admin123` for all):
- admin@company.com — Admin
- manager@company.com — AssetManager
- headit@company.com — DepartmentHead
- john@company.com — Employee

API docs: http://localhost:3000/docs

## Frontend (unchanged, React + Vite)

```bash
cd client
npm install
npm run dev
```

Vite proxies `/api` and `/uploads` to `http://localhost:3000`, so no frontend
changes are required — same routes, same JSON field names (camelCase),
same cookie-based JWT auth, same Socket.IO events.

## Notes on the conversion

- Express routes → FastAPI `APIRouter`s in `server/app/routers/`
- Prisma models → SQLAlchemy models in `server/app/models.py`
- Prisma JSON output (camelCase) → Pydantic schemas with a camelCase alias
  generator in `server/app/schemas.py`, so responses are byte-for-byte
  compatible with what the React client expects
- `jsonwebtoken` + `bcryptjs` → `PyJWT` + `bcrypt`, still using an httpOnly
  `token` cookie
- `multer` uploads → FastAPI `UploadFile`, still written to `/uploads`
- `socket.io` server → `python-socketio`, mounted via `server/app/asgi.py`
  (`uvicorn app.asgi:asgi_app`) so the existing `socket.io-client` on the
  frontend keeps working without changes
- SQLite by default (`DATABASE_URL` env var), same as the original Prisma setup

## Docker

```bash
docker compose up --build
```

FROM node:20-alpine AS client-build
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt
COPY server/ ./server/
COPY --from=client-build /app/client/dist ./client/dist
RUN mkdir -p /app/uploads
WORKDIR /app/server
EXPOSE 3000
CMD ["uvicorn", "app.asgi:asgi_app", "--host", "0.0.0.0", "--port", "3000"]

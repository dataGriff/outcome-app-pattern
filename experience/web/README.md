Simple Flask web frontend that calls the behaviour service.

Run with docker-compose (root compose maps port 5000).

The UI proxies to `/api/generate-colour` which forwards to the behaviour service at `http://behaviour-service:8000/generate-colour` inside compose to avoid CORS.

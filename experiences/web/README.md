# experiences/web — Flask web experience

The **web** channel consuming the one behaviour API. Run with the root
`docker-compose.yml`; the UI is served on **http://localhost:5001** (host 5000 is
often taken by macOS AirPlay Receiver).

- **Generate** — the button POSTs to the same-origin Flask proxy
  `/api/colours`, which forwards to `POST {DOMAIN_API_URL}/colours` (proxying
  writes avoids browser CORS). `DOMAIN_API_URL` defaults to
  `http://behaviour-service:8000` inside compose, matching the mobile and agent
  experiences.
- **Live feed** — the page subscribes directly to the API's SSE bridge at
  `http://localhost:8000/events/stream` (CORS-enabled) and renders
  `colour.generated` events as they happen — the same event stream the mobile and
  agent experiences consume.

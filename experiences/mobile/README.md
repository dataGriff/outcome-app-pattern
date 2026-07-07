# experiences/mobile — Expo / React Native experience

The **mobile** channel consuming the one behaviour API. Same endpoints as web and
agent: `POST /colours` to generate, `GET /colours/latest`, and the SSE feed at
`GET /events/stream`.

HTTP calls go through a **typed client** (`openapi-fetch` over `src/api/schema.ts`,
generated from the committed OpenAPI contract with `task gen:client`) — the app
cannot call an endpoint or read a field the contract doesn't define. SSE stays a
raw `EventSource`; streams aren't part of the typed surface.

## In the demo (compose)

`docker-compose.yml` builds a **web export** of this Expo app and serves it static
on **http://localhost:8081**. The web export runs the identical React Native code
in a browser — a compose-friendly way to show the mobile channel without a native
toolchain.

The API base URL is baked at build time via `EXPO_PUBLIC_API_URL`
(default `http://localhost:8000`, the host's published API port).

## As a real native app

The web export is **not** proof the native build works. To run it natively:

```bash
cd experiences/mobile
npm install
npx expo start      # then open in Expo Go / a simulator
```

Set `EXPO_PUBLIC_API_URL` to a host reachable from the device (e.g. your machine's
LAN IP) rather than `localhost`.

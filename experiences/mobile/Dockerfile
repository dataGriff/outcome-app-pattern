# Build the Expo web export, then serve it as static files.
# Web export runs the same React Native code in a browser; it is a compose-friendly
# demonstration, not a substitute for a native iOS/Android build (`npx expo start`).
FROM node:20-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
# Baked at build time — the browser reaches the API on the host's published port.
ENV EXPO_PUBLIC_API_URL=http://localhost:8000
RUN npx expo export --platform web

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

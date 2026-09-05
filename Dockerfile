# syntax=docker/dockerfile:1

# ---- build: wrap the game fragment into a standalone HTML document ----------
FROM python:3.12-alpine AS build
WORKDIR /src
COPY build-site.py schnauzer-butterfly-chase.html ./
RUN python build-site.py

# ---- serve: plain nginx, no runtime dependencies --------------------------
FROM nginx:1.27-alpine

# PORT is honoured at start-up, so this runs as-is on Cloud Run, Fly, Render,
# Railway and friends. Override with -e PORT=... anywhere else.
ENV PORT=8080

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /src/site/index.html /usr/share/nginx/html/index.html

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD wget -qO- "http://127.0.0.1:${PORT}/healthz" || exit 1

LABEL org.opencontainers.image.title="Schnauzer Butterfly Chase" \
      org.opencontainers.image.description="A 3D dog-park game: run Orson the giant schnauzer around a dusk-lit park catching butterflies." \
      org.opencontainers.image.licenses="MIT"

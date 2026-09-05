# Schnauzer Butterfly Chase

A 3D dog-park game: run Orson, a giant schnauzer, around a dusk-lit park catching
butterflies before the gates close. Three.js, one HTML file, no build step for the
game itself.

## Layout

| path | what it is |
| --- | --- |
| `schnauzer-butterfly-chase.html` | the game — the only file you edit |
| `build-site.py` | wraps that fragment into a standalone `site/index.html` |
| `Dockerfile` | two stages: run the wrapper, then serve with nginx |
| `nginx.conf.template` | listens on `$PORT`, gzip, no-cache on the page |
| `compose.yaml` | one-command local run |
| `.github/workflows/publish.yml` | builds and pushes `ghcr.io/blaktron/orson-butterflies` on every push to `main` |
| `unraid/orson-butterflies.xml` | dockerMan template for Unraid |

The game is authored as an Artifact fragment (no `<!doctype>`, `<html>`, `<head>`
or `<body>` — the Artifact host supplies those). `build-site.py` lifts the
`<title>` and font `<link>`s into a real `<head>` and wraps the rest, so the same
source file publishes both as an Artifact and as this site.

## Run it locally

```sh
docker build -t orson-butterflies .
docker run --rm -p 8080:8080 orson-butterflies
# → http://localhost:8080
```

or `docker compose up --build`. Podman works identically (`podman build`,
`podman run`); add `--format docker` to the build if you want the `HEALTHCHECK`
preserved, since OCI images drop it.

To iterate on the game without rebuilding the image:

```sh
python3 build-site.py && (cd site && python3 -m http.server 8099)
```

## Publish it

The image listens on `$PORT` (default 8080) and needs no volumes, env vars or
state, so it drops into any container host.

**Pull the published image.** Every push to `main` builds `linux/amd64` and
`linux/arm64` and pushes them to GHCR, tagged `latest` plus the short commit SHA
(and the tag name for `v*` tags):

```sh
docker run -d --name orson-butterflies --restart unless-stopped \
  -p 8080:8080 ghcr.io/blaktron/orson-butterflies:latest
```

If you want to push by hand instead, `docker login ghcr.io` with a token that has
`write:packages` and `docker buildx build --push -t ghcr.io/blaktron/orson-butterflies:latest .`

**Google Cloud Run** — free tier, HTTPS and a URL included:

```sh
gcloud run deploy orson-butterflies \
  --source . --region us-central1 --allow-unauthenticated
```

**Fly.io**:

```sh
fly launch --name orson-butterflies --now   # detects the Dockerfile
```

**Render / Railway / Koyeb**: point them at the repo; they read the `Dockerfile`
and inject `PORT` themselves. Nothing else to configure.

**Your own box**: `docker run -d --restart unless-stopped -p 8080:8080 …` behind
Caddy or nginx for TLS.

## Controls

Keyboard: `W A S D` or the arrow keys to run and steer, `Shift` (or a double-tap
of forward) to sprint, `Space` to pounce, `P` to pause, `M` to mute.

Touch: the controls appear automatically on a coarse pointer, or on the first
touch anywhere. Drag anywhere in the lower-left to raise a floating thumbstick —
push it forward all the way to sprint — and tap the pad on the right to pounce.
Append `?touch=1` to the URL to force the touch layer on a desktop browser.

## Unraid

The image is stateless — no volumes, no config, nothing written to the array —
so it is about as simple as a container gets.

**With the template (easiest).** On the Unraid terminal:

```sh
wget -O /boot/config/plugins/dockerMan/templates-user/my-orson-butterflies.xml \
  https://raw.githubusercontent.com/blaktron/orson-butterflies/main/unraid/orson-butterflies.xml
```

Then **Docker → Add Container**, pick `orson-butterflies` from the *Template*
dropdown, change the port if 8080 is taken, and hit Apply. The container's WebUI
link opens the game.

**By hand.** Docker → Add Container, toggle to Advanced View and fill in:

| field | value |
| --- | --- |
| Name | `orson-butterflies` |
| Repository | `ghcr.io/blaktron/orson-butterflies:latest` |
| Network Type | `Bridge` |
| WebUI | `http://[IP]:[PORT:8080]/` |
| Port | Container `8080` → Host `8080`, TCP |
| Extra Parameters | `--restart unless-stopped` |

No paths, no variables. If you change the host port, change the `[PORT:8080]` in
the WebUI field to match.

**Updating.** Unraid's *Check for Updates* on the Docker tab sees new `latest`
digests as they are published; hit *Update* and it pulls and recreates.

**Reaching it from outside the LAN**, put it behind your existing reverse proxy
(Nginx Proxy Manager, SWAG, Traefik) pointing at `http://TOWER-IP:8080`. The app
serves plain HTTP on purpose and expects TLS to terminate upstream.

## Notes

- The page pulls Three.js from cdnjs and two families from Google Fonts, so the
  browser needs outbound network. To go fully self-contained, vendor
  `three.min.js` and the font files into `site/` and repoint the tags.
- `window.__orson` exposes `{camera, scene, dog, dogState, G}` in the console for
  poking at the running game.
- Nothing is stored server-side; the best scores live in the visitor's
  `localStorage`.

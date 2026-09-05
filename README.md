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

**Push to a registry** (GitHub Container Registry shown):

```sh
echo "$GITHUB_TOKEN" | docker login ghcr.io -u YOUR_USER --password-stdin
docker build -t ghcr.io/YOUR_USER/orson-butterflies:latest .
docker push ghcr.io/YOUR_USER/orson-butterflies:latest
```

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

## Notes

- The page pulls Three.js from cdnjs and two families from Google Fonts, so the
  browser needs outbound network. To go fully self-contained, vendor
  `three.min.js` and the font files into `site/` and repoint the tags.
- `window.__orson` exposes `{camera, scene, dog, dogState, G}` in the console for
  poking at the running game.
- Nothing is stored server-side; the best scores live in the visitor's
  `localStorage`.

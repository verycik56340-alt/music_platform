# Music Platform

A Django-based music platform with a public catalog of artists, albums and tracks.
Listeners stream music through a global audio player, leave rated album reviews and
comment on tracks. Content is managed by admins through Django admin; artists apply
through a moderated registration flow.

## Screenshots

| | |
|:---:|:---:|
| <img src="docs/screenshots/01-home.png" width="480" alt="Home page"> <br><sub>Home — artist grid and latest albums</sub> | <img src="docs/screenshots/02-artist.png" width="480" alt="Artist page"> <br><sub>Artist page — bio, social links, Albums tab</sub> |
| <img src="docs/screenshots/03-artist-tracks.png" width="480" alt="Artist tracks tab"> <br><sub>Artist page — Tracks tab with the track list</sub> | <img src="docs/screenshots/04-album.png" width="480" alt="Album page"> <br><sub>Album page — tracks and a rated review</sub> |
| <img src="docs/screenshots/05-track-player.png" width="480" alt="Track page with player"> <br><sub>Track page — audio player and comments</sub> | <img src="docs/screenshots/06-artist-registration.png" width="480" alt="Artist registration"> <br><sub>Artist registration — a separate role from listener</sub> |

## Features

- **Two registration roles** — listeners sign up via *Register*, would-be artists via *Become Artist*. An artist application is created with `artist_status = pending` and does not grant artist rights yet.
- **Artist moderation** — admins approve or reject pending applications from Django admin bulk actions (*Approve selected users as artists* / *Reject selected artist applications*); approval flips the account to artist and auto-creates its `ArtistProfile`. Logged-in users with a pending application see a warning banner, and a confirmation page explains the waiting state.
- **Albums and tracks** — albums with cover, description and release date; tracks (including singles with no album) with audio files, description and **featuring** links to other artists. Content is managed through the Django admin (albums get an inline track form), and lists appear on the home page, artist pages, and album pages.
- **Artist pages with tabs** — bio, avatar, social links (Spotify, SoundCloud, Telegram, website) and switchable *Albums* / *Tracks* tabs; the tracks tab merges the artist's own tracks with tracks where they are featured.
- **Album reviews with rating** — authenticated users post a review with a numeric rating from 1 to 10 (`MinValueValidator`/`MaxValueValidator`), rendered as `★ 8/10`.
- **Track comments** — authenticated users discuss individual tracks; deleted accounts render as "Deleted user" instead of breaking the page.
- **Global audio player** — a fixed bottom player bar; *Play* buttons on album, artist, and track pages load the track into the same `<audio>` element and keep playing while navigating.
- **Audio file validation** — every uploaded track is checked for allowed extensions (`mp3`, `wav`), a 50 MB size limit, and the real MIME type sniffed with **python-magic** (`audio/mpeg`, `audio/wav`, `audio/x-wav`), so renamed non-audio files are rejected. Image uploads are capped at 10 MB.
- **Brute-force protection** — **django-axes** blocks login attempts (5 failures, 1-hour cool-off) via its middleware and standalone auth backend, and **django-ratelimit** rate-limits hot endpoints per IP: album page 30/h, track page 60/h, registration 5/min.
- **HTMX front-end** — navigation and forms swap only the main content fragment (`hx-get`/`hx-post`), with a `blank.html` partial layout for responses and URL push for full history support.
- **Hardened production settings** — WhiteNoise for static files, HTTPS-only cookies and HSTS when `DEBUG=False`, CSRF trusted origins and host allow-list from environment variables.

## Tech stack

| Component | Version |
|---|---|
| Python | 3.12+ (developed on 3.14) |
| Django | 6.0.7 |
| Database | SQLite (dev) / PostgreSQL via `dj-database-url` + psycopg 3 |
| Server | gunicorn + WhiteNoise |
| Frontend | Bootstrap 5.3.3, HTMX 1.9.12 (CDN), custom dark theme |
| Extras | Pillow, python-magic, django-axes, django-ratelimit, python-dotenv |

## Getting started (local)

```bash
git clone https://github.com/verycik56340-alt/music_platform.git
cd music_platform

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env  # required: sets DEBUG=True for local development

# System library for python-magic (MIME validation of audio files):
#   Linux (Debian/Ubuntu): sudo apt install libmagic1
#   NixOS (temporary shell): nix-shell -p file
#   macOS: brew install libmagic
#   Windows: pip install python-magic-bin

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000 and sign in (or use `/admin/` with the superuser to moderate artists and add albums/tracks).

There is no demo data in the repository (`db.sqlite3` and `media/` are gitignored), so after `createsuperuser` log in to `/admin/` and create an artist (approve their pending application via the bulk action), an album, and a track — otherwise the catalog pages are empty.

## Configuration

All settings come from environment variables loaded by python-dotenv from `.env` (see `.env.example`):

| Variable | Description | Local default | Server |
|---|---|---|---|
| `DEBUG` | Dev mode: SQLite fallback, no HTTPS enforcement, dev `SECRET_KEY` allowed | `True` in `.env.example` | `False` |
| `SECRET_KEY` | Django secret key; required when `DEBUG=False` (no fallback) | insecure dev key built in | required |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` | your domain(s) |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated origins trusted for CSRF (scheme + host) | `http://localhost:8000` | `https://your.domain` |
| `DATABASE_URL` | Database URL; falls back to local `db.sqlite3` | unset (SQLite) | `postgres://user:pass@host:5432/dbname` |
| `SECURE_SSL_REDIRECT` | Force HTTPS redirects; defaults to `on` when `DEBUG=False` | `False` | `True`, or `False` if TLS terminates at nginx |

## Deployment

1. Set `DEBUG=False` and a strong `SECRET_KEY` in the server environment; set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to your domain.
2. Set `DATABASE_URL` to PostgreSQL (psycopg is included in requirements).
3. Collect static files — they are served by WhiteNoise:

   ```bash
   python manage.py collectstatic --noinput
   ```

4. Run the app with gunicorn:

   ```bash
   gunicorn core.wsgi:application
   ```

5. Put **nginx in front for media**: with `DEBUG=False` Django does not serve `/media/` at all, so proxy or alias it to the `media/` directory:

   ```nginx
   location /media/ {
       alias /path/to/music_platform/media/;
   }
   ```

6. If TLS is terminated at nginx (Django receives plain HTTP from the proxy), set `SECURE_SSL_REDIRECT=False` to avoid redirect loops. Django still marks cookies as secure, and `SECURE_PROXY_SSL_HEADER` is configured to trust the `X-Forwarded-Proto` header.

## Project structure

```
music_platform/
├── core/
│   ├── settings.py          # env-driven settings (dotenv, DEBUG, security)
│   ├── urls.py              # admin + auth + app routes, /media/ in dev
│   ├── wsgi.py / asgi.py
├── music/
│   ├── models.py            # CustomUser, ArtistProfile, Album, Track, reviews, comments
│   ├── views.py             # pages, registration, review/comment handling + rate limits
│   ├── urls.py              # public routes
│   ├── forms.py             # registration, review and comment forms
│   ├── admin.py             # content management + artist approve/reject actions
│   ├── templates/           # dark Bootstrap UI (base, home, detail pages)
│   └── migrations/
├── docs/screenshots/
├── requirements.txt
├── .env.example
└── manage.py
```

## Known limitations

- Artists cannot upload content themselves; albums and tracks are managed through Django admin.
- Users can post multiple reviews per album and multiple comments per track (no uniqueness constraint, no edit/delete in the UI).
- Rate limiting and brute-force protection use the default in-process cache, so counters are per gunicorn worker; use Redis or Memcached for multi-worker deployments.

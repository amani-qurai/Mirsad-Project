# Mirsad

Weekly branch-export ingestion for Nakheel Retail that is honest about its own gaps.

## Run it

Needs Docker.

```bash
make up
```

- Web: http://localhost:3000
- API: http://localhost:8000/health

`make down` stops it. If a port is taken, set `DB_PORT`, `API_PORT` or `WEB_PORT` first, e.g. `API_PORT=8001 make up`.

## Develop

Needs Python 3.12 and Node 22.

```bash
python3.12 -m venv .venv
make install
make test
```

`make help` lists every target. Rules for contributors are in `CLAUDE.md`.

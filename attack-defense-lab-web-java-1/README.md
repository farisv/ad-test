# Patch Tuesday: attack-defense CTF lab

Six intentionally vulnerable services run in isolated Docker containers. Four are web
applications (PHP, Go, Node.js, and Java), one C binary is launched per connection by
`socat`, and one C binary owns its listening socket. Each service listens on its assigned
port directly, and Docker publishes those ports on all host interfaces.

## Start the arena

```sh
cp .env.example .env
docker compose up -d --build
docker compose logs -f checker
```

The checker runs immediately and every 60 seconds. For each service it registers a fresh
user, authenticates, stores a new `[A-Z0-9]{31}=` flag through the normal service feature, and
retrieves it. Results are persisted in the `checker-state` volume. A patch passes when
those public workflows continue to work. Run one immediate round with:

```sh
docker compose run --rm -e CHECK_ONCE=1 -e CHECK_INTERVAL=0 checker
```

| Challenge | Address | Intended bug classes |
|---|---|---|
| Paper Trail (PHP) | http://127.0.0.1:8081 | SQL injection, IDOR, arbitrary file read |
| Cipher Notes (Go) | http://127.0.0.1:8082 | logic bug, encryption flaw, hardcoded key |
| Merge Desk (Node.js) | http://127.0.0.1:8083 | NoSQL injection, prototype pollution, command injection/RCE |
| Receipt Room (Java) | http://127.0.0.1:8084 | IDOR, arbitrary file read, hardcoded signing key |
| Parcel Relay (C + socat) | 127.0.0.1:9001 | stack overflow/ret2win, path traversal |
| Beacon Vault (C socket server) | 127.0.0.1:9002 | logic bug, hardcoded master key, format string |

Web services expose `GET /` for usage help and `GET /health`. The binary services print
their protocol banner when connected with `nc`. Source is mounted into images at build
time; edit the relevant challenge directory, rebuild that service, and keep checker logs
green.

This repository contains real vulnerabilities. Use a dedicated CTF host and restrict
access at the cloud firewall when the arena is not in active use.

## Lifecycle

```sh
docker compose ps
docker compose logs --tail=30 checker
docker compose build web-go # rebuild one patched service
docker compose up -d web-go # replace it
docker compose down -v      # delete containers and all challenge/checker data
```

Challenge-specific notes live in each service directory. They describe the feature and
SLA contract without giving exploit payloads.

The bundled checker is also the periodic flag populator: it injects one fresh flag into
every challenge immediately and once per `CHECK_INTERVAL` (60 seconds by default).

# CTF checker simulator dashboard

This portable dashboard targets the six-service Patch Tuesday lab. Every tick it:

1. verifies the previous flag through its legitimate owner account;
2. creates a fresh account and injects a fresh `[A-Z0-9]{31}=` flag through the normal service feature;
3. retrieves the fresh flag through the normal owner workflow;
4. attempts the intended attack path without using the owner's password;
5. records SLA results and every deduplicated stolen flag in SQLite and displays them per tick.

## Run

Install Docker, extract this directory, then run:

```sh
cp .env.example .env
# Edit TARGET_HOST in .env if the challenge server address changed.
docker compose up -d --build
```

Open <http://localhost:8080>. The first tick starts immediately and later ticks run every
60 seconds. Click **Run tick now** for an additional check. History persists in a Docker
volume.

Flag population is periodic: every automatic tick injects one fresh random flag into each
challenge before the attack routines run.

Configuration:

| Variable | Default | Meaning |
|---|---:|---|
| `TARGET_HOST` | `51.158.179.106` | Challenge server hostname or IP, without a scheme |
| `CHECK_INTERVAL` | `60` | Seconds between automatic ticks |
| `WEB_PORT` | `8080` | Dashboard port on your computer |

The attack routines are tailored to this training lab: PHP and Java object authorization,
Go role assignment, Node prototype pollution, the socat service's record traversal,
and the direct C socket service's maintenance key. A stolen result means the flag placed
in that same tick was recovered through the attack path. Attacks that expose a collection
report multiple current and historical flags. After a correct patch, SLA should remain
**UP** and theft should change to **BLOCKED**.

Useful commands:

```sh
docker compose logs -f
docker compose down
docker compose down -v  # also erase history
```

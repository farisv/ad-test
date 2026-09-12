# ctf-web-node-web-node-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-web-node-web-node-1 (`cdaca3107df8`) |
| Image | `ctf-web-node-web-node` |
| Classification | web |
| Languages | JavaScript (2) |
| Ports | 0.0.0.0:8083 → 8083/tcp, :::8083 → 8083/tcp |
| Files inspected | 4 |
| Compose project/service | `ctf-web-node` / `web-node` |
| Compose project containers | 1 |

## Interesting patterns to inspect

These locations matched review-oriented source patterns. Inspect the surrounding code and runtime behavior before drawing conclusions.

| Pattern | File and line | Observed line |
|---|---|---|
| Shell execution | `source/server.js:6` | `const { exec } = require('child_process');` |
| File read | `source/server.js:13` | `data = JSON.parse(fs.readFileSync(DB, 'utf8'));` |
| File write | `source/server.js:19` | `fs.writeFileSync(DB, JSON.stringify(data));` |
| Authorization decision | `source/server.js:53` | `const token = (req.headers.authorization \|\| '').replace(/^Bearer /, '');` |
| Node request input | `source/server.js:53` | `const token = (req.headers.authorization \|\| '').replace(/^Bearer /, '');` |
| Recursive object merge | `source/server.js:62` | `function merge(target, source) { for (const key in source) { if (source[key] && typeof source[key] === 'object') { if (!target[key]) { target[key] = {}; } merge(target[key], source[key]); } else { target[key] = source[key];` |
| Authorization decision | `source/server.js:199` | `if (!user.profile.isAdmin) {` |
| Dynamic code evaluation | `source/server.js:213` | `exec(` |

## Cross-file relationships to trace

Compared definitions, references, and patterns across 4 source file(s). These links identify code paths worth following; they do not assert runtime data flow.

No review-pattern relationship crossed a file boundary.

No defined symbol was referenced from another inspected file.

## Routes and entry points

- `GET / — Node manual HTTP routing, source/server.js:98`
- `GET /api/admin/items — Node manual HTTP routing, source/server.js:198`
- `GET /health — Node manual HTTP routing, source/server.js:94`
- `PATCH /api/profile — Node manual HTTP routing, source/server.js:159`
- `POST /api/items — Node manual HTTP routing, source/server.js:165`
- `POST /api/login — Node manual HTTP routing, source/server.js:135`
- `POST /api/register — Node manual HTTP routing, source/server.js:114`
- `POST /api/render — Node manual HTTP routing, source/server.js:205`

## Package and build context

No recognized package or build manifest was found.

## Native and binary artifacts

No binary artifact was selected.

## Runtime context

- Command: `docker-entrypoint.sh node server.js`
- Working directory: `/app`
- Container user: `node`
- Running processes at collection: 1
- Environment variable names: NODE_VERSION, PATH, YARN_VERSION

Configuration details to review:
- Container root filesystem is writable.
- Writable volume at /data

## Dynamic observations

- Target IP: `51.158.179.106`
- Timeout per operation: 15 seconds

### Web endpoint on TCP 8083

Start URL: `http://51.158.179.106:8083/`

| Status | URL | Type | Bytes | Saved response |
|---:|---|---|---:|---|
| 200 | `http://51.158.179.106:8083/` | text/plain | 70 | [responses/0001-root-003974de34.body](web-8083/responses/0001-root-003974de34.body) |

Captured screenshots:

`http://51.158.179.106:8083/`

![Screenshot of http://51.158.179.106:8083/](web-8083/screenshots/0001-root-003974de34.png)


## Inspected source files

- `source/CHALLENGE.md`
- `source/Dockerfile`
- `source/compose.yaml`
- `source/server.js`

Note: Dumb quick analysis with naive deterministic checking. Only for situational awareness.

# ctf-web-go-web-go-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-web-go-web-go-1 (`72085d0c97f1`) |
| Image | `ctf-web-go-web-go` |
| Classification | web |
| Languages | Go (2) |
| Ports | 0.0.0.0:8082 → 8082/tcp, :::8082 → 8082/tcp |
| Files inspected | 5 |
| Compose project/service | `ctf-web-go` / `web-go` |
| Compose project containers | 1 |

## Interesting patterns to inspect

These locations matched review-oriented source patterns. Inspect the surrounding code and runtime behavior before drawing conclusions.

| Pattern | File and line | Observed line |
|---|---|---|
| Authorization decision | `source/CHALLENGE.md:5` | `backup ciphertext format as long as authenticated users can still request a backup.` |
| File write | `source/main.go:49` | `_ = os.WriteFile("/data/ciphernotes.json", raw, 0600)` |
| File read | `source/main.go:53` | `raw, e := os.ReadFile("/data/ciphernotes.json")` |
| Authorization decision | `source/main.go:89` | `t := strings.TrimPrefix(r.Header.Get("Authorization"), "Bearer ")` |

## Routes and entry points

- `ANY / — Go net/http, source/main.go:246`
- `ANY /api/admin/items — Go net/http, source/main.go:244`
- `ANY /api/backup — Go net/http, source/main.go:245`
- `ANY /api/items — Go net/http, source/main.go:242`
- `ANY /api/items/ — Go net/http, source/main.go:243`
- `ANY /api/login — Go net/http, source/main.go:241`
- `ANY /api/register — Go net/http, source/main.go:240`
- `ANY /health — Go net/http, source/main.go:237`

## Package and build context

### `source/go.mod`

Language family: Go


## Native and binary artifacts

No binary artifact was selected.

## Runtime context

- Command: `/service`
- Working directory: `/`
- Container user: `65534:65534`
- Running processes at collection: 1
- Environment variable names: PATH

Configuration details to review:
- Container root filesystem is writable.
- Writable volume at /data

## Dynamic observations

- Target IP: `51.158.179.106`
- Timeout per operation: 15 seconds

### Web endpoint on TCP 8082

Start URL: `http://51.158.179.106:8082/`

| Status | URL | Type | Bytes | Saved response |
|---:|---|---|---:|---|
| 200 | `http://51.158.179.106:8082/` | text/plain | 58 | [responses/0001-root-b053b6c908.body](web-8082/responses/0001-root-b053b6c908.body) |

Captured screenshots:

`http://51.158.179.106:8082/`

![Screenshot of http://51.158.179.106:8082/](web-8082/screenshots/0001-root-b053b6c908.png)


## Inspected source files

- `source/CHALLENGE.md`
- `source/Dockerfile`
- `source/compose.yaml`
- `source/go.mod`
- `source/main.go`

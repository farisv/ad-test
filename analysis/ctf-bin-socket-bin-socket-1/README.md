Note: Dumb quick analysis with naive deterministic checking. Only for situational awareness.

# ctf-bin-socket-bin-socket-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-bin-socket-bin-socket-1 (`ade4ba08f22a`) |
| Image | `ctf-bin-socket-bin-socket` |
| Classification | binary/network service |
| Classification signals | No static web-specific signal |
| Languages | native C/C++/other (1) |
| Ports | 0.0.0.0:9002 → 9002/tcp, :::9002 → 9002/tcp |
| Files inspected | 4 |
| Compose project/service | `ctf-bin-socket` / `bin-socket` |
| Compose project containers | 1 |

## Interesting patterns to inspect

These locations matched review-oriented source patterns. Inspect the surrounding code and runtime behavior before drawing conclusions.

No configured source pattern matched.

## Routes and entry points

No route was recognized by the static patterns.

## Package and build context

No recognized package or build manifest was found.

## Native and binary artifacts

| File | Language | Architecture | Linking | NX | PIE | RELRO | Canary | Symbols |
|---|---|---|---|---|---|---|---|---|
| `source/server` | native C/C++/other | Advanced Micro Devices X86-64 | dynamic | enabled | disabled | full | not found | not stripped |

## Runtime context

- Command: `/app/server`
- Working directory: `/app`
- Container user: `10002:10002`
- Running processes at collection: 1
- Environment variable names: PATH

Configuration details to review:
- Container root filesystem is writable.
- Writable volume at /data

## Dynamic observations

- Target IP: `51.158.179.106`
- Timeout per operation: 15 seconds

### Network transcripts

| Port | Exit | Received bytes | Transcript |
|---:|---:|---:|---|
| 9002 | 0 | 30 | [nc-9002.txt](nc-9002.txt) |

### Probe notes

- http://51.158.179.106:9002/: PATCH-TUESDAY Beacon Vault v1 
- https://51.158.179.106:9002/: <urlopen error [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:992)>

## Inspected source files

- `source/CHALLENGE.md`
- `source/Dockerfile`
- `source/compose.yaml`

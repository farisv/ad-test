# ctf-web-java-web-java-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-web-java-web-java-1 (`311216cb87bc`) |
| Image | `ctf-web-java-web-java` |
| Classification | binary/network service |
| Languages | Java (2) |
| Ports | 0.0.0.0:8084 → 8084/tcp, :::8084 → 8084/tcp |
| Files inspected | 4 |
| Compose project/service | `ctf-web-java` / `web-java` |
| Compose project containers | 1 |

## Interesting patterns to inspect

These locations matched review-oriented source patterns. Inspect the surrounding code and runtime behavior before drawing conclusions.

| Pattern | File and line | Observed line |
|---|---|---|
| Authorization decision | `source/App.java:116` | `String authorization = exchange` |
| Authorization decision | `source/App.java:118` | `.getFirst("Authorization");` |
| Authorization decision | `source/App.java:120` | `if (authorization == null \|\| !authorization.startsWith("Bearer ")) {` |
| Authorization decision | `source/App.java:124` | `String[] token = authorization.substring(7).split("\\.", 2);` |
| File write | `source/App.java:195` | `Files.write(Path.of("/data/users.db"), userLines);` |
| File write | `source/App.java:196` | `Files.write(Path.of("/data/items.db"), itemLines);` |
| File read | `source/App.java:206` | `for (String line : Files.readAllLines(userFile)) {` |
| File read | `source/App.java:217` | `for (String line : Files.readAllLines(itemFile)) {` |
| Authorization decision | `source/App.java:313` | `// Intentionally vulnerable: authenticated ownership is not checked (IDOR).` |
| File read | `source/App.java:337` | `"{\"content\":\"" + escape(Files.readString(file)) + "\"}"` |
| File write | `source/App.java:417` | `Files.writeString(welcome, "Receipt Room export service\n");` |
| Authorization decision | `source/CHALLENGE.md:4` | `Review object authorization, token trust, and path resolution. Existing user tokens do not` |

## Cross-file relationships to trace

Compared definitions, references, and patterns across 4 source file(s). These links identify code paths worth following; they do not assert runtime data flow.

### Pattern relationships

| Relationship | Files | Locations |
|---|---:|---|
| Authorization decision appears in 2 files | 2 | source/App.java:116; source/App.java:118; source/App.java:120; source/App.java:124; source/App.java:313; source/CHALLENGE.md:4 |
| Identity decisions and stored-object operations appear in separate files | 2 | Authorization decision: source/App.java:116; Authorization decision: source/App.java:118; Authorization decision: source/App.java:120; Authorization decision: source/App.java:124; Authorization decision: source/App.java:313; Authorization decision: source/CHALLENGE.md:4; File read: source/App.java:206; File read: source/App.java:217; File read: source/App.java:337; File write: source/App.java:195; File write: source/App.java:196; File write: source/App.java:417 |

### Symbol relationships

| Symbol | Defined at | Referenced from other files | Files |
|---|---|---|---:|
| `download` | `source/App.java:323` | `source/CHALLENGE.md:3` | 2 |
| `token` | `source/App.java:105` | `source/CHALLENGE.md:4` | 2 |

## Routes and entry points

No route was recognized by the static patterns.

## Package and build context

No recognized package or build manifest was found.

## Native and binary artifacts

No binary artifact was selected.

## Runtime context

- Command: `/__cacert_entrypoint.sh java App`
- Working directory: `/app`
- Container user: `10001:10001`
- Running processes at collection: 1
- Environment variable names: JAVA_HOME, JAVA_VERSION, LANG, LANGUAGE, LC_ALL, PATH

Configuration details to review:
- Container root filesystem is writable.
- Writable volume at /data

## Dynamic observations

- Target IP: `51.158.179.106`
- Timeout per operation: 15 seconds

### Network transcripts

| Port | Exit | Received bytes | Transcript |
|---:|---:|---:|---|
| 8084 | 0 | 0 | [nc-8084.txt](nc-8084.txt) |

## Inspected source files

- `source/App.java`
- `source/CHALLENGE.md`
- `source/Dockerfile`
- `source/compose.yaml`

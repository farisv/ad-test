# ctf-web-php-web-php-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-web-php-web-php-1 (`13f5eac72faf`) |
| Image | `ctf-web-php-web-php` |
| Classification | binary/network service |
| Languages | PHP (2), HTML/templates (1) |
| Ports | 0.0.0.0:8081 → 8081/tcp, :::8081 → 8081/tcp |
| Files inspected | 5 |
| Compose project/service | `ctf-web-php` / `web-php` |
| Compose project containers | 1 |

## Interesting patterns to inspect

These locations matched review-oriented source patterns. Inspect the surrounding code and runtime behavior before drawing conclusions.

| Pattern | File and line | Observed line |
|---|---|---|
| Hardcoded credential or key | `inspect.json:1` | `PHP_CFLAGS=<literal value present>` |
| Hardcoded credential or key | `inspect.json:1` | `PHP_CPPFLAGS=<literal value present>` |
| Hardcoded credential or key | `inspect.json:1` | `PHP_LDFLAGS=<literal value present>` |
| Authorization decision | `source/index.html:13` | `POST /api/items Authorization: Bearer TOKEN` |
| Authorization decision | `source/index.html:15` | `GET /api/items/ID Authorization: Bearer TOKEN` |
| Dynamic code evaluation | `source/router.php:17` | `$db->exec(` |
| Dynamic code evaluation | `source/router.php:21` | `$db->exec(` |
| File write | `source/router.php:27` | `file_put_contents('/data/help.txt', "Paper Trail export service\n");` |
| Dangerous PHP wrapper | `source/router.php:35` | `return json_decode(file_get_contents('php://input'), true) ?: [];` |
| File read | `source/router.php:35` | `return json_decode(file_get_contents('php://input'), true) ?: [];` |
| Authorization decision | `source/router.php:47` | `$header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';` |
| PHP user input | `source/router.php:47` | `$header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';` |
| Direct object identifier | `source/router.php:53` | `$query = db()->prepare('SELECT * FROM users WHERE token = ?');` |
| SQL query | `source/router.php:53` | `$query = db()->prepare('SELECT * FROM users WHERE token = ?');` |
| SSRF-capable request | `source/router.php:55` | `$user = $query->fetch(PDO::FETCH_ASSOC);` |
| PHP user input | `source/router.php:64` | `$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);` |
| PHP user input | `source/router.php:65` | `$method = $_SERVER['REQUEST_METHOD'];` |
| SQL query | `source/router.php:88` | `'INSERT INTO users(username, password, token) VALUES(?, ?, NULL)'` |
| SQL query | `source/router.php:104` | `$sql = "SELECT * FROM users WHERE username = '$name'";` |
| SSRF-capable request | `source/router.php:107` | `$user = db()->query($sql)->fetch(PDO::FETCH_ASSOC);` |
| Direct object identifier | `source/router.php:117` | `$query = db()->prepare('UPDATE users SET token = ? WHERE id = ?');` |
| SQL query | `source/router.php:117` | `$query = db()->prepare('UPDATE users SET token = ? WHERE id = ?');` |
| Direct object identifier | `source/router.php:118` | `$query->execute([$token, $user['id']]);` |
| SQL query | `source/router.php:133` | `'INSERT INTO notes(owner, title, content) VALUES(?, ?, ?)'` |
| Direct object identifier | `source/router.php:135` | `$query->execute([$user['id'], $title, $content]);` |
| Direct object identifier | `source/router.php:143` | `$query = db()->prepare('SELECT id, title, content FROM notes WHERE id = ?');` |
| SQL query | `source/router.php:143` | `$query = db()->prepare('SELECT id, title, content FROM notes WHERE id = ?');` |
| SSRF-capable request | `source/router.php:145` | `$note = $query->fetch(PDO::FETCH_ASSOC);` |
| PHP user input | `source/router.php:156` | `$name = (string) ($_GET['name'] ?? 'help.txt');` |
| File read | `source/router.php:163` | `reply(200, ['name' => $name, 'content' => file_get_contents($target)]);` |
| SSRF-capable request | `source/router.php:163` | `reply(200, ['name' => $name, 'content' => file_get_contents($target)]);` |

## Cross-file relationships to trace

Compared definitions, references, and patterns across 5 source file(s). These links identify code paths worth following; they do not assert runtime data flow.

### Pattern relationships

| Relationship | Files | Locations |
|---|---:|---|
| Authorization decision appears in 2 files | 2 | source/index.html:13; source/index.html:15; source/router.php:47 |
| Identity decisions and stored-object operations appear in separate files | 2 | Authorization decision: source/index.html:13; Authorization decision: source/index.html:15; Authorization decision: source/router.php:47; Direct object identifier: source/router.php:53; Direct object identifier: source/router.php:117; Direct object identifier: source/router.php:118; Direct object identifier: source/router.php:135; Direct object identifier: source/router.php:143; File read: source/router.php:35; File read: source/router.php:163; File write: source/router.php:27; SQL query: source/router.php:53; SQL query: source/router.php:88; SQL query: source/router.php:104; SQL query: source/router.php:117; SQL query: source/router.php:133; SQL query: source/router.php:143 |

No defined symbol was referenced from another inspected file.

## Routes and entry points

No route was recognized by the static patterns.

## Package and build context

No recognized package or build manifest was found.

## Native and binary artifacts

No binary artifact was selected.

## Runtime context

- Command: `docker-php-entrypoint php -S 0.0.0.0:8081 router.php`
- Working directory: `/app`
- Container user: `www-data`
- Running processes at collection: 1
- Environment variable names: GPG_KEYS, PATH, PHPIZE_DEPS, PHP_ASC_URL, PHP_CFLAGS, PHP_CPPFLAGS, PHP_INI_DIR, PHP_LDFLAGS, PHP_SHA256, PHP_URL, PHP_VERSION

Configuration details to review:
- Container root filesystem is writable.
- Writable volume at /data

## Dynamic observations

- Target IP: `51.158.179.106`
- Timeout per operation: 15 seconds

### Network transcripts

| Port | Exit | Received bytes | Transcript |
|---:|---:|---:|---|
| 8081 | 0 | 0 | [nc-8081.txt](nc-8081.txt) |

## Inspected source files

- `source/CHALLENGE.md`
- `source/Dockerfile`
- `source/compose.yaml`
- `source/index.html`
- `source/router.php`

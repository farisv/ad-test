Note: Dumb quick analysis with naive deterministic checking. Only for situational awareness.

# ctf-web-php-web-php-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-web-php-web-php-1 (`13f5eac72faf`) |
| Image | `ctf-web-php-web-php` |
| Classification | web |
| Classification signals | Web technology: PHP built-in web server, 6 static web route(s) recognized |
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

## Routes and entry points

- `ANY /health — PHP manual router, source/router.php:73`
- `GET / — PHP manual router, source/router.php:67`
- `GET /api/export — PHP manual router, source/router.php:154`
- `POST /api/items — PHP manual router, source/router.php:122`
- `POST /api/login — PHP manual router, source/router.php:98`
- `POST /api/register — PHP manual router, source/router.php:77`

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

### Web endpoint on TCP 8081

Start URL: `http://51.158.179.106:8081/`

| Status | URL | Type | Bytes | Saved response |
|---:|---|---|---:|---|
| 200 | `http://51.158.179.106:8081/` | text/html | 419 | [responses/0001-root-f3295fba17.html](web-8081/responses/0001-root-f3295fba17.html) |

Captured screenshots:

`http://51.158.179.106:8081/`

![Screenshot of http://51.158.179.106:8081/](web-8081/screenshots/0001-root-f3295fba17.png)


## Inspected source files

- `source/CHALLENGE.md`
- `source/Dockerfile`
- `source/compose.yaml`
- `source/index.html`
- `source/router.php`

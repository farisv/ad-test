<?php

declare(strict_types=1);

header('Content-Type: application/json');

function db(): PDO
{
    static $db;

    if ($db) {
        return $db;
    }

    $db = new PDO('sqlite:/data/papertrail.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->exec(
        'CREATE TABLE IF NOT EXISTS users '
        . '(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, token TEXT)'
    );
    $db->exec(
        'CREATE TABLE IF NOT EXISTS notes '
        . '(id INTEGER PRIMARY KEY, owner INTEGER, title TEXT, content TEXT)'
    );

    if (!file_exists('/data/help.txt')) {
        file_put_contents('/data/help.txt', "Paper Trail export service\n");
    }

    return $db;
}

function input(): array
{
    return json_decode(file_get_contents('php://input'), true) ?: [];
}

function reply(int $code, array $data): never
{
    http_response_code($code);
    echo json_encode($data);
    exit;
}

function bearer(): string
{
    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    return str_starts_with($header, 'Bearer ') ? substr($header, 7) : '';
}

function user(): array
{
    $query = db()->prepare('SELECT * FROM users WHERE token = ?');
    $query->execute([bearer()]);
    $user = $query->fetch(PDO::FETCH_ASSOC);

    if (!$user) {
        reply(401, ['error' => 'authentication required']);
    }

    return $user;
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$method = $_SERVER['REQUEST_METHOD'];

if ($path === '/' && $method === 'GET') {
    header('Content-Type: text/html');
    readfile(__DIR__ . '/index.html');
    exit;
}

if ($path === '/health') {
    reply(200, ['status' => 'ok']);
}

if ($path === '/api/register' && $method === 'POST') {
    $body = input();
    $name = (string) ($body['username'] ?? '');
    $password = (string) ($body['password'] ?? '');

    if (!preg_match('/^[A-Za-z0-9_]{3,48}$/', $name) || strlen($password) < 6) {
        reply(400, ['error' => 'invalid registration']);
    }

    try {
        $query = db()->prepare(
            'INSERT INTO users(username, password, token) VALUES(?, ?, NULL)'
        );
        $query->execute([$name, password_hash($password, PASSWORD_DEFAULT)]);
    } catch (PDOException $error) {
        reply(409, ['error' => 'username exists']);
    }

    reply(201, ['status' => 'registered']);
}

if ($path === '/api/login' && $method === 'POST') {
    $body = input();
    $name = (string) ($body['username'] ?? '');
    $password = (string) ($body['password'] ?? '');

    // Intentionally vulnerable: attacker-controlled username is concatenated into SQL.
    $sql = "SELECT * FROM users WHERE username = '$name'";

    try {
        $user = db()->query($sql)->fetch(PDO::FETCH_ASSOC);
    } catch (PDOException $error) {
        reply(400, ['error' => 'bad query']);
    }

    if (!$user || !password_verify($password, (string) $user['password'])) {
        reply(403, ['error' => 'bad credentials']);
    }

    $token = bin2hex(random_bytes(24));
    $query = db()->prepare('UPDATE users SET token = ? WHERE id = ?');
    $query->execute([$token, $user['id']]);
    reply(200, ['token' => $token]);
}

if ($path === '/api/items' && $method === 'POST') {
    $user = user();
    $body = input();
    $title = substr((string) ($body['title'] ?? ''), 0, 120);
    $content = (string) ($body['content'] ?? '');

    if ($title === '' || strlen($content) > 4096) {
        reply(400, ['error' => 'invalid note']);
    }

    $query = db()->prepare(
        'INSERT INTO notes(owner, title, content) VALUES(?, ?, ?)'
    );
    $query->execute([$user['id'], $title, $content]);
    reply(201, ['id' => (int) db()->lastInsertId()]);
}

if (preg_match('#^/api/items/(\d+)$#', $path, $matches) && $method === 'GET') {
    user();

    // Intentionally vulnerable: ownership is never checked (IDOR).
    $query = db()->prepare('SELECT id, title, content FROM notes WHERE id = ?');
    $query->execute([(int) $matches[1]]);
    $note = $query->fetch(PDO::FETCH_ASSOC);

    if (!$note) {
        reply(404, ['error' => 'not found']);
    }

    reply(200, $note);
}

if ($path === '/api/export' && $method === 'GET') {
    // Intentionally vulnerable: name is joined without canonicalization (arbitrary file read).
    $name = (string) ($_GET['name'] ?? 'help.txt');
    $target = '/data/' . $name;

    if (!is_file($target)) {
        reply(404, ['error' => 'not found']);
    }

    reply(200, ['name' => $name, 'content' => file_get_contents($target)]);
}

reply(404, ['error' => 'not found']);

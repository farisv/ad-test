#!/usr/bin/env python3
import json, os, secrets, socket, string, time, urllib.error, urllib.request
from datetime import datetime, timezone

INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))
TARGET_HOST = os.getenv('TARGET_HOST', 'host.docker.internal')
FLAG_ALPHABET = string.ascii_uppercase + string.digits
STATE = '/state/results.jsonl'
PLACEMENTS = '/state/placements.json'
WEB = {
    'web-php': f'http://{TARGET_HOST}:8081',
    'web-go': f'http://{TARGET_HOST}:8082',
    'web-node': f'http://{TARGET_HOST}:8083',
    'web-java': f'http://{TARGET_HOST}:8084',
}
BIN = {'bin-socat': (TARGET_HOST, 9001), 'bin-socket': (TARGET_HOST, 9002)}

def request(url, method='GET', body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = 'Bearer ' + token
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=5) as r:
        return json.loads(r.read())

def make_flag(service, nonce):
    del service, nonce
    return ''.join(secrets.choice(FLAG_ALPHABET) for _ in range(31)) + '='

def check_web(service, base, nonce, flag):
    user, password = f'sla_{nonce}', secrets.token_urlsafe(14)
    assert request(base + '/health')['status'] == 'ok'
    request(base + '/api/register', 'POST', {'username': user, 'password': password})
    token = request(base + '/api/login', 'POST', {'username': user, 'password': password})['token']
    created = request(base + '/api/items', 'POST', {'title': 'SLA probe', 'content': flag}, token)
    item = request(base + '/api/items/' + str(created['id']), token=token)
    assert item['content'] == flag and item['title'] == 'SLA probe'
    return {'user': user, 'password': password, 'item': created['id'], 'flag': flag}

def verify_web(base, record):
    token = request(base + '/api/login', 'POST', {'username': record['user'], 'password': record['password']})['token']
    item = request(base + '/api/items/' + str(record['item']), token=token)
    assert item['content'] == record['flag']

def talk(host, port, commands):
    with socket.create_connection((host, port), timeout=5) as s:
        stream = s.makefile('rwb', buffering=0)
        banner = stream.readline().decode(errors='replace').strip()
        replies = []
        for command in commands:
            stream.write((command + '\n').encode())
            replies.append(stream.readline().decode(errors='replace').strip())
        return banner, replies

def check_binary(service, endpoint, nonce, flag):
    user, password, key = f'sla{nonce}', secrets.token_hex(8), f'probe{nonce}'
    banner, replies = talk(*endpoint, [f'REGISTER {user} {password}', f'LOGIN {user} {password}', f'PUT {key} {flag}', f'GET {key}', 'QUIT'])
    assert banner.startswith('PATCH-TUESDAY')
    assert replies[0] in ('OK registered', 'ERR exists')
    assert replies[1] == 'OK authenticated'
    assert replies[2] == 'OK stored'
    assert replies[3] == 'VALUE ' + flag
    return {'user': user, 'password': password, 'key': key, 'flag': flag}

def verify_binary(endpoint, record):
    _, replies = talk(*endpoint, [f"LOGIN {record['user']} {record['password']}", f"GET {record['key']}", 'QUIT'])
    assert replies[0] == 'OK authenticated'
    assert replies[1] == 'VALUE ' + record['flag']

def load_placements():
    try:
        with open(PLACEMENTS, encoding='utf-8') as source:
            return json.load(source)
    except (OSError, ValueError):
        return {}

def save_placements(placements):
    temporary = PLACEMENTS + '.new'
    with open(temporary, 'w', encoding='utf-8') as output:
        json.dump(placements, output)
    os.replace(temporary, PLACEMENTS)

def round_once():
    nonce = str(int(time.time())) + secrets.token_hex(3)
    timestamp = datetime.now(timezone.utc).isoformat()
    results, previous, current = [], load_placements(), {}
    for service, endpoint in {**WEB, **BIN}.items():
        started = time.monotonic()
        try:
            if service in previous:
                if service in WEB: verify_web(endpoint, previous[service])
                else: verify_binary(endpoint, previous[service])
            flag = make_flag(service, nonce)
            detail = check_web(service, endpoint, nonce, flag) if service in WEB else check_binary(service, endpoint, nonce, flag)
            current[service] = detail
            result = {'time': timestamp, 'service': service, 'status': 'UP', 'previous_flag_verified': service in previous, 'latency_ms': round((time.monotonic()-started)*1000), 'user': detail['user'], 'item': detail.get('item', detail.get('key'))}
        except Exception as exc:
            result = {'time': timestamp, 'service': service, 'status': 'DOWN', 'error': f'{type(exc).__name__}: {exc}'}
        results.append(result)
        print(json.dumps(result), flush=True)
    try:
        save_placements({**previous, **current})
        with open(STATE, 'a', encoding='utf-8') as out:
            for result in results: out.write(json.dumps(result) + '\n')
    except OSError as exc:
        print(json.dumps({'status':'WARN', 'error':f'cannot persist checker state: {exc}'}), flush=True)
    return all(r['status'] == 'UP' for r in results)

if __name__ == '__main__':
    while True:
        ok = round_once()
        if os.getenv('CHECK_ONCE') == '1': raise SystemExit(0 if ok else 1)
        time.sleep(max(1, INTERVAL))

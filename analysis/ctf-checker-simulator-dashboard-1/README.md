# ctf-checker-simulator-dashboard-1

This report combines static inspection and dynamic observations. Pattern names are neutral review cues, not conclusions.

## Overview

| Field | Value |
|---|---|
| Container | ctf-checker-simulator-dashboard-1 (`f97e5190eea0`) |
| Image | `ctf-checker-simulator-dashboard` |
| Classification | binary/network service |
| Languages | Python (2), JavaScript (1), HTML/templates (1) |
| Ports | 0.0.0.0:8080 → 8080/tcp, :::8080 → 8080/tcp |
| Files inspected | 8 |
| Compose project/service | `ctf-checker-simulator` / `dashboard` |
| Compose project containers | 1 |

## Interesting patterns to inspect

These locations matched review-oriented source patterns. Inspect the surrounding code and runtime behavior before drawing conclusions.

| Pattern | File and line | Observed line |
|---|---|---|
| Authorization decision | `source/README.md:36` | `The attack routines are tailored to this training lab: PHP and Java object authorization,` |
| SSRF-capable request | `source/app.py:12` | `import urllib.request` |
| Raw SQL execution | `source/app.py:44` | `db.execute('PRAGMA journal_mode=WAL')` |
| Raw SQL execution | `source/app.py:74` | `columns = {row[1] for row in db.execute('PRAGMA table_info(results)')}` |
| Raw SQL execution | `source/app.py:76` | `db.execute("ALTER TABLE results ADD COLUMN stolen_flags TEXT NOT NULL DEFAULT '[]'")` |
| Authorization decision | `source/app.py:84` | `headers['Authorization'] = 'Bearer ' + token` |
| SSRF-capable request | `source/app.py:85` | `request = urllib.request.Request(url, data=payload, headers=headers, method=method)` |
| SSRF-capable request | `source/app.py:87` | `with urllib.request.urlopen(request, timeout=6) as response:` |
| Flag-like literal | `source/app.py:127` | `key = f'flag{nonce}'` |
| Authorization decision | `source/app.py:134` | `if replies[1] != 'OK authenticated' or replies[2] != 'OK stored' or replies[3] != 'VALUE ' + flag:` |
| Authorization decision | `source/app.py:151` | `if replies[0] != 'OK authenticated' or replies[1] != 'VALUE ' + placement['flag']:` |
| Authorization decision | `source/app.py:181` | `http_json('web-node', '/api/profile', 'PATCH', {'__proto__': {'isAdmin': True}}, token)` |
| Prototype pollution primitive | `source/app.py:181` | `http_json('web-node', '/api/profile', 'PATCH', {'__proto__': {'isAdmin': True}}, token)` |
| Raw SQL execution | `source/app.py:255` | `row = db.execute('SELECT username,password,item_key,flag FROM placements WHERE service=?', (service,)).fetchone()` |
| SQL query | `source/app.py:255` | `row = db.execute('SELECT username,password,item_key,flag FROM placements WHERE service=?', (service,)).fetchone()` |
| Raw SQL execution | `source/app.py:260` | `db.execute('''INSERT INTO placements(service,username,password,item_key,flag) VALUES(?,?,?,?,?)` |
| SQL query | `source/app.py:260` | `db.execute('''INSERT INTO placements(service,username,password,item_key,flag) VALUES(?,?,?,?,?)` |
| Raw SQL execution | `source/app.py:264` | `db.execute('''INSERT OR IGNORE INTO placement_history(service,username,item_key,flag)` |
| Raw SQL execution | `source/app.py:276` | `tick_id = db.execute('INSERT INTO ticks(started_at,target) VALUES(?,?)', (now(), TARGET)).lastrowid` |
| SQL query | `source/app.py:276` | `tick_id = db.execute('INSERT INTO ticks(started_at,target) VALUES(?,?)', (now(), TARGET)).lastrowid` |
| Raw SQL execution | `source/app.py:300` | `db.execute('''INSERT INTO results(tick_id,service,sla_ok,steal_ok,previous_verified,` |
| SQL query | `source/app.py:300` | `db.execute('''INSERT INTO results(tick_id,service,sla_ok,steal_ok,previous_verified,` |
| Raw SQL execution | `source/app.py:306` | `db.execute('UPDATE ticks SET finished_at=?,duration_ms=? WHERE id=?',` |
| SQL query | `source/app.py:306` | `db.execute('UPDATE ticks SET finished_at=?,duration_ms=? WHERE id=?',` |
| Raw SQL execution | `source/app.py:321` | `ticks = [dict(row) for row in db.execute('SELECT * FROM ticks ORDER BY id DESC LIMIT 100')]` |
| SQL query | `source/app.py:321` | `ticks = [dict(row) for row in db.execute('SELECT * FROM ticks ORDER BY id DESC LIMIT 100')]` |
| Raw SQL execution | `source/app.py:323` | `tick['results'] = [dict(row) for row in db.execute('''SELECT service,sla_ok,steal_ok,` |
| SQL query | `source/app.py:323` | `tick['results'] = [dict(row) for row in db.execute('''SELECT service,sla_ok,steal_ok, previous_verified,latency_ms,stolen_count,stolen_flags,sla_error,steal_error FROM results WHERE tick_id=? ORDER BY service''', (tick['id'],))]` |
| Direct object identifier | `source/static/app.js:2` | `const cards=document.querySelector('#cards'),history=document.querySelector('#history'),run=document.querySelector('#run');` |
| SQL string construction | `source/static/app.js:7` | `document.querySelector('#target').textContent=`Target ${data.target}`;` |
| SQL string construction | `source/static/app.js:8` | `document.querySelector('#clock').textContent=`Every ${data.interval}s · next in ${data.runtime.next_run_in??'…'}s`;` |
| Potential XSS sink | `source/static/app.js:9` | `const rt=document.querySelector('#runtime');rt.className='pill '+(data.runtime.running?'running':'');rt.innerHTML=`<span class="dot"></span>${data.runtime.running?'Tick running':'Scheduler active'}`;run.disabled=data.runtime.running;` |
| SQL string construction | `source/static/app.js:9` | `const rt=document.querySelector('#runtime');rt.className='pill '+(data.runtime.running?'running':'');rt.innerHTML=`<span class="dot"></span>${data.runtime.running?'Tick running':'Scheduler active'}`;run.disabled=data.runtime.running;` |
| Potential XSS sink | `source/static/app.js:10` | `const newest=data.ticks[0]?.results\|\|[];last=Object.fromEntries(newest.map(x=>[x.service,x]));cards.innerHTML='';` |
| Potential XSS sink | `source/static/app.js:11` | `for(const [id,meta] of Object.entries(data.services)){const r=last[id];const el=document.createElement('article');el.className='card';el.innerHTML=`<h2>${safe(meta.name)}</h2><div class="kind">${safe(id)} · :${meta.port} · ${safe(meta.attac` |
| Potential XSS sink | `source/static/app.js:12` | `if(!data.ticks.length)return;history.innerHTML='';` |
| Potential XSS sink | `source/static/app.js:13` | `for(const tick of data.ticks){const results=tick.results\|\|[],up=results.filter(r=>r.sla_ok).length,stolen=results.filter(r=>r.steal_ok).length,errors=results.filter(r=>r.sla_error\|\|r.steal_error).map(r=>`${r.service}: ${r.sla_error\|\|''}${r.` |
| SSRF-capable request | `source/static/app.js:15` | `async function refresh(){try{const r=await fetch('/api/status',{cache:'no-store'});render(await r.json())}catch(e){document.querySelector('#runtime').textContent='Dashboard API unavailable'}}` |
| SSRF-capable request | `source/static/app.js:16` | `run.onclick=async()=>{run.disabled=true;await fetch('/api/run',{method:'POST'});setTimeout(refresh,300)};` |

## Cross-file relationships to trace

Compared definitions, references, and patterns across 8 source file(s). These links identify code paths worth following; they do not assert runtime data flow.

### Pattern relationships

| Relationship | Files | Locations |
|---|---:|---|
| Authorization decision appears in 2 files | 2 | source/README.md:36; source/app.py:84; source/app.py:134; source/app.py:151; source/app.py:181 |
| SSRF-capable request appears in 2 files | 2 | source/app.py:12; source/app.py:85; source/app.py:87; source/static/app.js:15; source/static/app.js:16 |
| Request handling and data access appear in separate files | 2 | Direct object identifier: source/static/app.js:2; Raw SQL execution: source/app.py:44; Raw SQL execution: source/app.py:74; Raw SQL execution: source/app.py:76; Raw SQL execution: source/app.py:255; Raw SQL execution: source/app.py:260; Raw SQL execution: source/app.py:264; Raw SQL execution: source/app.py:276; Raw SQL execution: source/app.py:300; Raw SQL execution: source/app.py:306; Raw SQL execution: source/app.py:321; Raw SQL execution: source/app.py:323; SQL query: source/app.py:255; SQL query: source/app.py:260; SQL query: source/app.py:276; SQL query: source/app.py:300; SQL query: source/app.py:306; SQL query: source/app.py:321; SQL query: source/app.py:323; SQL string construction: source/static/app.js:7 |
| Identity decisions and stored-object operations appear in separate files | 3 | Authorization decision: source/README.md:36; Authorization decision: source/app.py:84; Authorization decision: source/app.py:134; Authorization decision: source/app.py:151; Authorization decision: source/app.py:181; Direct object identifier: source/static/app.js:2; Raw SQL execution: source/app.py:44; Raw SQL execution: source/app.py:74; Raw SQL execution: source/app.py:76; Raw SQL execution: source/app.py:255; Raw SQL execution: source/app.py:260; Raw SQL execution: source/app.py:264; Raw SQL execution: source/app.py:276; Raw SQL execution: source/app.py:300; Raw SQL execution: source/app.py:306; Raw SQL execution: source/app.py:321; Raw SQL execution: source/app.py:323; SQL query: source/app.py:255; SQL query: source/app.py:260; SQL query: source/app.py:276 |

No defined symbol was referenced from another inspected file.

## Routes and entry points

No route was recognized by the static patterns.

## Package and build context

No recognized package or build manifest was found.

## Native and binary artifacts

No binary artifact was selected.

## Runtime context

- Command: `python app.py`
- Working directory: `/app`
- Container user: `65534:65534`
- Running processes at collection: 1
- Environment variable names: CHECK_INTERVAL, DB_PATH, GPG_KEY, PATH, PYTHON_SHA256, PYTHON_VERSION, TARGET_HOST, WEB_PORT

Configuration details to review:
- Container root filesystem is writable.
- Writable volume at /data

## Dynamic observations

- Target IP: `51.158.179.106`
- Timeout per operation: 15 seconds

### Network transcripts

| Port | Exit | Received bytes | Transcript |
|---:|---:|---:|---|
| 8080 | 0 | 0 | [nc-8080.txt](nc-8080.txt) |

## Inspected source files

- `source/.dockerignore`
- `source/.env.example`
- `source/Dockerfile`
- `source/README.md`
- `source/app.py`
- `source/compose.yaml`
- `source/static/app.js`
- `source/static/index.html`

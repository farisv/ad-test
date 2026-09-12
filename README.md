# Docker service analysis

Generated deterministically from the collected container application directories. No AI model or network intelligence source is used.

- Source root: `.`
- Host: `collector host`
- Captured at: `current repository state`
- Services: 9

| Service | Type | Languages | Ports | Files inspected | Interesting patterns | Cross-file links | Processes | Containers in project | Database | Technology |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| [ctf-bin-socat-bin-socat-1](analysis/ctf-bin-socat-bin-socat-1/README.md) | binary/network service | native C/C++/other (1) | 0.0.0.0:9001 → 9001/tcp, :::9001 → 9001/tcp | 4 | 0 | 0 | 1 | 1 | No | socat |
| [ctf-bin-socket-bin-socket-1](analysis/ctf-bin-socket-bin-socket-1/README.md) | binary/network service | native C/C++/other (1) | 0.0.0.0:9002 → 9002/tcp, :::9002 → 9002/tcp | 4 | 0 | 0 | 1 | 1 | No | Unknown |
| [ctf-checker-checker-1](analysis/ctf-checker-checker-1/README.md) | background/utility service | Python (2) | None | 4 | 7 | 0 | 1 | 1 | No | socat |
| [ctf-checker-simulator-dashboard-1](analysis/ctf-checker-simulator-dashboard-1/README.md) | binary/network service | Python (2), JavaScript (1), HTML/templates (1) | 0.0.0.0:8080 → 8080/tcp, :::8080 → 8080/tcp | 8 | 39 | 4 | 1 | 1 | SQLite | socat |
| [ctf-download-server-files-1](analysis/ctf-download-server-files-1/README.md) | web | Python (1) | 0.0.0.0:8090 → 8090/tcp, :::8090 → 8090/tcp | 1 | 0 | 0 | 1 | 1 | No | Python standard-library HTTP server |
| [ctf-web-go-web-go-1](analysis/ctf-web-go-web-go-1/README.md) | web | Go (2) | 0.0.0.0:8082 → 8082/tcp, :::8082 → 8082/tcp | 5 | 4 | 3 | 1 | 1 | No | Unknown |
| [ctf-web-java-web-java-1](analysis/ctf-web-java-web-java-1/README.md) | binary/network service | Java (2) | 0.0.0.0:8084 → 8084/tcp, :::8084 → 8084/tcp | 4 | 12 | 4 | 1 | 1 | No | Java runtime |
| [ctf-web-node-web-node-1](analysis/ctf-web-node-web-node-1/README.md) | web | JavaScript (2) | 0.0.0.0:8083 → 8083/tcp, :::8083 → 8083/tcp | 4 | 8 | 0 | 1 | 1 | No | Node.js HTTP server, Node.js runtime |
| [ctf-web-php-web-php-1](analysis/ctf-web-php-web-php-1/README.md) | binary/network service | PHP (2), HTML/templates (1) | 0.0.0.0:8081 → 8081/tcp, :::8081 → 8081/tcp | 5 | 31 | 2 | 1 | 1 | SQLite | Unknown |

“Subservices” is the number of captured containers sharing the same Docker Compose project label. “Processes” comes from `docker top` at collection time. File, route, technology, database, and pattern results are static heuristics and may contain false positives or miss runtime-generated behavior.

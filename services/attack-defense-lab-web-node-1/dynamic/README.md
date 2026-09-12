# attack-defense-lab-web-node-1 dynamic analysis

This report records bounded observations made from the analyzer machine. It does not submit forms, authenticate, or scan ports that were absent from the captured Docker metadata.

- Vulnbox IP: `51.158.179.106`
- Timeout per operation: 15 seconds
- Crawl page/depth limits: 500 / 10
- Screenshot limit: 100 per service

## Web crawling and screenshots

### TCP 8083

Start URL: `http://51.158.179.106:8083/`

Observed 1 page result(s); discovered 1 unique same-origin URL(s). Page limit reached: False.

| Depth | Status | URL | Type | Bytes | SHA-256 | Saved response | Screenshot | Response headers / error |
|---:|---:|---|---|---:|---|---|---|---|
| 0 | 200 | `http://51.158.179.106:8083/` | text/plain | 70 | `db71031dd9b188cb288def73693d6e219da88dcd82817277d366833ae9b40158` | [responses/0001-root-003974de34.body](web-8083/responses/0001-root-003974de34.body) | [screenshots/0001-root-003974de34.png](web-8083/screenshots/0001-root-003974de34.png) | Connection: close; Date: Sat, 12 Sep 2026 22:27:25 GMT; Transfer-Encoding: chunked; content-type: text/plain |

## Binary/network transcripts

No `nc` transcript was required.

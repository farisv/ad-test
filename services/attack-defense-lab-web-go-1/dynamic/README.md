# attack-defense-lab-web-go-1 dynamic analysis

This report records bounded observations made from the analyzer machine. It does not submit forms, authenticate, or scan ports that were absent from the captured Docker metadata.

- Vulnbox IP: `51.158.179.106`
- Timeout per operation: 15 seconds
- Crawl page/depth limits: 500 / 10
- Screenshot limit: 100 per service

## Web crawling and screenshots

### TCP 8082

Start URL: `http://51.158.179.106:8082/`

Observed 1 page result(s); discovered 1 unique same-origin URL(s). Page limit reached: False.

| Depth | Status | URL | Type | Bytes | SHA-256 | Saved response | Screenshot | Response headers / error |
|---:|---:|---|---|---:|---|---|---|---|
| 0 | 200 | `http://51.158.179.106:8082/` | text/plain | 58 | `8216317cf2d026d797a5b7a19cbd59cbe2de4c449c71c234f9e6b5eab70fbaf2` | [responses/0001-root-b053b6c908.body](web-8082/responses/0001-root-b053b6c908.body) | [screenshots/0001-root-b053b6c908.png](web-8082/screenshots/0001-root-b053b6c908.png) | Connection: close; Content-Length: 58; Content-Type: text/plain; Date: Sat, 12 Sep 2026 22:27:23 GMT |

## Binary/network transcripts

No `nc` transcript was required.

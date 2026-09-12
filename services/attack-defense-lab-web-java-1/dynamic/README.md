# attack-defense-lab-web-java-1 dynamic analysis

This report records bounded observations made from the analyzer machine. It does not submit forms, authenticate, or scan ports that were absent from the captured Docker metadata.

- Vulnbox IP: `51.158.179.106`
- Timeout per operation: 15 seconds
- Crawl page/depth limits: 500 / 10
- Screenshot limit: 100 per service

## Web crawling and screenshots

### TCP 8084

Start URL: `http://51.158.179.106:8084/`

Observed 1 page result(s); discovered 1 unique same-origin URL(s). Page limit reached: False.

| Depth | Status | URL | Type | Bytes | SHA-256 | Saved response | Screenshot | Response headers / error |
|---:|---:|---|---|---:|---|---|---|---|
| 0 | 200 | `http://51.158.179.106:8084/` | application/json | 98 | `1ec265ceb8c3b27f6d8ebee769b0c1139e93c549fe7d2aa27e0c4ce001179a71` | [responses/0001-root-2839c9b8c3.body](web-8084/responses/0001-root-2839c9b8c3.body) | [screenshots/0001-root-2839c9b8c3.png](web-8084/screenshots/0001-root-2839c9b8c3.png) | Content-length: 98; Content-type: application/json; Date: Sat, 12 Sep 2026 22:27:24 GMT |

## Binary/network transcripts

No `nc` transcript was required.

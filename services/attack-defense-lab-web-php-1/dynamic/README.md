# attack-defense-lab-web-php-1 dynamic analysis

This report records bounded observations made from the analyzer machine. It does not submit forms, authenticate, or scan ports that were absent from the captured Docker metadata.

- Vulnbox IP: `51.158.179.106`
- Timeout per operation: 15 seconds
- Crawl page/depth limits: 500 / 10
- Screenshot limit: 100 per service

## Web crawling and screenshots

### TCP 8081

Start URL: `http://51.158.179.106:8081/`

Observed 1 page result(s); discovered 1 unique same-origin URL(s). Page limit reached: False.

| Depth | Status | URL | Type | Bytes | SHA-256 | Saved response | Screenshot | Response headers / error |
|---:|---:|---|---|---:|---|---|---|---|
| 0 | 200 | `http://51.158.179.106:8081/` | text/html | 419 | `cea996dd77986614cab0ae143fdd527b59108b6c57cd6d857a5574049bf2ed61` | [responses/0001-root-f3295fba17.html](web-8081/responses/0001-root-f3295fba17.html) | [screenshots/0001-root-f3295fba17.png](web-8081/screenshots/0001-root-f3295fba17.png) | Connection: close; Content-type: text/html;charset=UTF-8; Date: Sat, 12 Sep 2026 22:27:26 GMT; Host: 51.158.179.106:8081; X-Powered-By: PHP/8.4.25 |

## Binary/network transcripts

No `nc` transcript was required.

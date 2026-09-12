# ctf-download-server-files-1 dynamic analysis

This report records bounded observations made from the analyzer machine. It does not submit forms, authenticate, or scan ports that were absent from the captured Docker metadata.

- Vulnbox IP: `51.158.179.106`
- Timeout per operation: 15 seconds
- Crawl page/depth limits: 500 / 10
- Screenshot limit: 100 per service

## Web crawling and screenshots

### TCP 8090

Start URL: `http://51.158.179.106:8090/`

Observed 3 page result(s); discovered 3 unique same-origin URL(s). Page limit reached: False.

| Depth | Status | URL | Type | Bytes | SHA-256 | Saved response | Screenshot | Response headers / error |
|---:|---:|---|---|---:|---|---|---|---|
| 0 | 200 | `http://51.158.179.106:8090/` | text/html | 325 | `5519c112b6f88b2a2c94e63d65833f8751d95a46b1ac44e3021a15a1bf1a03f9` | [responses/0001-root-c5c8ef0ff8.html](web-8090/responses/0001-root-c5c8ef0ff8.html) | [screenshots/0001-root-c5c8ef0ff8.png](web-8090/screenshots/0001-root-c5c8ef0ff8.png) | Content-Length: 325; Content-type: text/html; charset=utf-8; Date: Sat, 12 Sep 2026 22:27:27 GMT; Server: SimpleHTTP/0.6 Python/3.13.15 |
| 1 | 200 | `http://51.158.179.106:8090/ctf-checker-simulator.zip` | application/zip | 10543 | `c466b113ed97192ba3c7aace4de6685b485c654761d8735dfb687850edf28617` | [responses/0002-ctf-checker-simulator.zip-e36e64140c.body](web-8090/responses/0002-ctf-checker-simulator.zip-e36e64140c.body) | chromium timeout | Content-Length: 10543; Content-type: application/zip; Date: Sat, 12 Sep 2026 22:27:28 GMT; Last-Modified: Sat, 12 Sep 2026 16:39:41 GMT; Server: SimpleHTTP/0.6 Python/3.13.15 |
| 1 | 200 | `http://51.158.179.106:8090/ctf-service-kit.zip` | application/zip | 41011 | `99b1750d15964a82fa09f5d3c216ccaeaaed7a98bc0765be9118bc87f2933499` | [responses/0003-ctf-service-kit.zip-4151eaae29.body](web-8090/responses/0003-ctf-service-kit.zip-4151eaae29.body) | chromium timeout | Content-Length: 41011; Content-type: application/zip; Date: Sat, 12 Sep 2026 22:27:58 GMT; Last-Modified: Sat, 12 Sep 2026 18:19:41 GMT; Server: SimpleHTTP/0.6 Python/3.13.15 |

## Binary/network transcripts

No `nc` transcript was required.

# ctf-checker-simulator-dashboard-1 dynamic analysis

This report records bounded observations made from the analyzer machine. It does not submit forms, authenticate, or scan ports that were absent from the captured Docker metadata.

- Vulnbox IP: `51.158.179.106`
- Timeout per operation: 15 seconds
- Crawl page/depth limits: 500 / 10
- Screenshot limit: 100 per service

## Web crawling and screenshots

No endpoint classified as web produced an HTTP response.

## Binary/network transcripts

| Port | Exit | Received bytes | Transcript | Error |
|---:|---:|---:|---|---|
| 8080 | 0 | 0 | [nc-8080.txt](nc-8080.txt) | Connection to 51.158.179.106 8080 port [tcp/*] succeeded!  |

# attack-defense-lab-bin-socat-1 dynamic analysis

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
| 9001 | 0 | 30 | [nc-9001.txt](nc-9001.txt) | Connection to 51.158.179.106 9001 port [tcp/*] succeeded!  |

## Probe errors and fallbacks

- http://51.158.179.106:9001/: PATCH-TUESDAY Parcel Relay v1 
- https://51.158.179.106:9001/: <urlopen error [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:992)>

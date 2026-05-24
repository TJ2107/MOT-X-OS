import urllib.request, json, sys
url = 'http://127.0.0.1:8000/api/status'
try:
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.load(r)
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print('ERROR', repr(e))
    sys.exit(2)

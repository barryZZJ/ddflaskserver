import requests as r

resp = r.post("http://ddflaskserver.ddasus.barryzzj.top:22100/test-put")
print(resp.status_code)
print(resp.text)
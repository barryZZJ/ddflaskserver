import requests
import requests as r

headers = {
    'Content-Type': 'application/json',
    'Authorization': f"Basic YmFycnk6RzhwOU1FVDNHZw==",
}

resp = requests.request('POST', 'http://', headers=headers, data=json.dumps(payload))

# resp = r.post("http://ddflaskserver.ddasus.barryzzj.top:22100/test-put")
# print(resp.status_code)
# print(resp.text)
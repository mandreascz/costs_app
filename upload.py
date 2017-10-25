import requests
import json
import pandas as pd

url = 'http://127.0.0.1:5000/uploader'
file = {'file': open('receipts/tesco/1.jpg', 'rb')}
r = requests.post(url, files=file)
print(pd.DataFrame(json.loads(r.content)['data']))

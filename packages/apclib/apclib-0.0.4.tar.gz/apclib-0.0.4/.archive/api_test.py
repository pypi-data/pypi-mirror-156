#%%
import requests
import json
import datetime

#%%
timestamp = datetime.datetime.utcnow().isoformat()
tags = {
    "u1":{"value":1,"timestamp":timestamp,"quality":"good"},
    "u2":{"value":2,"timestamp":timestamp,"quality":"good"},
    "y1":{"value":3,"timestamp":timestamp,"quality":"good"},
    "y2":{"value":4,"timestamp":timestamp,"quality":"good"}
}

requests.post('http://127.0.0.1:5000/opc/update_tags', json=tags)
response = requests.get('http://127.0.0.1:5000/opc/get_tags')
print (json.dumps(response.json(),indent=4))

tags = {
    "y1":{"value":30,"timestamp":timestamp,"quality":"bad"},
}
requests.post('http://127.0.0.1:5000/opc/update_tags', json=tags)
response = requests.get('http://127.0.0.1:5000/opc/get_tags')
print (json.dumps(response.json(),indent=4))

# %%

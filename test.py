import requests

data = {
    "start_lie": "Tee",
    "start_distance": 300,
    "end_lie": "Fairway",
    "end_distance": 100
}

res = requests.post("http://127.0.0.1:5000/calculate", json=data)
print(res.json())

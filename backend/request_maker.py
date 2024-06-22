import requests

base_url = "http://127.0.0.1:5000"

data = {
    "input": "https://docs.google.com/spreadsheets/d/14dmjeOPJnuxF3JS985SdKd0rcKYoKR5cCpiMlvSXTrQ/edit?usp=sharing"
}
response = requests.post(base_url+"/ingest", json=data)
print(response.status_code)
print(response.json())
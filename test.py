import requests

try:
    response = requests.get("https://huggingface.co", proxies={})
    print("Status code:", response.status_code)
except Exception as e:
    print("Error:", e)

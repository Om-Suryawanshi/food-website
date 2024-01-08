import requests

url = 'http://192.168.149.80/reset-password'
headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7,zh-CN;q=0.6,zh;q=0.5,mr;q=0.4,af;q=0.3',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'pragma': 'no-cache',
    'referer': 'http://192.168.149.80/admin',  # Manually set the Referer header
}

data = {"username": "admin"}

try:
    response = requests.post(url, headers=headers, json=data, cookies={"cookie-name": "cookie-value"})
    response.raise_for_status()

    # Process the response if needed
    print(response.text)

except requests.exceptions.RequestException as error:
    print('Error during request:', error)

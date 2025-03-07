import requests

data = {
    "abcd": "EFGH",
    "ijkl": "MNOP",
}

response = requests.post(
    "https://localhost:8089/services/echo_persistent", data=data, verify=False, auth=("admin", "splunkdev")
)

print(response.content)
print(response.status_code)

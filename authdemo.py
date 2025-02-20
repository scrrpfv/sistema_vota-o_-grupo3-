import requests

url = "http://localhost:5000"

nome = 'claudio'
query_string = f'/?nome={nome}'

get_response = requests.get(url+nome)
print("Response:", get_response.text)

print("Performing POST request...")
post_data = "327pwedfhua8anow38qr9yp21rwq"
headers = {"Content-Type": "text/plain"}
post_response = requests.post(url, data=post_data, headers=headers)
print("Response:", post_response.text)

# Final GET request to see the response again
print("Performing final GET request...")
final_get_response = requests.get(url)
print("Response:", final_get_response.text)
import requests
#post
files = [('files', ('README', open('./README.md', 'rb')))]
# header = {'Content-Type': 'multipart/form-data'}
response = requests.post('http://127.0.0.1:8000/pdicom/123', files=files)
# response = requests.post('http://127.0.0.1:8000/files', files={'fir': open('./README.md', 'rb')})

print(response.headers)
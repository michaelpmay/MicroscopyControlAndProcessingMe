import requests

url='http://localhost:8000/process'
name='null'
image=[[0,0,0],[0,0,0],[0,0,0]]
request={'name':name,'image':image}
response=requests.post(url,json=request)
print(response.content)
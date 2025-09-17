import hashlib 
import json
import time
import random
import requests
import datetime
from flask import Flask, request, jsonify

#### 01. 노드 블록 정보 확인
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/chain", headers=headers)
print(json.loads(res.content))
'''

#### 02. 트랜잭션 입력-1 
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
        "sender": "test_from",
        "recipient": "test_to",
    "amount": 3,
}
requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data)).content
print(data)
'''

#### 02. 트랜잭션 입력-2
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
        "sender": "test_from",
        "recipient": "test_to",
    "amount": 30,
}
requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data)).content
print(data)
'''


#### 02. 트랜잭션 입력-3
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
        "sender": "test_from",
        "recipient": "test_to",
    "amount": 300,
}
requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data)).content
print(data)
'''

#### 03. 채굴
##nonce 가 master인 점 확인. 

headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/mine")
#print(res)
#print(res.json())
print(res.text)



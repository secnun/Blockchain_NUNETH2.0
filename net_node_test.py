import requests
import json
import pandas as pd
import hashlib
import random

#### 01. 노드 블록 정보 확인
## 5000, 5001, 5002 각각 확인 -> 총 3대의 노드 활성화 확인
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/chain", headers=headers)
print(json.loads(res.content))
'''


#### 02. 노드 등록
### 5001(노드 2번), 5002(노드 3번)를 5000(노드 1번)에 등록(연결)
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
    "nodes": 'http://localhost:5001'
}
requests.post("http://localhost:5000/nodes/register", headers=headers, data=json.dumps(data)).content
'''
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
    "nodes": 'http://localhost:5002'
}
requests.post("http://localhost:5000/nodes/register", headers=headers, data=json.dumps(data)).content
'''



#### 03. 트랜잭션 입력
### 트랜잭션 입력 후 01번 과정으로 확인 실시
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
        "sender": "test_from",
        "recipient": "test_to",
    "amount": 3,
}
requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data)).content
'''
#03번 수행결과 아래와 같이 결과 찍힘
'''1번 노드
transactions_new!!! :  {'sender': 'test_from', 'recipient': 'test_to', 'amount': 3}
share transaction to >>    http://localhost:5001
share transaction to >>    http://localhost:5002

2번 노드 : transactions_new!!! :  {'sender': 'test_from', 'recipient': 'test_to', 'amount': 3, 'type': 'sharing'}

3번 노드 : transactions_new!!! :  {'sender': 'test_from', 'recipient': 'test_to', 'amount': 3, 'type': 'sharing'}
'''


#### 04. 채굴
## 5000번 포트(노드 1번)대상으로 마이닝 실시
## 1번 노드만 요청 받았으므로, 2,3번 노드는 1번 노드의 결과 똑같이 블록이 생성됨.
# 최종 /chain으로 확인
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/mine")
print(res)






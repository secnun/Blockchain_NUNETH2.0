import hashlib 
import json
import time
import random
import requests
import datetime
from flask import Flask, request, jsonify

class Blockchain(object):
    
    def __init__(self, account_name, account_weight):
        self.chain = []                                 
        self.current_transaction = []                   
        self.nodes = set()                              
        self.miner_wallet = {'account_name': account_name, 'weight': account_weight}  # 지갑정보 생성
        self.new_block(previous_hash='genesis_block', address = account_name) # genesis block 생성
        self.account_name = account_name
        self.account_weight = account_weight

        
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode() 
        return hashlib.sha256(block_string).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]                 


    def pos(self): #pick_winner를 포함한 PoS 핵심 합의.
        winner_list = [] # 각 노드에서 pick_winner 결과 뽑힌 winner 리스트
        time.sleep(1)
        my_winner = self.pick_winner(account_name = self.account_name, account_weight = self.account_weight)   
        winner_list.append(my_winner) # winner 리스트에 내노드 결과 넣기
        time.sleep(1)
        
        for target_node in blockchain.nodes:            # 다른 노드들도 pick_winner 진행 
            print(target_node)
            headers = {'Content-Type' : 'application/json; charset=utf-8'}
            res = requests.get('http://' + target_node   + "/nodes/pick_winner", headers=headers)
            winner_info = json.loads(res.content)  # 근처 노드들 선정결과 받아와서
            print(winner_info)
            winner_list.append(winner_info['winner']) 

        final_winner = max(winner_list,key = winner_list.count)  # 각 노드들의 pos 결과로 가장 많이 선정된 winner를 최종 winner 로 선정
        print("final_winner selected : ", final_winner)
        
        return final_winner
            
    
    #### PoS의 핵심. 채굴 담당자 선정 과정.
    ### 예치(staking)된 토큰의 비중을 기반으로 한 확률로 검증자를 선정
    def pick_winner(self,account_name, account_weight):  ### 누가 블록 만들지
        candidate_list = []  # POS 대상자를 뽑을 전체 풀, 소유 토큰 비중만큼 list에 노드 추가 후 랜덤 1개 검증자 선정 과정 거치게 됨.
             
        for w in range(account_weight):  # 나의 노드들의 weight 수만큼 추가(소유 토큰 수라고 생각)
            candidate_list.append(account_name)
       
        random.shuffle(candidate_list)       #  랜덤으로 섞고!
        for x in  candidate_list:           #  첫번째 node를 winner로 선정, 랜덤 pick
            winner  = x
            print("WINNER SELECTED : ", winner)
            break
        
        return winner                       # winner 공개
    # 현재 Pick 메커니즘은 여러 노드 연결시 더 복잡하나, 일단 단순하게 구현한 함수라고 생각하면 됨.


    def new_transaction(self, sender, recipient, amount, smart_contract):
        self.current_transaction.append(
            {
                'sender' : sender, # 송신자
                'recipient' : recipient, # 수신자
                'amount' : amount, # 금액
                'timestamp':time.time(),
                'smart_contract' : smart_contract
            }
        )
        return self.last_block['index'] + 1   


    def new_block(self, previous_hash=None, address = ''):
        block = {
            'index' : len(self.chain)+1,
            'timestamp' : time.time(),
            'transactions' : self.current_transaction,
            'previous_hash' : previous_hash ,
            'validator' : address #PoS 방식의 핵심
            #모든 노드가 믿을 수 있는 검증자(validator)를 선정, 그 검증자가 블록을 완성시켜 채굴 보상 획득
            #nonce 대신 validator 값이 들어감.
        }
        block["hash"] = self.hash(block)
        self.current_transaction = []
        self.chain.append(block)     
        return block

    #### 설명을 위해 추가
    ### PoS는 nonce 값이 사라짐에 따라, 해당 기능 역시 사라진다. 
    #@staticmethod
    #def valid_proof(last_proof, proof):
    #    guess = str(last_proof + proof).encode()          # 전 proof와 구할 proof 문자열 연결
    #    guess_hash = hashlib.sha256(guess).hexdigest()    # 이 hash 값 저장
    #    return guess_hash[:4] == "0000" 

my_ip = '0.0.0.0'
my_port = '5000'
node_identifier = 'node_'+my_port
mine_owner = 'master'
mine_profit = 0.1

blockchain = Blockchain(account_name=mine_owner, account_weight= 100)

app = Flask(__name__)

@app.route('/chain', methods=['GET'])
def full_chain():
    print("chain info requested!!")
    response = {
        'chain' : blockchain.chain, 
        'length' : len(blockchain.chain), 
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json() 
    print("transactions_new!!! : ", values)
    required = ['sender', 'recipient', 'amount'] 

    if not all(k in values for k in required):
        return 'missing values', 400
    
    if 'smart_contract' not in values:
        values['smart_contract'] = 'empty'

    index = blockchain.new_transaction(values['sender'],values['recipient'],
values['amount'], values['smart_contract'])
        
    response = {'message' : 'Transaction will be added to Block {%s}' % index}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    print("MINING STARTED")    
    final_winner = blockchain.pos()  
    
    if final_winner == blockchain.account_name:  # 만약 본 노드가 winner로 선정되었으면 아래와 같이

        blockchain.new_transaction(            #  나에게 보상을 주고
            sender=mine_owner, 
            recipient=node_identifier, 
            amount=mine_profit, # coinbase transaction 
            smart_contract={"contract_address":"mining_profit"}, 
        )

        previous_hash = blockchain.hash(blockchain.chain[-1])
        block = blockchain.new_block(previous_hash = previous_hash, address = mine_owner)  #  신규 블록 생성
        print("MY NODE IS SELECTED AS MINER NODE")

        response = {
            'message' : 'new block found',
            'index' : block['index'],
            'transactions' : block['transactions'],
            'nonce' : block['validator'], #nonce가 validator.
            'previous_hash' : block['previous_hash'],
            'hash' : block['hash']
        }

        return jsonify(response), 200
    
    else : # isWinner = False : 본 노드가 winner가 아님
        print("MY NODE IS NOT SELECTED AS MINER NODE")

        response = {
            'message' : 'NOT SELECTED'
        }

        return jsonify(response), 200
    
if __name__ == '__main__':
    app.run(host=my_ip, port=my_port)


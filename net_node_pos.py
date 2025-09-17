import hashlib
import json
import time
import random
import requests
from flask import Flask, request, jsonify
from urllib.parse import urlparse

class Blockchain(object):
    
    def __init__(self, account_name, account_weight):
        self.chain = []  # chain에 여러 block들 들어옴
        self.current_transaction = []  # 임시 transaction 넣어줌
        self.nodes = set()  # Node 목록을 보관
        self.miner_wallet = {'account_name': account_name, 'weight': account_weight}  # 지갑정보 생성
        self.new_block(previous_hash='genesis_block', address = account_name)        # genesis block 생성
        self.account_name = account_name
        self.account_weight = account_weight

        
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode() 
        return hashlib.sha256(block_string).hexdigest()
    
    @property
    def last_block(self):
        return self.chain[-1]


    def pos(self):
        winner_list = []   # 각 노드에서 pick_winner 결과 뽑힌 winner 리스트
        
        ## POS 가 시작되면 나뿐만 아니라 주변 모든 노드가 함께 Proof OF Staking을 진행
        self.resolve_conflict() #  PoS 시작 전 노드의 정상여부 선 검증 
        time.sleep(1)
        
        my_winner = self.pick_winner(account_name = self.account_name, account_weight = self.account_weight) # 본 노드에서 pick_winner 진행  : 확률로 승자 뽑기
        winner_list.append(my_winner)   # winner 리스트에 내노드 결과 넣기
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
#         if final_winner == self.account_name: # 본 노드가 final_winner             
#             return True
#         else:            # 본 노드가 final_winner가 아닐경우  
#                     
                
                
#             return False#  ### FALSE 값을 리턴!!!!
    
            
        
    def pick_winner(self,account_name, account_weight):
        candidate_list = []
             
        for w in range(account_weight):  # 나의 노드들의 weight 수만큼 추가
            candidate_list.append(account_name)
                
        for target_node in blockchain.nodes: # 근처 노드들의 weight 수만큼 추가
            print(target_node)

            headers = {'Content-Type' : 'application/json; charset=utf-8'}

            res = requests.get('http://' + target_node   + "/nodes/node_weight", headers=headers)
            target_node_info = json.loads(res.content)  # 근처 노드들의 weight 정보 받아와서

            for repeated in range(target_node_info['account_weight']):
                candidate_list.append(target_node_info['account_name'])  # weight값 만큼  candidate_list에 추가

        random.shuffle(candidate_list)       #  랜덤으로 섞고
        for x in  candidate_list:           #  첫번째 node를 winner 선정
            winner  = x
            print("WINNER SELECTED : ", winner)
            break

        return winner   # winner 공개
    
    
        
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
            'timestamp' : time.time(), # timestamp from 1970
            'transactions' : self.current_transaction,
            'previous_hash' : previous_hash ,
            'validator' : address #PoS 방식이라 nonce 제거
        }
        block["hash"] = self.hash(block)
        self.current_transaction = []
        self.chain.append(block) 
        
        return block

    def is_chain_valid(self, chain):           
        last_block = chain['chain'][-1]
        current_index = 1

        while current_index < len(chain): 
            block = chain[current_index]
            print('%s' % last_block)
            print('%s' % block)
            print("\n--------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False
            last_block = block
            current_index += 1
            
        return True
        
## 네트워크로 추가된부분 
    def register_node(self, address): # url 주소를 넣게 됨
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) # set 자료형태 안에 목록을 저장
        
        
    def resolve_conflict(self): # 다른노드들이랑 비교하며 지금의 내 노드 상태가 정상인지 검증
        
        for registering_node in blockchain.nodes:  # 근처 노드들의 weight 수만큼 추가
            headers = {'Content-Type' : 'application/json; charset=utf-8'}
            print(registering_node,  '    /http://' + registering_node   + "/chain")
            res = requests.get('http://' + registering_node   + "/chain", headers=headers)
            target_node_info = json.loads(res.content)
            
            
            if target_node_info['length'] > len(self.chain):  # 다른노드의 블록이 내 노드의 블록보다 길경우
                if self.is_chain_valid(target_node_info):     # 그리고 그 노드가 valid 할 경우 
                    self.blockchain = target_node_info        # 내 노드를 그 노드로 덮어씌우기
                    return
        return     

my_ip = 'localhost'
my_port = '5000'
node_identifier = 'node_'+my_port
mine_owner = 'validator_1'
mine_profit = 0.1

blockchain = Blockchain(account_name=mine_owner, account_weight= 100) #100개 토큰을 예치한것으로 시작 전제.

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
    
    if "type" not in values:  ## 신규로 추가된 경우 type 이라는 정보가 포함되어 없다. 해당 내용은 전파 필요
        for node in blockchain.nodes:  # nodes에 저장된 모든 노드에 정보를 전달한다.
            headers = {'Content-Type' : 'application/json; charset=utf-8'}
            data = {
                "sender": values['sender'],
                "recipient": values['recipient'],
                "amount": values['amount'],
                "type" : "sharing"   # 전파이기에 sharing이라는 type 이 꼭 필요하다.
            }
            requests.post("http://" + node  + "/transactions/new", headers=headers, data=json.dumps(data))
            print("share transaction to >>   ","http://" + node )
            
    return jsonify(response), 201


@app.route('/block/new', methods=['POST'])
def new_block():
    block = request.get_json() 
    print("NEW BLOCK  ADDED!!! : ", block)
    
    blockchain.current_transaction = []
    blockchain.chain.append(block) 
    response = {'message' : 'Transaction will be added to Block {%s}' % block['index']}
    return jsonify(response), 201



@app.route('/mine', methods=['GET'])
def mine():
    print("MINING STARTED")    
    final_winner = blockchain.pos()  
    
    if final_winner == blockchain.account_name:  # 만약 본 노드가 winner로 선정되었으면 아래와 같이
        print("MY NODE IS SELECTED AS MINER NODE")

    
    else : # isWinner = False : 본 노드가 winner가 아님
        print("MY NODE IS NOT SELECTED AS MINER NODE")

    blockchain.new_transaction(           #  선정된 노드에게 보상을 주고
        sender="mining_profit", 
        recipient=final_winner, 
        amount=mine_profit, # coinbase transaction 
        smart_contract={"contract_address":"mining_profit"}, 
    )

    previous_hash = blockchain.hash(blockchain.chain[-1])
    block = blockchain.new_block(previous_hash = previous_hash, address = final_winner)  #  신규 블록 생성
    print(final_winner," IS SELECTED AS MINER NODE")
    #####
    #다른노드들에 전파해야해!!!
    #####
    ################### 노드 연결을 위해 추가되는 부분
    for node in blockchain.nodes: # nodes에 연결된 모든 노드에 작업증명(PoW)가 완료되었음을 전파한다.
        headers = {'Content-Type' : 'application/json; charset=utf-8'}

        alarm_newBlock = requests.post("http://" + node  + "/block/new", headers=headers, data = json.dumps(blockchain.chain[-1] ) ) 
        print(alarm_newBlock.content)

    response = {
        'message' : 'new block found',
        'index' : block['index'],
        'transactions' : block['transactions'],
        'validator' : block['validator'],
        'previous_hash' : block['previous_hash'],
        'hash' : block['hash']
    }


    response = {'message' : 'Mining Complete'}
    return jsonify(response), 200



################### 노드 연결을 위해 추가되는 함수 : 다른 Node 등록!
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json() # json 형태로 보내면 노드가 저장이 됨
    print("register nodes !!! : ", values)
    registering_node =  values.get('nodes')
    if registering_node == None: # 요청된 node 값이 없다면! 
        return "Error: Please supply a valid list of nodes", 400
     
    ## 요청받은 노드드이 이미 등록된 노드와 중복인지 검사
    ## 중복인인 경우
    if registering_node.split("//")[1] in blockchain.nodes:
        print("Node already registered")  # 이미 등록된 노드입니다.
        response = {
            'message' : 'Already Registered Node',
            'total_nodes' : list(blockchain.nodes),
        }

    ## 중복  안되었다면
    else:  
        # 내 노드리스트에 추가
        blockchain.register_node(registering_node) 
        
        ## 이 후 해당 노드에 내정보를  등록하기
        headers = {'Content-Type' : 'application/json; charset=utf-8'}
        data = {
            "nodes": 'http://' + my_ip + ":" + my_port
        }
        print("MY NODE INFO " , 'http://' + my_ip + ":" + my_port)
        requests.post( registering_node + "/nodes/register", headers=headers, data=json.dumps(data))
        
        # 이후 주변 노드들에도 새로운 노드가 등장함을 전파
        for add_node in blockchain.nodes:
            if add_node != registering_node.split("//")[1]:
                print('add_node : ', add_node)
                ## 노드 등록하기
                headers = {'Content-Type' : 'application/json; charset=utf-8'}
                data = {
                    "nodes": registering_node
                }
                requests.post('http://' + add_node   + "/nodes/register", headers=headers, data=json.dumps(data))

        response = {
            'message' : 'New nodes have been added',
            'total_nodes' : list(blockchain.nodes),
        }
    return jsonify(response), 201


@app.route('/nodes/node_weight', methods=['GET'])
def node_weight():
    print("node_weight requested!!")

    response = {
        'account_name' : blockchain.account_name,
        'account_weight' : blockchain.account_weight
    }
    return jsonify(response), 200    

    
@app.route('/nodes/pick_winner', methods=['GET'])
def pick_winner():
    print("pick_winner requested!!")
    
    candidate_list = []  # POS 대상자를 뽑을 전체 풀!!
    for w in range(blockchain.account_weight):  # 나의 노드들의 weight 수만큼 추가
        candidate_list.append(blockchain.account_name)

    for target_node in blockchain.nodes:            # 근처 노드들의 weight 수만큼 추가
        print(target_node)
        
        headers = {'Content-Type' : 'application/json; charset=utf-8'}
        res = requests.get('http://' + target_node   + "/nodes/node_weight", headers=headers)
        target_node_info = json.loads(res.content)
                
        for repeated in range(target_node_info['account_weight']):
            candidate_list.append(target_node_info['account_name'])

    random.shuffle(candidate_list)       #  랜덤으로 섞고
    for x in  candidate_list:           #  첫번째 node를 winner로 선정
        winner  = x
        print("WINNER SELECTED : ", winner)
        break

    response = {
        'winner' : winner, 
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host=my_ip, port=my_port)
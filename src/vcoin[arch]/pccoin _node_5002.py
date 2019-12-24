#!/usr/bin/env python
""" Implementing a Cryptocurrency (Virtual coin [gccoin] code base) """

import datetime
import hashlib
import json
import requests
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse


__author__ = "SentinelWarren"
__credits__ = ""

__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "SentinelWarren"
__email__ = "warrenkalolo@gmail.com"
__status__ = "Prototype"

# Building a Blockchain
class Blockchain:
    """ Defining a blockchain class (it could be anything, Blockchain, Energychain, Wifichain, Shulechain whatever suitable ) """

    def __init__(self):
        # The chain pocket, Array is just fine since we don't wanna reverse anything.
        self.chain = []
        self.transactions = []

        # Genesis block
        self.create_block(proof = 1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        """new block creation function, Note, its {Immutable}"""
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}

        # Adding transaction to block | Appending chain to the pocket :)
        self.transactions = []
        self.chain.append(block)
        return block

    """ function to get a pervious_block in the blockchain """
    def get_prev_block(self): return self.chain[-1]

    def proof_of_work(self, previous_proof):
        """ function to calculate proof of work[solution] from the defined problem """

        # needed for attempts of finding a solution by incrementation till solved
        new_proof = 1

        # Once we find the solution it will be == True
        check_proof = False

        # While loop till check_proof == True
        while check_proof is False:
            # Hash operations to solve the problem using hashlib module when the miner mines.
            # Note, the problem used here is pretty basic, however it can be tweaked to any hardest problem preferable i.e. Energy consumption, verifying CO2 emition through the smartmeters and GU operations etc etc.
            hash_ops = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_ops[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        """ hash function that takes a block and return the sha256 cryptographic hash[The most secure one currently]. """

        encoded_block = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        """ A function to check if everything is right and valid in the blockchain """

        # First block of the chain
        previous_block = chain[0]
        # Looping variable
        block_index = 1

        # A while loop to check if the looping variable is less than the length of the chain iterate on all the chains
        while block_index < len(chain):
            # First block
            block = chain[block_index]

            # If the previous_hash of current block is different than the previous block return False since its invalid
            if block["previous_hash"] != self.hash(previous_block): return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            # hash operations
            hash_ops = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()

            # If the hash operations first 4/four char aren't matching
            if hash_ops[:4] != "0000": return False
            previous_block = block
            block_index += 1

        # If everything is gucci return True
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount})
        previous_block = self.get_prev_block()
        return previous_block["index"] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_len = len(self.chain)

        for node in network:
            response = requests.get(f'http://{node}/get_chain')

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > max_len and self.is_chain_valid(chain):
                    max_len = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Web part using Flask so that we can test our blockchain graphically in i.e postman
app = Flask(__name__)

# Creating an address for the node on Port 5002
node_address = str(uuid4()).replace("-", "")

# Creating a Blockchain
blockchain = Blockchain()

# Mining the new_block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    """ A mining function, pretty explanatory. """

    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block["proof"]
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = "Second_miner", amount = 1)

    block = blockchain.create_block(proof, previous_hash)
    response = {"message": "Congrats, you just mined the block!",
                "index": block['index'],
                "timestamp": block["proof"],
                "previous_hash": block["previous_hash"],
                "transactions": block["transactions"]}
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    """ A function for getting the chain value """

    response = {"chain": blockchain.chain,
                "length": len(blockchain.chain)}
    return jsonify(response), 200


# Checking if the blockchain is valid
@app.route('/is_chain_valid', methods=['GET'])
def is_chain_valid():
    """ A blockchain verification function, can be seen in action in postman """

    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid:
        response = {"message": "The Blockchain is valid!"}
    else:
        response = {"message": "Unfortunately the Blockchain is not valid!"}

    return jsonify(response), 200

#Adding new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    jsn = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]

    if not all (key in jsn for key in transaction_keys):
        return "Some elements on the transaction are missing", 400

    index = blockchain.add_transaction(jsn["sender"], jsn["receiver"], jsn["amount"])
    response = {"message": f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

#Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    jsn = request.get_json()
    nodes = jsn.get("nodes")

    if nodes is None:
        return "No node", 400

    for node in nodes:
        blockchain.add_node(node)

    response = {"message": "All the nodes are now connected. The pccoin blockchain now contains the following nodes:",
    "total_nodes": list(blockchain.nodes)}

    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    """ A blockchain verification function, can be seen in action in postman """

    is_chain_replaced = blockchain.replace_chain()

    if is_chain_replaced:
        response = {"message": "The Nodes had diff chains so the chain was replaced by the longest one!",
        "new_chain": blockchain.chain}
    else:
        response = {"message": "All good. The chain is the largest one!",
        "actual_chain": blockchain.chain}

    return jsonify(response), 200

# Serving our simple blockchain prototype
app.run(host='0.0.0.0', port=5002)


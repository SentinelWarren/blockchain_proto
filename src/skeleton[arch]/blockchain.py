#!/usr/bin/env python
"""Experimenting around blockchain implementation [code base]"""

import datetime
import hashlib
import json
from flask import Flask, jsonify


__author__ = "SentinelWarren"
__credits__= ""

__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "SentinelWarren"
__email__ = "warrenkalolo@gmail.com"
__status__ = "Prototype"


## Defining a blockchain class (it could be anything, Blockchain, Energychain, Wifichain, Shulechain whatever suitable )
class Bchain:
    def __init__(self):
        ## The chain pocket, Array is just fine since we don't wanna reverse anything.
        self.chain = []
        ## genesis block
        self.create_block(proof=1, previous_hash="0")

    ## new block creation function, Note, its {Immutable}
    def create_block(self, proof, previous_hash):
        block = {"index": len(self.chain) + 1,
                 "timestamp": str(datetime.datetime.now()),
                 "proof": proof,
                 "previous_hash": previous_hash}

        ## Appending to the pocket :)
        self.chain.append(block)
        return block

     ## function to get a pervious_block in the blockchain
    def get_prev_block(self):
        return self.chain[-1]

    ## function to calculate proof of work[solution] from the defined problem
    def proof_of_work(self, previous_proof):
        ## needed for attempts of finding a solution by incrementation till solved
        new_proof = 1

        ## Once we find the solution it will be == True
        check_proof = False

        ## While loop till check_proof == True
        while check_proof is False:
            ## Hash operations to solve the problem using hashlib module when the miner mines.
            ## Note, the problem used here is pretty basic, however it can be tweaked to any hardest problem preferable i.e. Energy consumption, verifying CO2 emition through the smartmeters and GU operations etc etc.
            hash_ops = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_ops[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    ## hash function that takes a block and return the sha256 cryptographic hash[The most secure one currently].
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(encoded_block).hexdigest()

    ## A function to check if everything is right and valid in the blockchain
    def is_chain_valid(self, chain):
        ## First block of the chain
        previous_block = chain[0]
        ## Looping variable
        block_index = 1

        ## A while loop to check if the looping variable is less than the length of the chain iterate on all the chains
        while block_index < len(chain):
            ## First block
            block = chain[block_index]

            ## If the previous_hash of current block is different than the previous block return False since its invalid
            if block["previous_hash"] != self.hash(previous_block): return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            ## hash operations
            hash_ops = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()

            ## If the hash operations first 4/four char aren't matching
            if hash_ops[:4] != "0000":
                return False
            previous_block = block
            block_index += 1

        ## If everything is gucci return True
        return True


# Web part using Flask so that we can test our blockchain graphically in i.e postman
app = Flask(__name__)

# Creating a Blockchain
blockchain = Bchain()

# Mining the new_block
@app.route('/mine_block', methods = ['GET'])

## A mining function, pretty explanatory.
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block["proof"]
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)
    response = {"message": "Congrats, you just mined the block!",
                "index": block['index'],
                "timestamp": block["proof"],
                "previous_hash": block["previous_hash"]}
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])

## A function for getting the chain value,
def get_chain():
    response = {"chain": blockchain.chain,
                "length": len(blockchain.chain)}
    return jsonify(response), 200


## Checking if the blockchain is valid
@app.route('/is_chain_valid', methods = ['GET'])

## A blockchain verification function, can be seen in action in postman
def is_bchain_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)

    if is_valid:
        response = {"message": "The Blockchain is valid!"}
    else:
        response = {"message": "Unfortunately the Blockchain is not valid!"}

    return jsonify(response), 200



## Serving our simple blockchain prototype
app.run(host = '0.0.0.0', port=5000)
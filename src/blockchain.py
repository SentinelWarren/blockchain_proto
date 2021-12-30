"""Blockchain module"""

import json
from hashlib import sha256
from datetime import datetime

from uuid import uuid4
from urllib.parse import urlparse

from typing import Any, List, Set, Dict, TypedDict
import requests


class Block(TypedDict):
    """Block class"""
    index: int
    timestamp: str
    transactions: List[Dict[str, Any]]
    proof: int
    previous_hash: str


class Blockchain:
    """The main blockchain class."""

    def __init__(self) -> None:
        self.transactions: List[Dict[str, Any]] = []
        self.chain: List[Block] = []    # The chain container

        self.nodes: Set[str] = set()
        self.node_id: str = str(uuid4()).replace('-', '')

        # Create the genesis block
        print("Creating genesis block")
        self.create_block(proof=1, prev_hash="genesis")

    def create_block(self, proof: int=None, prev_hash: str=None) -> Block:
        """Create a new Block in the Blockchain
        the Block should be immutable.

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: <str> Hash of the previous Block
        :return: <Block> A new Block
        """
        block = Block(
                    index = len(self.chain),
                    timestamp = str(datetime.now()),
                    transactions = self.transactions,
                    proof = proof or self.proof_of_work(self.last_block),
                    previous_hash = prev_hash or self.hash(self.last_block)
                )

        # Reset the current transactions list
        self.transactions = []

        # Append block to the chain
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """Creates a new transaction to go into the next mined Block

        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <float> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self) -> Block:
        """Get the last block in the chain.

        :return: <Block> The last Block in the chain.
        """
        return self.chain[-1]

    @staticmethod
    def hash(block: Block) -> str:
        """Creates a SHA-256 hash of a Block.

        :param block: <Block>
        :return: <str> Hash
        """
        # The dictionary has to be Ordered, or we'll have inconsistent hashes.
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return sha256(encoded_block).hexdigest()

    def proof_of_work(self, last_block: Block) -> int:
        """Proof of Work Algorithm:

        - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof

        :param last_block: <Block> The last Block
        :return: <int> Proof
        """
        last_proof = last_block["proof"]
        last_hash = self.hash(last_block)

        proof = 0
        while self.validate_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def validate_proof(last_proof: int, proof: int, last_hash: str) -> bool:
        """Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """
        guess: bytes = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def validate_chain(self, chain: List[Block]) -> bool:
        """Determine if a given blockchain is valid.

        :param chain: <List[Block]> A blockchain
        :return: <bool> True if valid, False if not
        """
        prev_block: Block = chain[0]
        current_index: int = 1

        while current_index < len(chain):
            block = chain[current_index]

            # return False If the previous_hash of current block
            # is different from the previous block,
            print(f'{prev_block}')
            print(f'{block}')
            print("\n-----------\n")
            prev_block_hash = self.hash(prev_block)
            if block["previous_hash"] != prev_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.validate_proof(prev_block["proof"], block["proof"], prev_block_hash):
                return False

            prev_block = block
            current_index += 1

        # If everything is valid & gucci return True
        return True

    def register_node(self, address: str) -> None:
        """Add a new node to the list of nodes.

        :param address: Address of node. Eg. 'http://127.0.0.1:5000'
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like 'http://127.0.0.1:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def resolve_conflicts(self) -> bool:
        """The consensus algorithm, it resolves conflicts by
        replacing the chain with the longest one in the network.

        :return: <bool> True if the chain was replaced, False if not
        """
        neighbors = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

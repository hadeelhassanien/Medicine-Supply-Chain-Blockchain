from hashlib import sha256
import json
import time
import os

CHAIN_FILE = "chain_data.json"


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        # self.hash is set externally after proof_of_work.
        # It is deliberately excluded from compute_hash() so that
        # freshly mined blocks and blocks loaded from disk hash identically.

    def compute_hash(self):
        """
        Return the SHA-256 hash of the block's contents.
        sort_keys=True guarantees the same dict always produces the same string.
        self.hash is excluded so the computation stays consistent across
        mine-time and load-from-disk.
        """
        block_dict = {
            "index":         self.index,
            "transactions":  self.transactions,
            "timestamp":     self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
        }
        block_string = json.dumps(block_dict, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # Number of leading zeros required — raise this to make mining slower
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.load()
        if not self.chain:
            self.create_genesis_block()

    # ── Genesis ────────────────────────────────────────────────────
    def create_genesis_block(self):
        """
        Block 0: empty transactions, previous_hash='0'.
        Also runs proof_of_work so the genesis hash satisfies difficulty
        and is_chain_valid() can check it uniformly with all other blocks.
        """
        genesis = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0",
        )
        # Run PoW on genesis so its hash satisfies difficulty like every
        # other block — this lets is_chain_valid() check all blocks uniformly.
        genesis.hash = self.proof_of_work(genesis)
        self.chain.append(genesis)
        self.save()

    @property
    def last_block(self):
        return self.chain[-1]

    # ── Proof of Work ──────────────────────────────────────────────
    def proof_of_work(self, block):
        """
        Increment nonce until the block's hash starts with `difficulty` zeros.
        Returns the valid hash string (the proof).
        """
        block.nonce = 0
        block_hash = block.compute_hash()
        while not block_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            block_hash = block.compute_hash()
        return block_hash

    def is_valid_proof(self, block, block_hash):
        """
        Confirm that block_hash satisfies difficulty AND correctly
        reflects the block's current contents.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    # ── Adding blocks ──────────────────────────────────────────────
    def add_block(self, block, proof):
        """
        Validate then commit a block to the chain.
          a) proof must satisfy difficulty and match block contents
          b) block.previous_hash must match the last block's hash
        """
        if not self.is_valid_proof(block, proof):
            print("Error: proof of work is invalid")
            return False
        if self.last_block.hash != block.previous_hash:
            print("Error: previous_hash does not match the last block's hash")
            return False
        block.hash = proof
        self.chain.append(block)
        self.save()
        return True

    def add_new_transaction(self, transaction: dict):
        """
        Queue one supply chain event as an unconfirmed transaction.
        Required keys: product, action, account, note, timestamp
        """
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        """
        Bundle all pending transactions into a new block,
        run proof of work, and commit it.
        Returns the new block's index, or False if nothing to mine.
        """
        if not self.unconfirmed_transactions:
            return False

        new_block = Block(
            index=self.last_block.index + 1,
            transactions=self.unconfirmed_transactions,
            timestamp=time.time(),
            previous_hash=self.last_block.hash,
        )

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index

    # ── Chain validation ───────────────────────────────────────────
    def is_chain_valid(self):
        """
        Walk every block (including genesis) and verify three things:
          1. Stored hash matches recomputed hash  → detects data tampering
          2. previous_hash matches prior block's hash → detects chain relinking
          3. Hash satisfies proof-of-work difficulty → detects hash substitution
        Returns (True, 'Chain is valid') or (False, '<reason for failure>').
        """
        for i in range(len(self.chain)):
            current = self.chain[i]

            # Check 1: data integrity
            if current.hash != current.compute_hash():
                return False, f"Block {i} hash is invalid — data was altered"

            # Check 2: chain linkage (skip genesis which has no predecessor)
            if i > 0:
                previous = self.chain[i - 1]
                if current.previous_hash != previous.hash:
                    return False, f"Block {i} previous_hash does not match block {i-1} hash"

            # Check 3: proof of work
            if not current.hash.startswith('0' * Blockchain.difficulty):
                return False, f"Block {i} does not satisfy proof of work"

        return True, "Chain is valid"

    # ── Query helpers ──────────────────────────────────────────────
    def get_product_history(self, product: str):
        """
        Return all transactions across all blocks that match the product name.
        Case-insensitive. Each entry includes block_index and block_hash.
        """
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("product", "").lower() == product.lower():
                    history.append({
                        **tx,
                        "block_index": block.index,
                        "block_hash":  block.hash,
                    })
        return history

    def get_all_products(self):
        """Return a sorted, deduplicated list of every product in the chain."""
        products = set()
        for block in self.chain:
            for tx in block.transactions:
                if "product" in tx:
                    products.add(tx["product"])
        return sorted(products)

    def get_chain_as_list(self):
        """Return the full chain as a JSON-serializable list of dicts."""
        return [
            {
                "index":         block.index,
                "transactions":  block.transactions,
                "timestamp":     block.timestamp,
                "previous_hash": block.previous_hash,
                "nonce":         block.nonce,
                "hash":          block.hash,
            }
            for block in self.chain
        ]

    # ── Persistence ────────────────────────────────────────────────
    def save(self):
        """Write the current chain to chain_data.json."""
        with open(CHAIN_FILE, "w") as f:
            json.dump(self.get_chain_as_list(), f, indent=2)

    def load(self):
        """Load the chain from chain_data.json if it exists."""
        if not os.path.exists(CHAIN_FILE):
            return
        with open(CHAIN_FILE, "r") as f:
            data = json.load(f)
        for d in data:
            block = Block(
                index=d["index"],
                transactions=d["transactions"],
                timestamp=d["timestamp"],
                previous_hash=d["previous_hash"],
            )
            block.nonce = d["nonce"]
            block.hash  = d["hash"]
            self.chain.append(block)


# ── Demo / manual test  (python blockchain.py) ─────────────────────
if __name__ == "__main__":
    if os.path.exists(CHAIN_FILE):
        os.remove(CHAIN_FILE)

    blockchain = Blockchain()

    # --- Genesis ---
    if len(blockchain.chain) == 1:
        print("Genesis block successfully created!")
    else:
        print("Genesis block was NOT created")
    print("Genesis block attributes:")
    print(blockchain.chain[0].__dict__)
    print()

    # --- Add transactions and mine ---
    blockchain.add_new_transaction({"product": "Aspirin Batch 001", "action": "manufactured",        "account": "PharmaCo",    "note": "Lot #A001 - 10,000 units", "timestamp": time.time()})
    blockchain.add_new_transaction({"product": "Aspirin Batch 001", "action": "qa_passed",           "account": "PharmaCo",    "note": "Potency 99.8%",            "timestamp": time.time()})
    blockchain.add_new_transaction({"product": "Aspirin Batch 001", "action": "received_at_warehouse","account": "ColdStorage", "note": "Temp: 4C on arrival",      "timestamp": time.time()})
    blockchain.add_new_transaction({"product": "Aspirin Batch 001", "action": "delivered_to_pharmacy","account": "MedDistribute","note": "Truck #MT-77",            "timestamp": time.time()})
    blockchain.add_new_transaction({"product": "Aspirin Batch 001", "action": "received_at_pharmacy", "account": "CVS",         "note": "All seals intact",         "timestamp": time.time()})
    print("5 transactions added\n")

    index = blockchain.mine()
    if len(blockchain.chain) == 2:
        print(f"Mining of a block was successful!")
    else:
        print("Mining was not successful")
    print(f"Index of mined block: {index}")
    print("Blockchain after mining:")
    for block in blockchain.chain:
        print(block.__dict__)
        print()

    # --- Validate ---
    valid, message = blockchain.is_chain_valid()
    print(f"Chain valid: {valid} | {message}\n")

    # --- Tamper demo ---
    print("--- Tampering with block 1 ---")
    blockchain.chain[1].transactions[0]["action"] = "TAMPERED"
    valid, message = blockchain.is_chain_valid()
    print(f"Chain valid after tamper: {valid} | {message}")
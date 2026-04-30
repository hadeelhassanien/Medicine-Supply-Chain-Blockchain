# app.py
# Flask REST API — ties blockchain.py and accounts.py together.

from flask import Flask, request, jsonify, send_from_directory
from blockchain import Blockchain
from accounts import is_valid_account, is_allowed_action, get_all_accounts, get_allowed_actions
import time
import os
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)
blockchain = Blockchain()


# ── Serve the dashboard ────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── Log a new supply chain event ───────────────────────────────────
@app.route("/log", methods=["POST"])
def log_transaction():
    """
    Expects JSON body:
    {
        "product":  "Aspirin Batch 001",
        "action":   "manufactured",
        "account":  "PharmaCo",
        "note":     "Lot #A001 - 10,000 units"
    }
    """
    data = request.get_json()

    # Validate required fields
    required = ["product", "action", "account"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    account = data["account"]
    action  = data["action"]

    # Validate account exists
    if not is_valid_account(account):
        return jsonify({"error": f"Unknown account: {account}"}), 403

    # Validate account is allowed to perform this action
    if not is_allowed_action(account, action):
        allowed = get_allowed_actions(account)
        return jsonify({
            "error":           f"{account} is not allowed to perform '{action}'",
            "allowed_actions": allowed
        }), 403

    # Build transaction and add to pending pool
    transaction = {
        "product":   data["product"],
        "action":    action,
        "account":   account,
        "note":      data.get("note", ""),
        "timestamp": time.time()
    }

    blockchain.add_new_transaction(transaction)

    # Mine immediately so each event is its own block
    index = blockchain.mine()

    return jsonify({
        "message":     "Transaction logged and mined successfully",
        "block_index": index
    }), 201


# ── Get full history for a product ─────────────────────────────────
@app.route("/history/<product_id>", methods=["GET"])
def get_history(product_id):
    """
    Returns all transactions for a given product across the entire chain.
    Example: GET /history/Aspirin Batch 001
    """
    history = blockchain.get_product_history(product_id)
    if not history:
        return jsonify({"error": f"No records found for product: {product_id}"}), 404
    return jsonify({"product": product_id, "history": history}), 200


# ── Verify chain integrity ─────────────────────────────────────────
@app.route("/verify", methods=["GET"])
def verify_chain():
    valid, message = blockchain.is_chain_valid()
    return jsonify({"valid": valid, "message": message}), 200


# ── View the entire blockchain ─────────────────────────────────────
@app.route("/chain", methods=["GET"])
def get_chain():
    chain = blockchain.get_chain_as_list()
    return jsonify({"length": len(chain), "chain": chain}), 200


# ── List all accounts ──────────────────────────────────────────────
@app.route("/accounts", methods=["GET"])
def accounts():
    return jsonify({"accounts": get_all_accounts()}), 200


# ── List all products in the chain ────────────────────────────────
@app.route("/products", methods=["GET"])
def products():
    return jsonify({"products": blockchain.get_all_products()}), 200


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
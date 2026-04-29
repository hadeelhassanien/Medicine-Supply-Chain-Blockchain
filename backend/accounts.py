# accounts.py
# Defines the four supply chain participants and their permissions.

ACCOUNTS = {
    "PharmaCo": {
        "role": "Manufacturer",
        "allowed_actions": ["manufactured", "qa_passed"]
    },
    "ColdStorage": {
        "role": "Warehouse",
        "allowed_actions": ["received_at_warehouse", "stored", "dispatched_from_warehouse"]
    },
    "MedDistribute": {
        "role": "Distributor",
        "allowed_actions": ["picked_up_from_warehouse", "in_transit", "delivered_to_pharmacy"]
    },
    "CVS": {
        "role": "Retail Pharmacy",
        "allowed_actions": ["received_at_pharmacy", "available_for_sale", "sold"]
    }
}


def is_valid_account(account: str) -> bool:
    """Check if the account name exists in the system."""
    return account in ACCOUNTS


def is_allowed_action(account: str, action: str) -> bool:
    """Check if the account is permitted to perform the given action."""
    if not is_valid_account(account):
        return False
    return action in ACCOUNTS[account]["allowed_actions"]


def get_role(account: str) -> str:
    """Return the role of a given account, or 'Unknown' if not found."""
    if not is_valid_account(account):
        return "Unknown"
    return ACCOUNTS[account]["role"]


def get_all_accounts() -> list:
    """Return a list of all account names."""
    return list(ACCOUNTS.keys())


def get_allowed_actions(account: str) -> list:
    """Return the list of allowed actions for an account."""
    if not is_valid_account(account):
        return []
    return ACCOUNTS[account]["allowed_actions"]


# ── Quick test (python accounts.py) ───────────────────────────────
if __name__ == "__main__":
    print("=== Accounts ===")
    for name, info in ACCOUNTS.items():
        print(f"{name} ({info['role']}) → {info['allowed_actions']}")

    print("\n=== Permission Checks ===")
    print(f"PharmaCo can 'manufactured':        {is_allowed_action('PharmaCo', 'manufactured')}")
    print(f"PharmaCo can 'received_at_pharmacy': {is_allowed_action('PharmaCo', 'received_at_pharmacy')}")
    print(f"CVS can 'sold':                      {is_allowed_action('CVS', 'sold')}")
    print(f"CVS can 'manufactured':              {is_allowed_action('CVS', 'manufactured')}")
    print(f"FakeOrg can do anything:             {is_allowed_action('FakeOrg', 'manufactured')}")
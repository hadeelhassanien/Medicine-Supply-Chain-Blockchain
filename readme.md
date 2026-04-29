# Pharma-Chain: Blockchain-Based Pharmaceutical Supply Chain Tracker

A blockchain simulation that tracks pharmaceutical products through a multi-organization supply chain, ensuring transparency, immutability, and tamper-evident record keeping.

## Group Members
- Hadeel Hassanien - hxh230009
- Alishba Jafri - arj220005
- Maryam Al-Naami - mxa220202
- Manaar Quadri - msq220001

## Project Overview

This project implements a blockchain-based supply chain tracking system for the pharmaceutical industry. Each stage of a product's journey from manufacturing to final retail delivery is recorded as an immutable block in the chain. No participant can alter or delete records logged by another participant, simulating how independent organizations share a ledger without relying on a central authority.

### Participants
| Account          | Role 
|------------------|------------------------
| PharmaCo         | Manufacturer — introduces products into the chain 
| ColdStorage Inc. | Warehouse — logs receipt and cold storage 
| MedDistribute    | Distributor — logs shipment events 
| CVS              | Retail Pharmacy — logs final delivery 

## Tech Stack
- **Python 3** — core blockchain logic
- **Flask** — REST API layer for participant interactions
- **SHA-256** — cryptographic hashing for tamper detection
- **JSON** — persistent chain storage
- **HTML/CSS/JS** — dashboard UI for querying product history

## Project Structure
pharma-chain/
├── blockchain.py        # Block and Blockchain classes
├── accounts.py          # Participant accounts and permissions
├── app.py               # Flask REST API
├── chain_data.json      # Persisted blockchain data
├── static/
│   └── index.html       # Dashboard UI
└── README.md

## How to Run

1. Clone the repository
```bash
git clone https://github.com/yourusername/pharma-chain.git
cd pharma-chain
```

2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

3. Install dependencies
```bash
pip install flask
```

4. Run the app
```bash
python app.py
```

5. Open your browser and go to `http://localhost:5000`

## API Endpoints
| Method | Endpoint                | Description 
|--------|-------------------------|-------------
| POST   | `/log`                  | Log a new supply chain event 
| GET    | `/history/<product_id>` | Get full chain history for a product 
| GET    | `/verify`               | Verify chain integrity |
| GET    | `/chain`                | View the entire blockchain |


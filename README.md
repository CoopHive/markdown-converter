# CoopHive Markdown Converter

## 📌 Overview

The **CoopHive Markdown Converter** is a sophisticated Python-based pipeline designed for processing, converting, chunking, embedding, querying, and rewarding activities around scientific documents. Primarily tailored for decentralized science (DeSci) applications, it integrates powerful tools such as ChromaDB, Neo4j graph databases, IPFS storage, and blockchain-based reward mechanisms.

---

## 🗂️ Project Directory Structure

```bash
coophive-markdown-converter/
├── README.md                          # Documentation overview
├── pyproject.toml                     # Python project metadata and dependencies
├── pytest.ini                         # Pytest configuration
├── .env.example                       # Template for environment variables
├── .flake8                            # Flake8 linting rules
├── config/                            # Runtime configuration files
│   ├── db_creator.yml                 # Config for database creation from Neo4j/IPFS
│   ├── evaluation.yml                 # Config for evaluating query results
│   ├── processor.yml                  # Config for document processing pipeline
│   └── token_test.yml                 # Config for blockchain-based token rewards
├── contracts/                         # Blockchain contract ABIs
│   ├── CoopHiveV1.json                # Current smart contract ABI
│   └── old.json                       # Older contract ABI
├── descidb/                           # Core application modules
│   ├── core/                          # Main document processing logic
│   │   ├── chunker.py                 # Text chunking logic
│   │   ├── converter.py               # PDF to markdown conversion
│   │   ├── embedder.py                # Text embedding generation
│   │   ├── processor.py               # Processing pipeline class
│   │   └── processor_main.py          # Entrypoint for running processing
│   ├── db/                            # Database management modules
│   │   ├── chroma_client.py           # ChromaDB client for embeddings
│   │   ├── db_creator.py              # Populate DBs from Neo4j/IPFS
│   │   ├── db_creator_main.py         # Entrypoint to run DB creation
│   │   ├── graph_db.py                # Neo4j Graph DB client
│   │   └── postgres_db.py             # PostgreSQL DB management
│   ├── query/                         # Querying and evaluation modules
│   │   ├── evaluation_agent.py        # Agent-based evaluation logic
│   │   ├── evaluation_main.py         # Entrypoint for evaluation tasks
│   │   └── query_db.py                # ChromaDB querying functionality
│   ├── rewards/                       # Reward mechanisms
│   │   ├── token_rewarder.py          # Blockchain token reward logic
│   │   └── token_reward_main.py       # Entrypoint to execute reward logic
│   └── utils/                         # Utility functions
│       ├── logging_utils.py           # Logging utilities
│       └── utils.py                   # File handling and IPFS helpers
├── docker/                            # Dockerfiles for containerization
├── erc20-token/                       # ERC20 blockchain token setup
├── papers/                            # Sample documents and metadata
├── scripts/                           # Shell scripts for easy task execution
├── tests/                             # Unit tests for modules
└── .github/workflows/                 # CI/CD workflows
```

---

## ⚙️ Components and What They Do

### 🔄 Processor (processor_main.py)

This is the main entrypoint to run a full pipeline:

1. Converts PDFs to markdown using Marker or OpenAI
2. Chunks the markdown
3. Embeds the chunks
4. Uploads to IPFS and stores metadata in ChromaDB, Neo4j, and Postgres

👉 Controlled by: `config/processor.yml`

**Customize:**

- `converter`: Use `marker` or `openai`, or define your own in `converter.py`
- `chunker`: Choose between `paragraph`, `sentence`, `fixed_length`, etc.
- `embedder`: Use `openai`, `nvidia`, or extend `embedder.py` with your own

### 🧠 Evaluation Agent (evaluation_main.py)

Evaluates multiple DBs for a user query, compares results using LLMs (e.g., via OpenRouter), and outputs ranking + reasoning.

👉 Controlled by: `config/evaluation.yml`

**Customize:**

- Modify the evaluation query and model in the config
- Add your own ranking logic inside `evaluation_agent.py`

### 🧱 DB Creator (db_creator_main.py)

Reconstructs databases using paths from Neo4j that lead from original PDFs to embeddings stored in IPFS.

👉 Controlled by: `config/db_creator.yml`

**Customize:**

- Adjust traversal depth and path in the config
- Extend `graph_db.py` to support new graph logic

### 🎖️ Token Rewarding (token_reward_main.py)

Reads user job stats (based on Neo4j-authored edges or DB logs), calculates reward scores, and distributes ERC20 tokens using a custom smart contract.

👉 Controlled by: `config/token_test.yml`

**Customize:**

- Choose from strategies: `milestone`, `bonus`, `decay`, or create your own in `token_rewarder.py`
- Replace the ABI or contract address in `.env` and `contracts/`

---

## 🚀 Running the Project

### ⚙️ Initial Setup

```bash
git clone https://github.com/your-repo/coophive-markdown-converter.git
cd coophive-markdown-converter
bash scripts/setup.sh
poetry lock --no-update
poetry install
cp .env.example .env
# Edit the .env file with actual credentials
```

### 🛠️ Execute Main Workflows

```bash
bash scripts/run_processor.sh         # Convert, chunk, embed, store
bash scripts/run_db_creator.sh        # Recreate DBs from IPFS graph
bash scripts/run_evaluation.sh        # Compare results across DBs
bash scripts/run_token_reward.sh      # Distribute token rewards
```

### 🔍 Code Quality & Testing

```bash
bash scripts/lint.sh                  # Run black, isort, flake8, mypy
bash scripts/test.sh                  # Unit tests with pytest
```

### 💻 Poetry Shell (Optional Interactive Mode)

```bash
poetry shell                          # Drop into a virtualenv shell
```

---

## 🧩 Customization

Each module can be customized via:

- `config/*.yml` to control which converter/embedder/etc. to use
- `descidb/core` and `descidb/rewards` to add new functionality
- `.env` for runtime secrets

Add your new embedder in `embedder.py`, and reference its name in `config/processor.yml`. The system will pick it up dynamically.

---

## 🔧 Environment Variables

A `.env` file (based on `.env.example`) should include:

```bash
OPENAI_API_KEY=
NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
OWNER_ADDRESS=
PRIVATE_KEY=
LIGHTHOUSE_TOKEN=
OPENROUTER_API_KEY=
```

---

## 📜 License

This project is open-sourced under the MIT License.

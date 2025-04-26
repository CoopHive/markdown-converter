# 🧠 CoopHive: Modular RAG Pipelines for Scientific Papers

CoopHive builds RAG framework pipelines for scientific literature by providing a modular, reproducible framework. It supports customizable document processing, embedding, querying, and incentivization mechanisms, allowing decentralized and transparent science.

---

## ✨ Features

- **Modular Architecture**: Customize each stage—conversion, chunking, embedding, storage, querying, and rewards—via configuration files.
- **Reproducibility**: Deterministic pipelines with version-controlled configurations ensure consistent results.
- **Multi-Backend Support**:
  - **Conversion**: Marker, OpenAI, or custom converters.
  - **Chunking**: Paragraph, sentence, fixed-length, or custom strategies.
  - **Embedding**: OpenAI, NVIDIA, or your own models.
  - **Storage**: ChromaDB (vector database), PostgreSQL (metadata), Neo4j (graph database), IPFS (document storage).
- **Incentivization**: Distribute ERC20 tokens based on user contributions using customizable reward strategies.
- **Evaluation**: Evaluate and compare database performance using LLMs via OpenRouter.

### Philosophy

CoopHive is designed to be **modular** and **reproducible**:

- Add new conversion, chunking, and embedding strategies without affecting the core logic of the project.
- Configurable through YAML files.
- Seperate pipelines for knowledge graph creation, querying, and token incentivization.

### Tech Stack

- **Python** (project core, orchestration)
- **ChromaDB** (vector database for embeddings)
- **Neo4j** (graph database for document lineage)
- **IPFS / Lighthouse** (storage of document versions)
- **OpenAI / NVIDIA / Custom** (embedders for RAG)
- **Hardhat, Solidity** (ERC20 contracts for reward distribution)
- **Docker + Nomad** (optional containerization and deployment)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Poetry
- Node.js 18+
- Access to required APIs (OpenAI, Lighthouse, OpenRouter, etc.)

### Installation

```bash
git clone https://github.com/your-repo/coophive-markdown-converter.git
cd coophive-markdown-converter
bash scripts/setup.sh
poetry lock --no-update
poetry install
cp .env.example .env
```

### Development Commands

```bash
poetry shell                          # Open interactive dev environment
bash scripts/lint.sh                  # Code quality (black, isort, flake8, mypy)
bash scripts/test.sh --integration    # Integration tests
```

### 💡 Environment Variables

Create a `.env` file (template available in `.env.example`) with the following keys:

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

## 🛠️ Running Workflows

Execute the main pipelines using provided shell scripts:

```bash
bash scripts/run_processor.sh         # Convert, chunk, embed, store documents
bash scripts/run_db_creator.sh        # Recreate databases from IPFS and Neo4j graph to ChromaDB
bash scripts/run_evaluation.sh        # Query and evaluate across databases using agents
bash scripts/run_token_reward.sh      # Distribute blockchain-based token rewards for creation of databases
```

Or drop into a virtual environment for manual work:

```bash
poetry shell
```

---

## 🧬 Module Configuration

### ✨ Processor

- Converts PDF ➔ markdown using **Marker** or **OpenAI**
- Chunks text into paragraphs, sentences, or fixed length
- Embeds chunks using **OpenAI**, **NVIDIA**, or custom models
- Uploads to **IPFS** and stores metadata into **ChromaDB** / **Neo4j** / **Postgres**

Configuration: [`config/processor.yml`](config/processor.yml)

```yaml
converter: marker # Options: marker, openai, custom
chunker: paragraph # Options: paragraph, sentence, fixed_length, custom
embedder: openai # Options: openai, nvidia, custom
```

Define your custom classes inside `descidb/core/converter.py`, `descidb/core/chunker.py`, or `descidb/core/embedder.py` and reference them in the config.

### 🔁 DB Creator

- Traverses IPFS graph in **Neo4j** to rebuild databases
- Fetches embeddings + metadata from Lighthouse storage
- Supports different path traversal depths and relationships

Configuration: [`config/db_creator.yml`](config/db_creator.yml)

```yaml
components:
  converter:
    - marker # Recreates documents from IPFS/Neo4j converted by specified converter
  chunker:
    - fixed_length # Recreates chunks from documents converted by specified chunker
  embedder:
    - openai # Recreates embeddings from chunks embedded by specified embedder
```

```yaml
cids_file_paths:
  - cids.txt # Path to file containing CIDs of documents to recreate
```

### 🧐 Evaluation Agent

- Runs a query across different vector DBs that were created by the DB Creator module
- Uses an LLM (via **OpenRouter**) to **rank results**
- Outputs structured ranking + analysis JSONs

```yaml
query: "impact of CRISPR on neuroscience" # Query to run across vector DBs
model_name: "gpt-4" # Model to use for ranking
```

Outputs can be found in `temp/evaluation/` folder.

### 🏅 Token Rewarding

- Reads contribution data from Neo4j and creates Postgres database with token contributions
- Calculates reward based on job count, bonuses, time decay, etc.
- Issues **ERC20** tokens to contributors via smart contract

```yaml
databases: # List of databases combinations to reward
  - converter: openai
    chunker: paragraph
    embedder: openai
```

Extend `descidb/rewards/token_rewarder.py` for new reward calculation methods.

---

## 📦 Reproducibility

- All document uploads are hashed and tracked deterministically on **IPFS**.
- Stores each object (chunk, embedding, etc.) as seperate git commits to ensure reproducibility and traceability.
- Runs can be reproduced exactly by using pinned dependency versions (`poetry.lock`) and fixed configs.

---

## Directory Overview

```bash
coophive-markdown-converter/
├── config/        # YAML files controlling each pipeline
├── descidb/        # Core libraries for processing, database, rewards
├── scripts/       # Bash scripts for setup, linting, running pipelines
├── contracts/     # Blockchain smart contract ABIs
├── docker/        # Docker/Nomad job specs (optional deployment)
├── erc20-token/  # Hardhat config for token contracts
├── papers/        # Sample document files and metadata
├── tests/         # Unit + integration tests
└── .github/       # CI/CD pipelines
```

---

## 📄 License

This project is open-sourced under the MIT License.

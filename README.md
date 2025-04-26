# 🧠 CoopHive: Modular RAG Pipelines for Scientific Papers

CoopHive builds RAG framework pipelines for scientific literature by providing a modular, reproducible framework. It supports customizable document processing, embedding, querying, and incentivization mechanisms, allowing decentralized and transparent science.

---

## ✨ Features

- **Modular Architecture**: Swap out converters, chunkers, embedders, and reward strategies easily via configuration files.
- **Reproducibility**: Deterministic pipelines with version-controlled configs ensure consistent, repeatable results.
- **Transparency**: All document processing and contributions are traceable via Git commits and IPFS hashes.
- **Built-in Pipelines**:
  - Document **conversion** to markdown (Marker, OpenAI, or custom)
  - Text **chunking** (by paragraph, sentence, fixed length, or custom logic)
  - **Embedding** of chunks (OpenAI, NVIDIA, or custom models)
  - **Storage** of documents, chunks, and embeddings in Neo4j and IPFS.
  - **Recreation** of documents, chunks, and embeddings from IPFS/Neo4j to ChromaDB.
  - **Querying** of documents, chunks, and embeddings using a RAG pipeline.
  - **Evaluation** of vector DBs using an LLM via OpenRouter.
  - **Token Rewarding** of contributors based on job count, bonuses, time decay, etc.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Poetry
- Node.js 18+
- Access to required APIs (OpenAI, Lighthouse, OpenRouter, etc.)

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

### Running Modules

```bash
bash scripts/run_processor.sh         # Convert, chunk, embed, store documents
bash scripts/run_db_creator.sh         # Recreate DBs from IPFS graph
bash scripts/run_evaluation.sh         # Query and evaluate across DBs
bash scripts/run_token_reward.sh       # Distribute ERC20 token rewards
```

Or enter an interactive environment:

```bash
poetry shell
```

### Code Quality and Testing

```bash
bash scripts/lint.sh                   # Lint (black, isort, flake8, mypy)
bash scripts/test.sh --integration      # Only integration tests
```

## 🧬 Module Configuration

### ✨ Processor

- Converts PDF ➔ markdown using **Marker** or **OpenAI**
- Chunks text into paragraphs, sentences, or fixed length
- Embeds chunks using **OpenAI**, **NVIDIA**, or custom models
- Uploads to **IPFS** and stores metadata into **ChromaDB** / **Neo4j** / **Postgres**
- Logs each operation as a Git commit with the specified author

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

## 🛠️ Tech Stack

- **Python** (main orchestration)
- **ChromaDB** (vector database)
- **Neo4j** (graph lineage and job tracking)
- **IPFS / Lighthouse** (document storage)
- **OpenAI / NVIDIA / Custom** (embedding backends)
- **Hardhat + Solidity** (ERC20 reward contracts)
- **Docker + Nomad** (optional containerization)

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

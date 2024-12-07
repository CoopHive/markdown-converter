# Research Paper Processing Pipeline and Querying Database

This document provides a comprehensive guide to processing research papers into custom databases and querying those databases using the CoopHive SDK.

## Part 1: Processing Research Papers

This section explains how to the conversion of research papers (PDFs) into markdown format, extract metadata, and insert the processed documents into custom databases.

### Prerequisites

Before running the script, ensure that you have the following:

- **Python 3.12** installed
- Access to OpenAI API (with an API key)
- Lighthouse API key for file storage
- A set of research papers in PDF format

### Installation

1. **Clone the Repository:**

   ```bash
   git clone git@github.com:CoopHive/markdown-converter.git
   cd markdown-converter
   ```

2. **Install Required Packages:**

   Install the necessary Python packages using `uv`:

   ```bash
   make uv-download
   make install
   ```

3. **Prepare Your Enviornment and Metadata Files:**

   - **.env** This file should contain your API keys and other configurations.

   See .env.example as a reference.

   ```env
      OPENAI_API_KEY=your_openai_api_key
      LIGHTHOUSE_TOKEN=your_lighthouse_token
   ```

   - **metadata.json:** A JSON file containing metadata for your papers. A sample file has been created, containing the metadata of arXiv papers. Hence, unless using arXiv papers, a custom metadata file would have to be created in the format below. If metadata if not provided, it will default it to blank.

   Example metadata.json:

   ```json
   {
     "id": "paper1",
     "title": "Sample Paper",
     "authors": ["Author 1", "Author 2"],
     "categories": ["Category 1"],
     "abstract": "This is a sample abstract.",
     "doi": "10.1234/sample.doi"
   }
   ```

4. **Prepare Your Papers Directory:**

   - Place all your research paper

5. **Selecting Database Creation Methods**

   By default, the script allows you to choose from the following processing methods:

   1. **Conversion Methods:** Convert PDFs to markdown using one of the following:

      - **OpenAI Model:** Uses OpenAI's model to convert PDFs to markdown.
      - **Marker Library:** Uses the marker library/repository to convert PDFs to markdown.

   2. **Text Marking Level:**

      - **Paragraph Level:** Processes and chunks the text at the paragraph level.
      - **Sentence Level:** Processes and chunks the text at the sentence level.

   3. **Chunking Model:**

      - **NVIDIA Model:** Uses NVIDIA's model for text chunking.
      - **OpenAI Model:** Uses OpenAI's model for text chunking.

   These default methods provide a versatile framework for processing research papers into databases. Each combination of methods results in a unique database tailored to specific use cases. Select the options that best suit your research needs.

### Running the Script

## Part 2: Token Rewarding Mechanism

The **TokenRewarder** class automates the rewarding process for contributions to the research paper processing pipeline. It integrates with a PostgreSQL database and a smart contract to calculate and issue rewards to contributors. Token pools can be created by the owner of the smart contract using the contract template found in /contracts.

### Setting Up the Token Rewarder

The TokenRewarder class requires the following parameters:

- **network**: The network to connect to.
- **contract_address**: The address of the smart contract.
- **contract_abi_path**: The path to the smart contract ABI.
- **db_components**: The components of the database.
- **host**: The host of the PostgreSQL database.
- **port**: The port of the PostgreSQL
  The .env file should contain the following environment variables:

```env
   OWNER_ADDRESS=your_owner_address
   PRIVATE_KEY=your_private_key
```

### Database Structure

The `user_rewards` table is created within each database and has the following schema:

| Column       | Type      | Description                                  |
| ------------ | --------- | -------------------------------------------- |
| `id`         | SERIAL    | Primary key for the table.                   |
| `public_key` | TEXT      | The public key of the contributor.           |
| `job_count`  | INT       | The number of jobs completed by the user.    |
| `time_stamp` | TIMESTAMP | The time of the last contribution or update. |

### Rewarding Users

The rewards are added to the `user_rewards` table and can be distributed to users by calling the `get_user_rewards()` function. By default, this function uses:

````python
user_rewards = self.reward_users_default(db_name)
```sfksdfkdskf

However, this can be swapped with any of the following functions depending on the desired reward logic:

- **`reward_users_constant`**: Rewards users based on a constant reward per job count.
- **`reward_users_milestone`**: Rewards users who reach specified milestones.
- **`reward_users_after_time`**: Rewards users for contributions made after a specified time.
- **`reward_users_with_bonus`**: Adds a bonus reward for users exceeding a contribution threshold.
- **`reward_users_within_timeframe`**: Rewards users for contributions made within a specific timeframe.
- **`reward_users_by_tier`**: Rewards users based on tiers of contribution levels.

These functions calculate the rewards based on their respective logic and update the blockchain by issuing tokens to users.

### Issuing Tokens

Tokens are issued using the `issue_token()` method, which transfers the calculated reward to the contributor's blockchain address. The transaction details are managed securely using the owner's private key stored in the environment variables.

### Example Usage

See descidb/TokenScheduler.py for an example of how to use the TokenRewarder class to reward users. The TokenScheduler class is used to reward users for contributions to multiple databases. The parameters for the TokenRewarder class are passed in from the TokenScheduler class. You can add specific databases to reward users for by adding them to the databases list in TokenScheduler.py:

```python
databases = [
    {"converter": "openai", "chunker": "sentence", "embedder": "openai"},
    {"converter": "openai", "chunker": "paragraph", "embedder": "openai"},
]
````

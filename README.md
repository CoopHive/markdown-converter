# Research Paper Processing Pipeline and Querying Database

This document provides a comprehensive guide to processing research papers into custom databases and querying those databases using the CoopHive SDK.

## Part 1: Research Paper Processing Pipeline

This section explains how to automate the conversion of research papers (PDFs) into markdown format, extract metadata, and insert the processed documents into custom databases.

### Prerequisites

Before running the script, ensure that you have the following:

- **Python 3.6+** installed
- Required Python libraries installed (see below)
- Access to OpenAI API (with an API key)
- Lighthouse API key for file storage
- A set of research papers in PDF format
- Metadata for the research papers in a JSON file

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/CoopHive/markdown-converter/tree/local-marker
   cd markdown-converter
   ```

2. **Install Required Packages:**

   Install the necessary Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` should include:

   - `requests`
   - `PyPDF2`
   - `openai`
   - `chroma`
   - `torch`

3. **Prepare Your Config Files:**

   - **`config.json`:** This file should contain your API keys and other configurations.

   Example `config.json`:

   ```json
   {
     "api_key": "your-lighthouse-api-key",
     "openai_api_key": "your-openai-api-key"
   }
   ```

   - **`metadata.json`:** A JSON file containing metadata for your papers. Each line in the file should be a JSON object representing a single paper.

   Example `metadata.json`:

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

   - Place all your research paper PDFs in a directory named `papers`.

### Running the Script

1. **Execution:**

   Run the main script by executing:

   ```bash
   python local_papers.py
   ```

   The script will process each paper in the `papers` directory, extract metadata from the corresponding entry in `metadata.json`, and upload the PDF and markdown files to Lighthouse. It will then store the documents in the following databases:

   - **Paragraph Level:**

     - `para_marker_nvidia_dvd`: NVIDIA-based embedding for paragraph-marked text.
     - `para_marker_openai_dvd`: OpenAI-based embedding for paragraph-marked text.
     - `para_llm_nvidia_dvd`: NVIDIA-based embedding for LLM-processed paragraph-marked text.
     - `para_llm_openai_dvd`: OpenAI-based embedding for LLM-processed paragraph-marked text.

   - **Sentence Level:**
     - `sentence_marker_nvidia_dvd`: NVIDIA-based embedding for sentence-marked text.
     - `sentence_marker_openai_dvd`: OpenAI-based embedding for sentence-marked text.
     - `sentence_llm_nvidia_dvd`: NVIDIA-based embedding for LLM-processed sentence-marked text.
     - `sentence_llm_openai_dvd`: OpenAI-based embedding for LLM-processed sentence-marked text.

2. **Processed Papers:**

   The script keeps track of processed papers in `processed_papers.txt` to avoid reprocessing.

3. **Cleanup (Optional):**

   After processing, you can delete the output directory by uncommenting the `cleanup_directory("output")` line in the `main()` function.

## Part 2: Querying the Database with CoopHive SDK

This section walks you through the steps needed to query the database created in Part 1 using the CoopHive SDK.

### Prerequisites

Before you begin, ensure you have the following:

1. A running instance of the API.
2. A valid API key generated using the provided API.
3. The CoopHive SDK installed in your Python environment.

### Step 1: Set Up the API

To begin, you need to have the API running locally. The code for the API can be cloned from the following repository:

- [Markdown Converter - CoopHive API](https://github.com/CoopHive/markdown-converter/tree/local-marker)

Follow the instructions in the repository to set up and run the API called app.py in api_client_sdk.

### Step 2: Generate an API Key

After the API is running, you need to generate a valid API key. This can be done by sending a POST request to the `/generate_key` endpoint.

Ensure that you have the necessary `user_id` and authentication in place before attempting to generate the key.

### Step 3: Query the Database

Once you have the API key, you can use the CoopHive SDK to run queries against a specific database.

#### Example

Here’s a simple example of how to query a database using the SDK:

```python
from coophive_sdk import CoopHiveClient

api_key = "your_api_key_here"

client = CoopHiveClient(api_key=api_key)

database_name = "your_database_name_here"
user_query = "your_query_here"
response = client.queries.query_database(database_name, user_query)

```

#### Explanation

- **CoopHiveClient:** This initializes the client using your API key.
- **query_database:** This function queries the specified database with the given user query and returns the result.

### Step 4: Review the Results

The `response` variable will contain the information retrieved from the database based on your query. You can print or manipulate this data as needed for your application.

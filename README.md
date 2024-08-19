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

   - requests
   - PyPDF2
   - openai
   - chroma
   - torch

3. **Prepare Your Config Files:**

   - **config.json:** This file should contain your API keys and other configurations.

   Example config.json:

   ```json
   {
     "api_key": "your-lighthouse-api-key",
     "openai_api_key": "your-openai-api-key"
   }
   ```

   - **metadata.json:** A JSON file containing metadata for your papers. A sample file has been created, containing the metadata of arXiv papers. Hence, unless using arXiv papers, a custom metadata file would have to be created in the format below.

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

   - Place all your research paper PDFs in a directory named `papers`.

### Running the Script

1. **Execution:**

   Run the main script by executing:

   ```bash
   python local_papers.py
   ```

   The script will process each paper in the `papers` directory, extract metadata from the corresponding entry in `metadata.json`, and upload the PDF and markdown files to Lighthouse.

   ### Step 1: Choose Your Processing Options

   The script supports three options for processing research papers, creating a total of eight different databases:

   1. **Conversion Method:**

   - **OpenAI Model:** Uses OpenAI's model to convert PDFs to markdown.
   - **Marker Library:** Uses the marker library/repository to convert PDFs to markdown.

   2. **Text Marking Level:**

      - **Paragraph Level:** Processes and chunks the text at the paragraph level.
      - **Sentence Level:** Processes and chunks the text at the sentence level.

   3. **Chunking Model:**
      - **NVIDIA Model:** Uses NVIDIA's model for text chunking.
      - **OpenAI Model:** Uses OpenAI's model for text chunking.

   Each combination of these options results in a different database, allowing for flexibility in how the text is processed and queried.

   ### Step 2: Databases Created

   Based on the options chosen in Step 1, the following databases are created:

   - **Paragraph Level:**

     - `para_marker_nvidia_dvd`: Uses the marker library to convert PDFs to markdown and NVIDIA-based chunking for paragraph-marked text.
     - `para_marker_openai_dvd`: Uses the marker library to convert PDFs to markdown and OpenAI-based chunking for paragraph-marked text.
     - `para_llm_nvidia_dvd`: Uses the OpenAI model to convert PDFs to markdown and NVIDIA-based chunking for LLM-processed paragraph-marked text.
     - `para_llm_openai_dvd`: Uses the OpenAI model to convert PDFs to markdown and OpenAI-based chunking for LLM-processed paragraph-marked text.

   - **Sentence Level:**
     - `sentence_marker_nvidia_dvd`: Uses the marker library to convert PDFs to markdown and NVIDIA-based chunking for sentence-marked text.
     - `sentence_marker_openai_dvd`: Uses the marker library to convert PDFs to markdown and OpenAI-based chunking for sentence-marked text.
     - `sentence_llm_nvidia_dvd`: Uses the OpenAI model to convert PDFs to markdown and NVIDIA-based chunking for LLM-processed sentence-marked text.
     - `sentence_llm_openai_dvd`: Uses the OpenAI model to convert PDFs to markdown and OpenAI-based chunking for LLM-processed sentence-marked text.

2. **Processed Papers:**

   The script keeps track of processed papers in `processed_papers.txt` to avoid reprocessing.

3. **Cleanup (Optional):**

   After processing, you can delete the output directory by uncommenting the `cleanup_directory("output")` line in the `main()` function.

### Value of the Databases

Each of the eight databases generated through this process provides unique insights depending on the combination of text marking level, conversion method, and chunking model used:

### 1. Measuring Different Query Results

- **Tailored Query Responses:** By having databases with different configurations, you can compare how different processing methods affect the retrieval of information. For example, you can evaluate whether paragraph-level chunking provides more accurate or relevant results compared to sentence-level chunking for certain types of queries.
- **Domain-Specific Optimization:** If your research papers belong to a highly specialized domain, you can experiment with different chunking and conversion methods to see which combination yields the most relevant results. This allows for domain-specific optimization, particularly valuable in fields like medicine, law, or technical research.

### 2. Understanding Model Performance

- **Data-Driven Model Fine-Tuning:** By using both NVIDIA and OpenAI models for chunking, you can determine which model performs better for your specific dataset. This can be particularly useful for tasks that require high precision in text retrieval or when working with specialized content.
- **Transfer Learning Opportunities:** The insights gained from comparing results across different databases can inform transfer learning strategies. For example, findings from sentence-level databases might be applied to enhance paragraph-level models, or vice versa, creating a more robust overall system.

### 3. Conversion Method Impact

- **Multiple Perspectives on Data:** The choice between using the OpenAI model and the marker library for converting PDFs to markdown can influence the structure and quality of the extracted text. By comparing results across databases that use different conversion methods, you can identify the strengths and weaknesses of each approach.
- **Redundancy for Critical Applications:** In mission-critical applications, having multiple databases provides redundancy, ensuring that even if one method or model fails, others can provide backup, increasing the reliability and robustness of your system.

These databases collectively offer a robust framework for experimenting with and fine-tuning the text processing and retrieval pipeline, enabling you to make data-driven decisions about which methods to deploy in production.

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

---

This guide provides a complete walkthrough from processing research papers into databases to querying those databases using the CoopHive SDK. Ensure you follow each step carefully to set up your environment and execute your queries successfully. For more advanced usage and customization, refer to the official SDK documentation.

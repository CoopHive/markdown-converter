# Research Paper Processing Pipeline

This script is designed to automate the process of converting research papers (PDFs) into markdown format, extracting metadata, and inserting the processed documents into custom databases. It supports both NVIDIA and OpenAI models for text processing.

## Prerequisites

Before running the script, ensure that you have the following:

- **Python 3.6+** installed
- Required Python libraries installed (see below)
- Access to OpenAI API (with an API key)
- Lighthouse API key for file storage
- A set of research papers in PDF format
- Metadata for the research papers in a JSON file

## Installation

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

## Running the Script

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

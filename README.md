# Research Paper Processing Pipeline and Querying Database

This document provides a comprehensive guide to processing research papers into custom databases and querying those databases using the CoopHive SDK.

## Part 1: Research Paper Processing Pipeline

This section explains how to automate the conversion of research papers (PDFs) into markdown format, extract metadata, and insert the processed documents into custom databases.

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

3. **Prepare Your Enviornment Files:**

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

   - Place all your research paper PDFs in a directory named `papers`. Name the papers with its corresponding id from the metadata.json section.

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

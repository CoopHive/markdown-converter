# arXiv Preprints Scraper and PDF Processor

This repository contains a script for handling arXiv preprints, including downloading PDFs and scraping preprint metadata.

## Usage

The script can be used in two modes based on the value of the `download` variable:

### Mode 1: Download PDFs

If `download` is set to `True`, the script processes pre-downloaded PDFs from a specified directory.

1. Place the PDFs you want to process in a directory named `papers`.
2. Ensure the `download` variable is set to `True` in the script.
3. Run the script. It will:
   - Upload each PDF to Lighthouse storage.
   - Execute a Hive command for each uploaded PDF.
   - Extract and process the output from Hive.

```python
download = True
```

### Mode 2: Scrape arXiv

If `download` is set to `False`, the script scrapes arXiv for preprints within a specified category and date range.

Ensure the `download` variable is set to `False` in the script.
Set the `category`, `date_from`, and `date_until` variables to define the scrape parameters.
Run the script. It will:

- Scrape metadata of preprints from arXiv.
- Download the PDFs of the scraped preprints.
- Upload each PDF to Lighthouse storage.
- Execute a Hive command for each uploaded PDF.
- Extract and process the output from Hive.

```python
download = False
category = 'physics:cond-mat'
date_from = '2024-05-13'
date_until = '2024-05-14'
```

## Running the Script

To run the script, ensure you have the necessary dependencies installed and environment variables set:

1. Install dependencies:

   ```bash
   pip install arxivscraper pandas requests
   ```

2. Set your Lighthouse API key and Hive private key in the script:

   ```python
   api_key = "YOUR_LIGHTHOUSE_API_KEY"
   private_key = "YOUR_HIVE_PRIVATE_KEY"
   ```

3. Execute the script:
   ```bash
   python script_name.py
   ```

## Output

The script will print information about the processed preprints, including their arXiv IDs, metadata, and Hive processing results.

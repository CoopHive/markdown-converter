import arxivscraper
import pandas as pd
import requests
import os
import subprocess
import json
import shutil
from db import DocumentDatabase


def scrape_arxiv(category='physics:cond-mat', date_from='2024-05-13', date_until='2024-05-14'):
    scraper = arxivscraper.Scraper(
        category=category, date_from=date_from, date_until=date_until)
    output = scraper.scrape()
    cols = ('id', 'title', 'categories', 'abstract',
            'doi', 'created', 'updated', 'authors')
    df = pd.DataFrame(output, columns=cols)
    df.to_csv('arxiv_preprints_may_2024.csv', index=False)
    return df


def download_pdf(arxiv_id, filename):
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    response = requests.get(pdf_url)
    response.raise_for_status()
    with open(filename, 'wb') as pdf_file:
        pdf_file.write(response.content)


def upload_to_lighthouse(filepath, api_key):
    url = 'https://node.lighthouse.storage/api/v0/add'
    headers = {'Authorization': f'Bearer {api_key}'}
    with open(filepath, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
        return response.json()['Hash']


def execute_marker_module(pdf_file, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        command = [
            "marker_single",
            pdf_file,
            output_dir,
            "--langs", "English"
        ]
        subprocess.run(command, check=True)
        return output_dir
    except subprocess.CalledProcessError as e:
        print(f"Error running marker for {pdf_file}: {e}")
        return None


def scrape_and_download_papers(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)

    api_key = config.get('api_key')
    category = config.get('category', 'physics:cond-mat')
    date_from = config.get('date_from', '2024-05-13')
    date_until = config.get('date_until', '2024-05-14')
    num_pdfs = config.get('num_pdfs', 2)

    papers_info = {}
    output_base_dir = "output"
    inputs_base_dir = "inputs"
    os.makedirs(output_base_dir, exist_ok=True)
    os.makedirs(inputs_base_dir, exist_ok=True)

    df = scrape_arxiv(category, date_from, date_until)
    valid_indices = df['id'].dropna().index[:num_pdfs]

    print(f"Downloading {num_pdfs} papers...")

    for idx in valid_indices:
        arxiv_id = df.loc[idx, 'id']
        try:
            filename = os.path.join(inputs_base_dir, f"paper_{idx}.pdf")
            download_pdf(arxiv_id, filename)

            output_dir = execute_marker_module(filename, output_base_dir)
            if output_dir:
                subdir_name = os.path.splitext(os.path.basename(filename))[0]
                markdown_filename = f"{subdir_name}.md"
                markdown_path = os.path.join(
                    output_dir, subdir_name, markdown_filename)

                if not os.path.exists(markdown_path):
                    raise FileNotFoundError(
                        f"Markdown file not found: {markdown_path}")

                markdown_cid = upload_to_lighthouse(markdown_path, api_key)
                pdf_cid = upload_to_lighthouse(filename, api_key)

                with open(markdown_path, 'r') as file:
                    file_contents = file.read()

                paper_info = {
                    "file_contents": file_contents,
                    "doi": df.loc[idx, 'doi'],
                    "title": df.loc[idx, 'title'],
                    "categories": df.loc[idx, 'categories'],
                    "authors": df.loc[idx, 'authors'],
                    "created": df.loc[idx, 'created'],
                    "abstract": df.loc[idx, 'abstract'],
                    "pdf_cid": pdf_cid,
                    "markdown_cid": markdown_cid
                }

                papers_info[arxiv_id] = paper_info
        except requests.RequestException as e:
            print(f"Failed to process arXiv ID: {arxiv_id}. Error: {e}")
        except subprocess.CalledProcessError as e:
            print(
                f"Error executing command for arXiv ID: {arxiv_id}. Error: {e}")
            print(f"Command output: {e.output}")
            print(f"Command stderr: {e.stderr}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")

    db_instance = DocumentDatabase(api_key)
    db_instance.create_database("chroma_vector_database", "1.0")

    for paper_id, info in papers_info.items():
        metadata = {
            'file_contents': info['file_contents'],
            'source': 'academic_paper',
            'author': ', '.join(info['authors']),
            'year': info['created'],
            'title': info['title'],
            'categories': info['categories'],
            'doi': info['doi'],
            'pdf_cid': info['pdf_cid'],
            'markdown_cid': info['markdown_cid']
        }

        db_instance.insert_document(info['file_contents'], paper_id, metadata)


def cleanup_directory(directory):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Deleted directory: {directory}")
    except Exception as e:
        print(f"Error deleting directory {directory}: {e}")


def cleanup_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")


def main():
    config_file = "config.json"

    print("Starting script...")

    scrape_and_download_papers(config_file)

    # Clean up the input and output directories
    cleanup_directory("inputs")
    cleanup_directory("output")
    cleanup_file("arxiv_preprints_may_2024.csv")


if __name__ == "__main__":
    print("Running main function...")
    main()

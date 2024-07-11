import arxivscraper
import pandas as pd
import requests
import os
import subprocess
import re
import json
from db import create_database, insert_document


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


def execute_hive_command(cid, private_key):
    command = f"""
        hive run marker:de3ebcd -i input=/inputs/{cid} -i url=https://gateway.lighthouse.storage/ipfs/{cid}
    """
    env_var = os.environ.copy()
    env_var["WEB3_PRIVATE_KEY"] = private_key
    result = subprocess.run(command, shell=True, env=env_var, check=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result


def extract_path(output):
    pattern = r"/tmp/coophive/data/downloaded-files/Qm[a-zA-Z0-9]+"
    match = re.search(pattern, output)

    if match:
        return match.group(0)
    else:
        return None


def upload_markdown_to_ipfs(markdown_path, api_key):
    try:
        cid = upload_to_lighthouse(markdown_path, api_key)
        return cid
    except requests.RequestException as e:
        print(f"Failed to upload markdown to IPFS. Error: {e}")
        return None


def scrape_and_download_papers(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)

    api_key = config.get('api_key')
    private_key = config.get('private_key')
    category = config.get('category', 'physics:cond-mat')
    date_from = config.get('date_from', '2024-05-13')
    date_until = config.get('date_until', '2024-05-14')
    num_pdfs = config.get('num_pdfs', 2)

    papers_info = {}

    df = scrape_arxiv(category, date_from, date_until)
    valid_indices = df['id'].dropna().index[:num_pdfs]

    print(f"Downloading {num_pdfs} papers...")

    for idx in valid_indices:
        arxiv_id = df.loc[idx, 'id']
        try:
            filename = f"paper_{idx}.pdf"
            download_pdf(arxiv_id, filename)
            pdf_cid = upload_to_lighthouse(filename, api_key)
            result = execute_hive_command(pdf_cid, private_key)
            path = extract_path(result.stdout)
            if path:
                markdown_path = os.path.join(path, "outputs", "output.md")
                markdown_cid = upload_markdown_to_ipfs(markdown_path, api_key)
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
            print(
                f"Failed to process arXiv ID: {arxiv_id}. Error: {e}")
        except subprocess.CalledProcessError as e:
            print(
                f"Error executing command for arXiv ID: {arxiv_id}. Error: {e}")
            print(f"Command output: {e.output}")
            print(f"Command stderr: {e.stderr}")
        except FileNotFoundError as e:
            print(f"File not found: {e}")

    collection = create_database("chroma_vector_database", "1.0")

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

        insert_document(collection, info['file_contents'], paper_id, metadata)


def process_downloaded_papers(api_key, private_key, papers_directory="papers"):
    papers_info = {}

    for filename in os.listdir(papers_directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(papers_directory, filename)
            print(f"Processing file: {filename}")
            try:
                pdf_cid = upload_to_lighthouse(filepath, api_key)
                print(f"Uploaded file to Lighthouse. CID: {pdf_cid}")
                result = execute_hive_command(pdf_cid, private_key)
                print(f"Executed Hive command for file: {filename}")
                print(str(result.stderr))
                path = extract_path(result.stdout)
                if path:
                    markdown_path = os.path.join(path, "outputs", "output.md")
                    markdown_cid = upload_markdown_to_ipfs(
                        markdown_path, api_key)
                    with open(markdown_path, 'r') as file:
                        file_contents = file.read()

                    paper_info = {
                        "file_contents": file_contents,
                        "pdf_cid": pdf_cid,
                        "markdown_cid": markdown_cid
                    }

                    papers_info[filename] = paper_info
            except requests.RequestException as e:
                print(
                    f"Failed to upload PDF for file: {filename}. Error: {e}")
            except subprocess.CalledProcessError as e:
                print(
                    f"Error executing command for file: {filename}. Error: {e}")
                print(f"Command output: {e.output}")
                print(f"Command stderr: {e.stderr}")
            except FileNotFoundError as e:
                print(f"File not found: {e}")

    for filename, info in papers_info.items():
        print(f"Filename: {filename}")
        for key, value in info.items():
            print(f"{key}: {value}")
        print("\n")


def main():
    config_file = "config.json"
    with open(config_file, 'r') as file:
        config = json.load(file)

    api_key = config.get('api_key')
    private_key = config.get('private_key')
    download = config.get('download', False)

    print("Starting script...")

    if download:
        process_downloaded_papers(api_key, private_key)
    else:
        scrape_and_download_papers(config_file)


if __name__ == "__main__":
    print("Running main function...")
    main()

import arxivscraper
import pandas as pd
import requests
import os
import subprocess
import re


def scrape_arxiv(category, date_from, date_until):
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


def main():
    api_key = "LIGHTHOUSE API KEY"
    private_key = "PRIVATE KEY WALLET"
    num_pdfs = 2
    download = True

    papers_info = {}

    if download:

        # Download papers to the papers directory in the PDF Format

        papers_directory = "papers"
        for filename in os.listdir(papers_directory):
            if filename.endswith(".pdf"):
                filepath = os.path.join(papers_directory, filename)
                print(f"Processing file: {filename}")
                try:
                    cid = upload_to_lighthouse(filepath, api_key)
                    print(f"Uploaded file to Lighthouse. CID: {cid}")
                    result = execute_hive_command(cid, private_key)
                    print(f"Executed Hive command for file: {filename}")
                    print(str(result.stderr))
                    path = extract_path(result.stdout)
                    if path:
                        path += "/outputs/output.md"
                        with open(path, 'r') as file:
                            file_contents = file.read()

                        paper_info = {
                            "file_contents": file_contents,
                            "cid": cid
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
    else:

        # Scrape arXiv for preprints in the specified category and date range

        category = 'physics:cond-mat'
        date_from = '2024-05-13'
        date_until = '2024-05-14'

        df = scrape_arxiv(category, date_from, date_until)
        valid_indices = df['id'].dropna().index[:num_pdfs]

        for idx in valid_indices:
            arxiv_id = df.loc[idx, 'id']
            try:
                filename = f"paper_{idx}.pdf"
                download_pdf(arxiv_id, filename)
                cid = upload_to_lighthouse(filename, api_key)
                result = execute_hive_command(cid, private_key)
                path = extract_path(result.stdout)
                if path:
                    path += "/outputs/output.md"
                    with open(path, 'r') as file:
                        file_contents = file.read()

                    paper_info = {
                        "file_contents": file_contents,
                        "doi": df.loc[idx, 'doi'],
                        "title": df.loc[idx, 'title'],
                        "categories": df.loc[idx, 'categories'],
                        "authors": df.loc[idx, 'authors'],
                        "created": df.loc[idx, 'created'],
                        "abstract": df.loc[idx, 'abstract'],
                        "cid": cid
                    }

                    papers_info[arxiv_id] = paper_info
            except requests.RequestException as e:
                print(
                    f"Failed to download PDF for arXiv ID: {arxiv_id}. Error: {e}")
            except subprocess.CalledProcessError as e:
                print(
                    f"Error executing command for arXiv ID: {arxiv_id}. Error: {e}")
                print(f"Command output: {e.output}")
                print(f"Command stderr: {e.stderr}")
            except FileNotFoundError as e:
                print(f"File not found: {e}")

    for arxiv_id, info in papers_info.items():
        print(f"arXiv ID: {arxiv_id}")
        for key, value in info.items():
            print(f"{key}: {value}")
        print("\n")


if __name__ == "__main__":
    main()

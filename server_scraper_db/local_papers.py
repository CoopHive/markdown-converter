import os
import subprocess
import shutil
import requests
from db import DocumentDatabase
import json


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


def upload_to_lighthouse(filepath, api_key):
    url = 'https://node.lighthouse.storage/api/v0/add'
    headers = {'Authorization': f'Bearer {api_key}'}
    with open(filepath, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, headers=headers, files=files)
        return response.json()['Hash']


def get_metadata_for_paper(metadata_file, paper_id):
    with open(metadata_file, 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                if data.get('id') == paper_id:
                    return data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue
    return {}


def process_papers(papers_directory, metadata_file, config_file, max_papers=2):
    with open(config_file, 'r') as file:
        config = json.load(file)

    api_key = config.get('api_key')
    output_base_dir = "output"
    os.makedirs(output_base_dir, exist_ok=True)

    OPENAI_API_KEY = "sk-proj-OqH5ok75imwtsbJKZrH7T3BlbkFJK9fL3mmdg5e4uryrf9vd"

    db_instance = DocumentDatabase(OPENAI_API_KEY)
    para_nvidia_dvd, para_openai_dvd = db_instance.create_database(
        "dvd_paragraph")

    db_instance.print_all_documents(para_openai_dvd)

    sentence_nvidia_dvd, sentence_openai_dvd = db_instance.create_database(
        "dvd_sentence")

    processed_count = 0
    for filename in os.listdir(papers_directory):
        if filename.endswith(".pdf"):
            paper_id = filename[:-4]
            pdf_file = os.path.join(papers_directory, filename)
            try:
                metadata = get_metadata_for_paper(metadata_file, paper_id)

                output_dir = execute_marker_module(pdf_file, output_base_dir)
                if output_dir:
                    subdir_name = os.path.splitext(
                        os.path.basename(pdf_file))[0]
                    markdown_filename = f"{subdir_name}.md"
                    markdown_path = os.path.join(
                        output_dir, subdir_name, markdown_filename)

                    if not os.path.exists(markdown_path):
                        raise FileNotFoundError(
                            f"Markdown file not found: {markdown_path}")

                    markdown_cid = upload_to_lighthouse(markdown_path, api_key)
                    pdf_cid = upload_to_lighthouse(pdf_file, api_key)

                    with open(markdown_path, 'r') as file:
                        file_contents = file.read()

                paper_info = {
                    "file_contents": file_contents,
                    "pdf_cid": pdf_cid,
                    "markdown_cid": markdown_cid,
                    "title": metadata.get("title", "Unknown Title"),
                    "authors": metadata.get("authors", "Unknown Authors"),
                    "categories": metadata.get("categories", "Unknown Categories"),
                    "abstract": metadata.get("abstract", "No abstract available."),
                    "doi": metadata.get("doi", "No DOI available")
                }

                db_instance.insert_document(
                    document=file_contents,
                    collection=para_nvidia_dvd,
                    doc_id=filename,
                    metadata=paper_info,
                    chunk_strategy='paragraph',
                    embed_strategy='nvidia'
                )

                # db_instance.insert_document(
                #     document=file_contents,
                #     collection=para_openai_dvd,
                #     doc_id=filename,
                #     metadata=paper_info,
                #     chunk_strategy='paragraph'
                # )

                # db_instance.insert_document(
                #     document=file_contents,
                #     collection=sentence_nvidia_dvd,
                #     doc_id=filename,
                #     metadata=paper_info,
                #     chunk_strategy='sentence',
                # )

                # db_instance.insert_document(
                #     document=file_contents,
                #     collection=sentence_openai_dvd,
                #     doc_id=filename,
                #     metadata=paper_info,
                #     chunk_strategy='sentence'
                # )

                processed_count += 1
                if processed_count >= 1:
                    break

            except subprocess.CalledProcessError as e:
                print(
                    f"Error executing command for PDF file: {pdf_file}. Error: {e}")
                print(f"Command output: {e.output}")
                print(f"Command stderr: {e.stderr}")
            except FileNotFoundError as e:
                print(f"File not found: {e}")
            except requests.RequestException as e:
                print(f"Failed to upload file: {pdf_file}. Error: {e}")


def cleanup_directory(directory):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Deleted directory: {directory}")
    except Exception as e:
        print(f"Error deleting directory {directory}: {e}")


def main():
    config_file = "config.json"
    metadata_file = "metadata.json"
    papers_directory = "papers"

    print("Starting script...")

    process_papers(papers_directory, metadata_file, config_file)

    # cleanup_directory("output")


if __name__ == "__main__":
    print("Running main function...")
    main()

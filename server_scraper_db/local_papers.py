import os
import subprocess
import shutil
import requests
from db import DocumentDatabase
import json
import PyPDF2
from openai import OpenAI


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


def upload_pdf(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    text_content = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text_content += page.extract_text()

    return text_content


def chunk_text(text, chunk_size=10000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def convert_pdf_to_markdown_openai(file_content, api_key):
    client = OpenAI(api_key=api_key)
    chunks = chunk_text(file_content)
    markdown_chunks = []

    for chunk in chunks:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Convert the following text to Markdown:\n\n{chunk}",
                }
            ]
        )

        if response and response.choices:
            markdown_chunks.append(response.choices[0].message.content)
        else:
            print('Failed to convert chunk to Markdown.')
            markdown_chunks.append('')

    return '\n'.join(markdown_chunks)


def process_papers(papers_directory, metadata_file, config_file, processed_papers_file="processed_papers.txt", max_papers=1):
    with open(config_file, 'r') as file:
        config = json.load(file)

    api_key = config.get('api_key')
    author_public_key = config.get('author_key')
    output_base_dir = "output"
    os.makedirs(output_base_dir, exist_ok=True)

    OPENAI_API_KEY = config.get('openai_api_key')

    db_instance = DocumentDatabase(OPENAI_API_KEY)

    para_marker_nvidia_dvd, para_marker_openai_dvd = db_instance.create_database(
        "dvd_paragraph_marker")

    para_llm_nvidia_dvd, para_llm_openai_dvd = db_instance.create_database(
        "dvd_paragraph_llm")

    sentence_marker_nvidia_dvd, sentence_marker_openai_dvd = db_instance.create_database(
        "dvd_sentence_marker")

    sentence_llm_nvidia_dvd, sentence_llm_openai_dvd = db_instance.create_database(
        "dvd_sentence_llm")

    if os.path.exists(processed_papers_file):
        with open(processed_papers_file, 'r') as file:
            processed_papers = set(file.read().splitlines())
    else:
        processed_papers = set()

    for filename in os.listdir(papers_directory):
        if filename.endswith(".pdf"):
            paper_id = filename[:-4]

            if paper_id in processed_papers:
                print(
                    f"Paper {paper_id} has already been processed. Skipping.")
                continue

            pdf_file = os.path.join(papers_directory, filename)
            metadata = get_metadata_for_paper(metadata_file, paper_id)
            pdf_cid = upload_to_lighthouse(pdf_file, api_key)
            try:
                output_dir = execute_marker_module(pdf_file, output_base_dir)
                subdir_name = os.path.splitext(
                    os.path.basename(pdf_file))[0]
                markdown_filename = f"{subdir_name}.md"
                markdown_path = os.path.join(
                    output_dir, subdir_name, markdown_filename)

                if not os.path.exists(markdown_path):
                    raise FileNotFoundError(
                        f"Markdown file not found: {markdown_path}")

                markdown_cid = upload_to_lighthouse(markdown_path, api_key)

                with open(markdown_path, 'r') as file:
                    file_contents_marker = file.read()

                # # Step 2: Execute openai converter

                pdf_text = upload_pdf(pdf_file)
                file_contents_openai = convert_pdf_to_markdown_openai(
                    pdf_text, OPENAI_API_KEY)

                openai_markdown_path = os.path.join(
                    output_dir, subdir_name, f"{subdir_name}_openai.md")

                with open(openai_markdown_path, 'w') as openai_md_file:
                    openai_md_file.write(file_contents_openai)

                openai_markdown_cid = upload_to_lighthouse(
                    openai_markdown_path, api_key)

                paper_info = {
                    "pdf_cid": pdf_cid,
                    "markdown_cid": markdown_cid,
                    "title": metadata.get("title", "Unknown Title"),
                    "authors": metadata.get("authors", "Unknown Authors"),
                    "categories": metadata.get("categories", "Unknown Categories"),
                    "abstract": metadata.get("abstract", "No abstract available."),
                    "doi": metadata.get("doi", "No DOI available")
                }

                paper_info_openai = {
                    "pdf_cid": pdf_cid,
                    "markdown_cid": openai_markdown_cid,
                    "title": metadata.get("title", "Unknown Title"),
                    "authors": metadata.get("authors", "Unknown Authors"),
                    "categories": metadata.get("categories", "Unknown Categories"),
                    "abstract": metadata.get("abstract", "No abstract available."),
                    "doi": metadata.get("doi", "No DOI available")
                }

                db_instance.insert_document(
                    document=file_contents_marker,
                    collection=para_marker_nvidia_dvd,
                    doc_id=filename,
                    metadata=paper_info,
                    chunk_strategy='paragraph',
                    embed_strategy='nvidia',
                    postgresdb='dvd_paragraph_marker_nvidia',
                    author=author_public_key
                )

                print("Inserted document into para_marker_nvidia_dvd")

                db_instance.insert_document(
                    document=file_contents_marker,
                    collection=para_marker_openai_dvd,
                    doc_id=filename,
                    metadata=paper_info,
                    chunk_strategy='paragraph',
                    postgresdb='dvd_paragraph_marker_openai',
                    author=author_public_key
                )

                print("Inserted document into para_marker_openai_dvd")

                db_instance.insert_document(
                    document=file_contents_marker,
                    collection=sentence_marker_nvidia_dvd,
                    doc_id=filename,
                    metadata=paper_info,
                    chunk_strategy='sentence',
                    embed_strategy='nvidia',
                    postgresdb='dvd_sentence_marker_nvidia',
                    author=author_public_key
                )

                print("Inserted document into sentence_marker_nvidia_dvd")

                db_instance.insert_document(
                    document=file_contents_marker,
                    collection=sentence_marker_openai_dvd,
                    doc_id=filename,
                    metadata=paper_info,
                    chunk_strategy='sentence',
                    postgresdb='dvd_sentence_marker_openai',
                    author=author_public_key
                )

                print("Inserted document into sentence_marker_openai_dvd")

                db_instance.insert_document(
                    document=file_contents_openai,
                    collection=para_llm_nvidia_dvd,
                    doc_id=filename,
                    metadata=paper_info_openai,
                    chunk_strategy='paragraph',
                    embed_strategy='nvidia',
                    postgresdb='dvd_paragraph_llm_nvidia',
                    author=author_public_key
                )

                print("Inserted document into para_llm_nvidia_dvd")

                db_instance.insert_document(
                    document=file_contents_openai,
                    collection=para_llm_openai_dvd,
                    doc_id=filename,
                    metadata=paper_info_openai,
                    chunk_strategy='paragraph',
                    postgresdb='dvd_paragraph_llm_openai',
                    author=author_public_key
                )

                print("Inserted document into para_llm_openai_dvd")

                db_instance.insert_document(
                    document=file_contents_openai,
                    collection=sentence_llm_nvidia_dvd,
                    doc_id=filename,
                    metadata=paper_info_openai,
                    chunk_strategy='sentence',
                    embed_strategy='nvidia',
                    postgresdb='dvd_sentence_llm_nvidia',
                    author=author_public_key
                )

                print("Inserted document into sentence_llm_nvidia_dvd")

                db_instance.insert_document(
                    document=file_contents_openai,
                    collection=sentence_llm_openai_dvd,
                    doc_id=filename,
                    metadata=paper_info_openai,
                    chunk_strategy='sentence',
                    postgresdb='dvd_sentence_llm_openai',
                    author=author_public_key
                )

                print("Inserted document into sentence_llm_openai_dvd")
                print("-----------------------------")
                print("-----------------------------")
                print("-----------------------------")
                print("-----------------------------")

                with open(processed_papers_file, 'a') as file:
                    file.write(f"{paper_id}\n")

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

    cleanup_directory("output")


if __name__ == "__main__":
    print("Running main function...")
    main()

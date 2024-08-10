import os
import PyPDF2
import requests
from openai import OpenAI


api_key = ""

client = OpenAI(api_key=api_key)


def upload_pdf(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    text_content = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text_content += page.extract_text()

    return text_content


def convert_pdf_to_markdown(file_content):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
                                              messages=[
                                                  {
                                                      "role": "user",
                                                      "content": f"Convert the content of the following file to Markdown:\n\n{file_content}",
                                                  }
                                              ])

    if response and response.choices:
        return response.choices[0].message.content
    else:
        print('Failed to convert PDF to Markdown.')
        return None


def main():
    file_path = 'test.pdf'
    file_content = upload_pdf(file_path)

    if file_content:
        markdown_content = convert_pdf_to_markdown(file_content)
        if markdown_content:
            print(markdown_content)


if __name__ == "__main__":
    main()

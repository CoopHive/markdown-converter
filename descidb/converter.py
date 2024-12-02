import os
from typing import Literal

import PyPDF2
from dotenv import load_dotenv
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.logger import configure_logging
from marker.models import create_model_dict
from openai import OpenAI

load_dotenv(override=True)
configure_logging()


ConversionType = Literal["marker", "openai"]


def convert(conversion_type: ConversionType, input_path: str) -> str:
    """Convert based on the specified conversion type."""
    # Mapping conversion types to functions
    conversion_methods = {
        "marker": marker,
        "openai": openai,
    }

    return conversion_methods[conversion_type](input_path)


def marker(input_path: str) -> str:
    """Convert text using the marker module, where input_path is either a path to pdf file or a path to a folder containing a set of pdf files."""
    try:
        # Ensure the input_path is a valid file
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input path not found: {input_path}")

        # Check if the path is a file and a PDF
        if os.path.isfile(input_path):
            if input_path.lower().endswith(".pdf"):
                input_pdf_paths = [input_path]
            else:
                raise ValueError(f"File at {input_path} is not a PDF.")

        # Check if the path is a folder containing PDFs
        elif os.path.isdir(input_path):
            input_pdf_paths = [
                os.path.join(input_path, f)
                for f in os.listdir(input_path)
                if f.lower().endswith(".pdf")
            ]
            if not input_pdf_paths:
                raise ValueError(f"No PDF files found in directory: {input_path}")
        else:
            raise ValueError(f"Invalid input path: {input_path}")

        models = create_model_dict()
        config_parser = ConfigParser(
            {
                "languages": "en",
                "output_format": "markdown",
            }
        )

        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=models,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
        )

        std_out = ""
        for pdf_path in input_pdf_paths:
            rendered = converter(pdf_path)
            rendered_markdown = rendered.markdown
            std_out += rendered_markdown

        return std_out

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return ""  # Return empty string in case of error


def extract_text_from_pdf(input_path: str) -> str:
    """Extracts text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(input_path)
    text_content = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text_content += page.extract_text()

    return text_content


def openai(input_path: str) -> str:
    """Convert text using the OpenAI API."""
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        pdf_text = extract_text_from_pdf(input_path)

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Convert the following text to Markdown:\n\n{pdf_text}",
                },
            ],
        )

        if response and response.choices:
            return response.choices[0].message.content
        else:
            print("Failed to convert text using OpenAI.")
            return pdf_text

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

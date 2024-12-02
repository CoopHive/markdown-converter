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
    """Convert text using the marker module, where input_path is a path to a file."""
    try:
        # Ensure the input_path is a valid file
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

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

        rendered = converter(input_path)
        return rendered.markdown

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

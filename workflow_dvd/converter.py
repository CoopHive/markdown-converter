import os
import subprocess
from typing import List
from openai import OpenAI
import PyPDF2


class Converter:

    def marker(self, input_path: str) -> str:
        """Convert text using the marker module, where input_path is a path to a file."""
        try:
            # Ensure the input_path is a valid file
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")

            # Directory for the output of the marker module
            output_dir = "output_marker"
            os.makedirs(output_dir, exist_ok=True)

            # Command to execute the marker module, passing the file path directly
            command = ["marker_single", input_path,
                       output_dir, "--langs", "English"]
            subprocess.run(command, check=True)

            # Assuming marker module outputs a file in the output_dir
            output_file_path = os.path.join(output_dir, "marker_output.txt")
            if os.path.exists(output_file_path):
                with open(output_file_path, "r") as output_file:
                    result = output_file.read()
            else:
                raise FileNotFoundError(
                    f"Marker output file not found in: {output_dir}")

            return result  # Return the processed result

        except subprocess.CalledProcessError as e:
            print(f"Error running marker module: {e}")
            return ""  # Return empty string in case of error
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return ""  # Return empty string in case of error

    def openai(self, input_path: str) -> str:
        """Convert text using the OpenAI API, where input_path is a path to a PDF file."""
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")

            # Extract text from the PDF file
            pdf_text = self.extract_text_from_pdf(input_path)

            OPENAI_API_KEY = "ENTER_API_KEY_HERE"
            client = OpenAI(api_key=OPENAI_API_KEY)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"Convert the following text to Markdown:\n\n{pdf_text}"},
                ]
            )

            if response and response.choices:
                return response.choices[0].message.content
            else:
                print('Failed to convert text using OpenAI.')
                return pdf_text

        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return ""
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""

    def extract_text_from_pdf(self, input_path: str) -> str:
        """Extracts text from a PDF file."""
        pdf_reader = PyPDF2.PdfReader(input_path)
        text_content = ""

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text()

        return text_content

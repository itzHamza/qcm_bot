import subprocess
import tempfile
import os

def convert_pdf_to_html(pdf_file_path):
    """
    Converts a PDF file to HTML using pdf2htmlEX.

    Args:
        pdf_file_path (str): The path to the PDF file.

    Returns:
        str: The path to the generated HTML file.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_filename = 'output.html'
        # pdf2htmlEX seems to have trouble with absolute output paths.
        # By setting cwd, we can use a relative output path.
        command = ['pdf2htmlEX', os.path.abspath(pdf_file_path), output_filename]

        try:
            with open('stdout.log', 'w') as stdout_f, open('stderr.log', 'w') as stderr_f:
                result = subprocess.run(
                    command,
                    check=True,
                    stdout=stdout_f,
                    stderr=stderr_f,
                    text=True,
                    cwd=temp_dir
                )

            output_file_path = os.path.join(temp_dir, output_filename)
            with open(output_file_path, 'r') as f:
                html_content = f.read()
            return html_content
        except subprocess.CalledProcessError as e:
            with open('stderr.log', 'r') as f:
                stderr_content = f.read()
            print(f"Error during PDF to HTML conversion: {stderr_content}")
            raise Exception(f"Error during PDF to HTML conversion: {stderr_content}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e

import os
from fastapi import UploadFile
import requests
from PyPDF2 import PdfReader

# ---------------- File Upload Helper ---------------- #
def save_uploaded_file(file: UploadFile, directory: str = "uploads") -> str:
    """
    Saves the uploaded file to the specified directory.

    Args:
        file (UploadFile): The file object uploaded by the user.
        directory (str): Directory to save the uploaded file. Defaults to 'uploads'.

    Returns:
        str: The file path where the file is saved.
    """
    # Ensure the upload directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the file path and save the file
    path = os.path.join(directory, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())

    return path

# ---------------- Extract Data from DOI ---------------- #
def extract_from_doi(doi: str) -> str:
    """
    Extracts data from a DOI (Digital Object Identifier) by making a request to the DOI API.

    Args:
        doi (str): The DOI of the research paper.

    Returns:
        str: The BibTeX citation or an error message.
    """
    url = f"https://doi.org/{doi}"
    try:
        response = requests.get(url, headers={"Accept": "application/x-bibtex"})
        if response.status_code == 200:
            return response.text
        else:
            return f"DOI fetch failed with status code {response.status_code}"
    except Exception as e:
        return f"Error fetching DOI: {str(e)}"

# ---------------- Extract Data from URL ---------------- #
def extract_from_url(url: str) -> str:
    """
    Extracts content from a URL.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        str: The content of the URL or an error message.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"URL fetch failed with status code {response.status_code}"
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

# ---------------- PDF Text Extraction ---------------- #
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

# ---------------- Text Cleaning ---------------- #
def clean_text(text: str) -> str:
    """
    Cleans the text by removing unnecessary whitespace and non-alphanumeric characters.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text.
    """
    # Removing leading/trailing spaces and multiple spaces
    text = " ".join(text.split())

    # You can add more cleaning steps like removing special characters, etc.
    return text

import requests
from bs4 import BeautifulSoup
import re

def search_paper_by_url(url: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1', {'class': 'paper-title'}).get_text(strip=True) if soup.find('h1', {'class': 'paper-title'}) else 'No Title Found'
        authors = [author.get_text(strip=True) for author in soup.find_all('a', {'class': 'author-name'})]
        abstract_tag = soup.find("meta", {"name": "description"}) or soup.find("div", {"class": "abstract"})
        abstract = (
            abstract_tag.get("content") if abstract_tag and "content" in abstract_tag.attrs
            else abstract_tag.get_text() if abstract_tag else soup.get_text()
        )
        abstract = re.sub(r'\s+', ' ', abstract).strip()

        return {
            'title': title,
            'url': url,
            'authors': authors,
            'abstract': abstract
        }

    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return {}
    except Exception as e:
        print(f"Error extracting information from {url}: {e}")
        return {}

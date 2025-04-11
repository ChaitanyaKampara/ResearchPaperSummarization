import fitz  # PyMuPDF
from pathlib import Path
from PyPDF2 import PdfReader
from utils.helpers import extract_from_doi, extract_from_url

def process_paper(file_path: str = None, url: str = None, doi: str = None) -> dict:
    """
    Process the research paper based on the provided input (file, URL, or DOI).

    :param file_path: Path to the uploaded file (PDF or TXT).
    :param url: URL of the research paper to scrape.
    :param doi: DOI of the research paper to extract information.
    :return: A dictionary containing the paper ID and its extracted content.
    """
    if file_path:
        return process_file(file_path)
    elif doi:
        return extract_from_doi(doi)
    elif url:
        return extract_from_url(url)
    else:
        raise ValueError("No valid input provided. Provide either a file path, DOI, or URL.")

def process_file(file_path: str) -> dict:
    """
    Process the uploaded file based on its extension (PDF or TXT).

    :param file_path: Path to the file to process.
    :return: A dictionary containing the file ID and extracted content.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file type. Only .pdf and .txt are supported.")

    return {"id": file_path, "content": text}

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF or PyPDF2.
    """
    text = ""

    # Option 1: Using PyMuPDF (fitz)
    try:
        with fitz.open(file_path) as doc:
            text = " ".join([page.get_text() for page in doc])
    except Exception as e:
        print(f"❌ Error extracting text with PyMuPDF: {e}")

    # Option 2: Fallback to PyPDF2
    if not text:
        try:
            with open(file_path, "rb") as file:
                pdf = PdfReader(file)
                text = "".join([page.extract_text() or "" for page in pdf.pages])
        except Exception as e:
            print(f"❌ Error extracting text with PyPDF2: {e}")

    if not text:
        raise ValueError("Failed to extract text from PDF file.")

    return text

def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from a TXT file.

    :param file_path: Path to the TXT file.
    :return: Text extracted from the TXT file.
    """
    try:
        return Path(file_path).read_text()
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        raise ValueError("Failed to read text from TXT file.")

# Example functions for extracting from DOI and URL (implement these in your helpers)

def c(doi: str) -> dict:
    """
    Extract paper information using a DOI.

    :param doi: The DOI of the research paper.
    :return: A dictionary containing the paper's content extracted from the DOI.
    """
    # Implement the DOI extraction logic here, typically using an API or database lookup
    pass

import requests
from bs4 import BeautifulSoup

def extract_from_url(url: str) -> dict:
    """
    Extract paper information from a URL by scraping academic websites.

    :param url: The URL of the research paper to scrape.
    :return: A dictionary containing the paper's title, abstract, authors, and publication year.
    """
    # Make a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise ValueError(f"Failed to retrieve page. Status code: {response.status_code}")
    
    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example extraction from an academic site (e.g., Semantic Scholar, arXiv)
    
    # Extract the title of the paper
    title_tag = soup.find('h1', class_='title')  # Modify based on the website's HTML structure
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"
    
    # Extract the abstract of the paper
    abstract_tag = soup.find('blockquote', class_='abstract')  # Modify as needed
    abstract = abstract_tag.get_text(strip=True) if abstract_tag else "Abstract not found"
    
    # Extract authors of the paper
    authors_tag = soup.find_all('a', class_='author')  # Modify as needed
    authors = [author.get_text(strip=True) for author in authors_tag] if authors_tag else ["Authors not found"]
    
    # Extract publication year
    year_tag = soup.find('span', class_='year')  # Modify as needed
    publication_year = year_tag.get_text(strip=True) if year_tag else "Year not found"
    
    # Return the extracted information as a dictionary
    return {
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "publication_year": publication_year,
    }



import re
import requests
from PyPDF2 import PdfReader
from urllib.parse import urlparse

def extract_metadata_from_pdf(file_path: str) -> dict:
    try:
        reader = PdfReader(file_path)
        info = reader.metadata or {}

        title = info.title or "Untitled"
        author = info.author or "Unknown Author"
        year = info.get('/CreationDate', 'n.d.')[2:6] if info.get('/CreationDate') else "n.d."
        source = file_path.split("/")[-1] or file_path.split("\\")[-1]

        return {
            "title": title.strip(),
            "author": author.strip(),
            "year": year,
            "source": source
        }
    except Exception as e:
        return {
            "title": "Untitled",
            "author": "Unknown Author",
            "year": "n.d.",
            "source": file_path
        }

def extract_metadata_from_doi(doi: str) -> dict:
    try:
        url = f"https://api.crossref.org/works/{doi}"
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception("DOI not found")

        data = res.json()["message"]
        author_data = data.get("author", [])
        author_names = [f"{a.get('family', '')}, {a.get('given', '')}" for a in author_data]
        authors = ", ".join(author_names) if author_names else "Unknown Author"
        title = data.get("title", ["Untitled"])[0]
        year = data.get("created", {}).get("date-parts", [[None]])[0][0] or "n.d."
        source = data.get("URL", "CrossRef")

        return {
            "title": title,
            "author": authors,
            "year": year,
            "source": source
        }
    except Exception as e:
        return {
            "title": "Untitled",
            "author": "Unknown Author",
            "year": "n.d.",
            "source": doi
        }

def extract_metadata_from_url(url: str) -> dict:
    try:
        # Fallback just using domain
        parsed = urlparse(url)
        domain = parsed.netloc

        return {
            "title": "Untitled from Web",
            "author": "Unknown Author",
            "year": "n.d.",
            "source": domain
        }
    except Exception as e:
        return {
            "title": "Untitled",
            "author": "Unknown Author",
            "year": "n.d.",
            "source": url
        }

def extract_metadata_from_text(text: str) -> dict:
    # Very basic fallback
    title = text.strip().split('\n')[0][:100] if text else "Untitled"
    return {
        "title": title,
        "author": "Unknown Author",
        "year": "n.d.",
        "source": "User-provided text"
    }

def generate_citation(source: str, source_type: str) -> str:
    if source_type == "pdf":
        meta = extract_metadata_from_pdf(source)
    elif source_type == "doi":
        meta = extract_metadata_from_doi(source)
    elif source_type == "url":
        meta = extract_metadata_from_url(source)
    elif source_type == "text":
        meta = extract_metadata_from_text(source)
    else:
        return "Invalid source type for citation."

    citation = f"{meta['author']}. ({meta['year']}). *{meta['title']}*. Retrieved from {meta['source']}."
    return citation

import requests
from bs4 import BeautifulSoup
import re
def search_paper(query: str, max_results: int = 5, sort_by: str = 'relevance', date_filter: str = 'year') -> list:
    """
    Search for academic papers based on a query string from the Semantic Scholar API or other repositories.
    
    :param query: The search query string (e.g., paper topic or keywords).
    :param max_results: The maximum number of results to return (default is 5).
    :param sort_by: Sort results by 'relevance' or 'date' (default is 'relevance').
    :param date_filter: Filter results based on 'year' or 'month' (default is 'year').
    :return: A list of dictionaries containing paper information such as title, URL, and year.
    """
    
    # Prepare the Semantic Scholar search URL with sorting and filtering
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': max_results,
        'sort': sort_by,
        'filter': f"published:{date_filter}",  # Example filter for papers published in the last year
    }
    
    try:
        # Send the request to the API endpoint
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response JSON data
        data = response.json()
        
        # Extract paper details from the JSON response
        papers = []
        for paper in data.get('data', []):
            paper_info = {
                "title": paper.get('title', 'No Title Available'),
                "url": f"https://www.semanticscholar.org/paper/{paper.get('paperId')}",
                "year": paper.get('year', 'Unknown Year'),
                "authors": [author.get('name') for author in paper.get('authors', [])],
                "abstract": paper.get('abstract', 'No abstract available'),
            }
            papers.append(paper_info)
        
        return papers
    
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return []
    
import requests

def search_semantic_scholar(query: str, sort_by: str = "relevance", limit: int = 10):
    """
    Searches research articles on Semantic Scholar based on the given query.

    :param query: The search term (topic, title, author, etc.).
    :param sort_by: Sorting method ('relevance' or 'recency').
    :param limit: Number of articles to return.
    :return: List of article metadata.
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {"Accept": "application/json"}

    sort_mapping = {
        "relevance": "relevance",
        "recency": "pubDate"
    }

    sort_param = sort_mapping.get(sort_by.lower(), "relevance")

    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,abstract,year,venue,url",
        "offset": 0,
        "sort": sort_param
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for paper in data.get("data", []):
            results.append({
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "authors": [author["name"] for author in paper.get("authors", [])],
                "year": paper.get("year"),
                "venue": paper.get("venue"),
                "url": paper.get("url")
            })

        return results

    except Exception as e:
        raise RuntimeError(f"Semantic Scholar search failed: {e}")
    
import feedparser

import requests
from urllib.parse import urlencode

import feedparser

def search_arxiv(query: str, limit: int = 10, sort_by: str = "relevance"):
    base_url = "http://export.arxiv.org/api/query"
    
    params = {
        "search_query": query,
        "start": 0,
        "max_results": limit,
        "sortBy": sort_by,
        "sortOrder": "descending"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # Parse the XML response
        feed = feedparser.parse(response.text)
        results = []
        for entry in feed.entries:
            results.append({
                "title": entry.title,
                "abstract": entry.summary,
                "authors": [author.name for author in entry.authors],
                "publication_year": entry.published.split('-')[0],
                "venue": "arXiv",
                "url": entry.link
            })
        return results

    except requests.RequestException as e:
        raise RuntimeError(f"ArXiv search failed: {e}")



import requests
from xml.etree import ElementTree

def search_pubmed(query: str, sort_by: str = "relevance", limit: int = 10):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # Step 1: Search for IDs
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": limit,
        "sort": "relevance" if sort_by == "relevance" else "pub+date",
        "retmode": "json"
    }
    response = requests.get(search_url, params=search_params)
    response.raise_for_status()
    ids = response.json().get("esearchresult", {}).get("idlist", [])

    # Step 2: Fetch article metadata
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml"
    }
    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_response.raise_for_status()

    root = ElementTree.fromstring(fetch_response.content)
    results = []

    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle", default="No title")
        abstract = article.findtext(".//Abstract/AbstractText", default="No abstract")
        authors = [f"{a.findtext('ForeName')} {a.findtext('LastName')}" 
                   for a in article.findall(".//Author") if a.find("LastName") is not None]
        journal = article.findtext(".//Journal/Title", default="Unknown Journal")
        results.append({
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal
        })

    return results

import requests

import requests

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    # Flatten and sort by word position
    word_positions = [(pos, word) for word, positions in inverted_index.items() for pos in positions]
    word_positions.sort()
    return " ".join(word for _, word in word_positions)

def search_openalex(query: str, sort_by: str = "relevance", limit: int = 10):
    base_url = "https://api.openalex.org/works"
    sort_param = "relevance_score:desc" if sort_by == "relevance" else "publication_date:desc"

    params = {
        "search": query,
        "per-page": limit,
        "sort": sort_param
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for work in data.get("results", []):
            abstract_text = reconstruct_abstract(work.get("abstract_inverted_index"))
            authors = [auth.get("author", {}).get("display_name", "Unknown") for auth in work.get("authorships", [])]
            results.append({
                "title": work.get("title", "No title"),
                "abstract": abstract_text,
                "authors": authors,
                "publication_year": work.get("publication_year", "Unknown"),
                "venue": work.get("host_venue", {}).get("display_name", "Unknown"),
                "url": work.get("id", "")
            })

        return results

    except Exception as e:
        raise RuntimeError(f"OpenAlex search failed: {e}")



    
def search_articles(source: str, query: str, sort_by: str = "relevance", limit: int = 10):
    if source == "semanticscholar":
        return search_semantic_scholar(query, sort_by, limit)
    elif source == "arxiv":
        return search_arxiv(query, limit, sort_by)
    elif source == "pubmed":
        return search_pubmed(query, sort_by, limit)
    elif source == "openalex":
        return search_openalex(query, sort_by, limit)
    else:
        raise ValueError("Source not supported.")


def search_paper_by_url(url: str) -> dict:
    """
    Search for an academic paper from its URL on Semantic Scholar or another site, and extract paper details.
    
    :param url: The URL of the paper (e.g., from Semantic Scholar or other repositories).
    :return: A dictionary containing the paper's title, URL, authors, and abstract.
    """
    
    try:
        # Make a request to the paper's URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Use BeautifulSoup to parse the page content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Example: Extract title, authors, and abstract (Semantic Scholar's HTML structure may differ)
        title = soup.find('h1', {'class': 'paper-title'}).get_text(strip=True) if soup.find('h1', {'class': 'paper-title'}) else 'No Title Found'
        authors = [author.get_text(strip=True) for author in soup.find_all('a', {'class': 'author-name'})]
        abstract = soup.find("meta", {"name": "description"}) or soup.find("div", {"class": "abstract"})
        text = abstract.get("content") if abstract and "content" in abstract.attrs else abstract.get_text() if abstract else soup.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        return {
            'title': title,
            'url': url,
            'authors': authors,
            'abstract': text
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
        return {}
    except Exception as e:
        print(f"Error extracting information from {url}: {e}")
        return {}
    
   
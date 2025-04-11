from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import tempfile
import fitz  # PyMuPDF
import httpx
import time
import shutil
import os
import requests
import re
from bs4 import BeautifulSoup
from utils.helpers import search_paper_by_url
from agents.cross_paper_synthesis import cross_paper_synthesis

# Import agents
from agents.classify_agent import classify_content
from agents.summarize_agent import summarize
from agents.process_agent import extract_text_from_pdf ,extract_from_url,extract_from_doi,extract_text_from_txt
from agents.audio_agent import generate_audio
from agents.citation_agent import generate_citation
from agents.search_agent import (
    search_semantic_scholar,
    search_arxiv,
    search_pubmed,
    search_openalex,
    search_articles
)
from agents.cross_paper_synthesis import cross_paper_synthesis

# FastAPI instance
app = FastAPI(title="🔍 Multi-Source Research Article Search")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories for file handling
UPLOAD_DIR = Path("uploads")
SUMMARY_DIR = Path("summaries")
AUDIO_DIR = Path("audio")
for directory in [UPLOAD_DIR, SUMMARY_DIR, AUDIO_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Mount audio for public access
app.mount("/audio", StaticFiles(directory="audio"), name="audio")


# ----------------------------- MODELS -----------------------------

class SearchRequest(BaseModel):
    query: str
    source: str
    sort_by: Optional[str] = "relevance"
    limit: Optional[int] = 10

class URLRequest(BaseModel):
    url: str

class DOIRequest(BaseModel):
    doi: str


# ----------------------------- ROUTES -----------------------------

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Source Research Article Search API"}


@app.post("/synthesize-papers/")
async def synthesize_papers(files: List[UploadFile] = File(...)):
    saved_paths = []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(file_path)

    synthesis_result = cross_paper_synthesis(saved_paths)
    return {"synthesis": synthesis_result}


@app.get("/search-articles")
async def search_research_articles(
    source: str = Query(...),
    query: str = Query(...),
    sort_by: str = Query("relevance"),
    limit: int = Query(10)
):
    try:
        results = search_articles(source, query, sort_by, limit)
        return {
            "source": source,
            "query": query,
            "sort_by": sort_by,
            "limit": limit,
            "results": results
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")



@app.post("/process-url")
async def process_from_url(request: URLRequest):
    url = request.url.strip()
    print("🔗 Received URL:", url)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=20, allow_redirects=True, verify=True)

        if response.status_code >= 400:
            return {"text": f"❌ Failed to fetch content. HTTP {response.status_code}"}

        if "text/html" not in response.headers.get("Content-Type", ""):
            return {"text": "⚠️ URL does not point to an HTML page."}

        soup = BeautifulSoup(response.content, 'html.parser')

        full_text_div = soup.find("div", class_="papercontent")
        if full_text_div:
            content = full_text_div.get_text(separator=" ", strip=True)
        else:
            meta = soup.find("meta", attrs={"name": "description"})
            abstract_div = soup.find("div", class_=re.compile("abstract", re.IGNORECASE))
            paragraphs = soup.find_all("p")

            content_parts = []
            if meta and meta.get("content"):
                content_parts.append(meta.get("content"))
            if abstract_div:
                content_parts.append(abstract_div.get_text(separator=" ", strip=True))
            if paragraphs:
                content_parts.append(" ".join(p.get_text(strip=True) for p in paragraphs[:5]))

            content = " ".join(content_parts)

        clean_text = re.sub(r'\s+', ' ', content).strip()
        if not clean_text:
            return {"text": "ℹ️ No useful content found on this page."}

        # 🔍 Agents work
        category = classify_content(clean_text)
        summary = summarize(clean_text)
        audio_url = generate_audio(summary)
        citation = generate_citation(url, source_type="url")  # ✅ only one argument

        return {
            "text": clean_text,
            "category": category,
            "summary": summary,
            "audio_url": audio_url,
            "citation": citation
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"text": f"⚠️ Error occurred while processing: {str(e)}"}


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    start_time = time.time()

    try:
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(await file.read())
        temp_file.close()

        pdf_path = Path(temp_file.name)
        print(f"📄 PDF saved at {pdf_path}")

        # Extract text
        print("📖 Extracting text from PDF...")
        extracted_text = extract_text_from_pdf(str(pdf_path))

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="❌ Could not extract text from the PDF.")

        # Run your agents
        print("🏷 Classifying...")
        classification = classify_content(extracted_text)

        print("📝 Summarizing...")
        summary = summarize(extracted_text)

        print("📚 Generating citation...")
        citation = generate_citation(pdf_path, source_type="pdf")

        print("🎧 Generating audio...")
        audio_path = generate_audio(summary, f"{file.filename}_summary.mp3")
        if audio_path is None:
            raise HTTPException(status_code=500, detail="❌ Audio generation failed.")

        elapsed = round(time.time() - start_time, 2)

        return {
            "classification": classification,
            "summary": summary,
            "citations": citation,
            "audio_file": audio_path.name,
            "message": f"✅ PDF processed successfully in {elapsed} seconds!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {e}")
@app.post("/process-doi")
async def process_doi(request: DOIRequest):
    doi = request.doi.strip()
    crossref_url = f"https://api.crossref.org/works/{doi}"

    try:
        response = requests.get(crossref_url, timeout=15)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="DOI not found or inaccessible.")

        data = response.json()["message"]

        # Extract raw abstract or fallback content
        abstract = data.get("abstract")
        if abstract:
            clean_text = re.sub(r'<.*?>', '', abstract).strip()
        else:
            url = data.get("URL", "")
            if not url:
                raise HTTPException(status_code=404, detail="No URL found in DOI metadata.")
            clean_text = fetch_abstract_from_url(url)
            if not clean_text:
                raise HTTPException(status_code=404, detail="Could not extract abstract or content.")

        # Run agents
        category = classify_content(clean_text)
        summary = summarize(clean_text)
        audio_url = generate_audio(summary)
        citation = generate_citation(source=doi, source_type="doi")  # for DOIs

        return {
            "text": clean_text,
            "category": category,
            "summary": summary,
            "audio_url": audio_url,
            "citation": citation
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
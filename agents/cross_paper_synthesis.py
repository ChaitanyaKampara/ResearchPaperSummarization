import os
import time
from typing import List
from PyPDF2 import PdfReader
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor, as_completed

# Use a faster model or keep Pegasus
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Or use "google/pegasus-xsum"

def clean_text(text: str) -> str:
    lines = text.splitlines()
    clean_lines = [line.strip() for line in lines if len(line.strip()) > 30]
    return " ".join(clean_lines)

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return clean_text(text)
    except Exception as e:
        print(f"❌ Failed to extract text from {pdf_path}: {e}")
        return ""

def chunk_text(text: str, max_words: int = 200) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def summarize_single_chunk(i: int, chunk: str) -> str:
    try:
        if len(chunk.split()) < 50:
            print(f"⚠️ Chunk {i+1} too short, skipping.")
            return ""
        summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
        print(f"✅ Chunk {i+1} summarized.")
        return summary
    except Exception as e:
        print(f"⚠️ Error summarizing chunk {i+1}: {e}")
        return ""

def summarize_chunks_parallel(chunks: List[str], max_workers: int = 6) -> List[str]:
    summaries = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {executor.submit(summarize_single_chunk, i, chunk): i for i, chunk in enumerate(chunks)}
        for future in as_completed(future_to_index):
            summary = future.result()
            if summary:
                summaries.append(summary)
    return summaries

def summarize_pdf(pdf_path: str) -> str:
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"⚠️ No extractable text in {pdf_path}")
        return ""
    chunks = chunk_text(text)
    summaries = summarize_chunks_parallel(chunks)
    return " ".join(summaries)

def cross_paper_synthesis(pdf_paths: List[str]) -> str:
    start_time = time.time()
    all_summaries = []

    for i, path in enumerate(pdf_paths):
        print(f"\n📄 Processing {os.path.basename(path)} ({i+1}/{len(pdf_paths)})...")
        summary = summarize_pdf(path)
        if summary:
            all_summaries.append(f"Summary of {os.path.basename(path)}:\n{summary}")
        else:
            print(f"⚠️ Skipping {os.path.basename(path)} due to empty summary.")

    if not all_summaries:
        return "❌ No valid summaries were generated."

    combined_input = "\n\n".join(all_summaries)[:3000]
    final_prompt = (
        "Here are summaries of different research papers. "
        "Please synthesize the key insights, compare common themes, highlight unique contributions, "
        "and provide an overall cohesive understanding of the papers:\n\n"
        + combined_input
    )

    try:
        result = summarizer(final_prompt, max_length=250, min_length=100, do_sample=False)[0]['summary_text']
        elapsed = round(time.time() - start_time, 2)
        return f"🧠 Cross-Paper Synthesis (completed in {elapsed}s):\n\n{result}"
    except Exception as e:
        return f"❌ Final synthesis failed: {e}"

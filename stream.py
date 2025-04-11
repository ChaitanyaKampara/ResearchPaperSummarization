import streamlit as st
import requests
import os

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="📚 Multi-Source Research Tool", layout="wide")

st.title("🔍 Multi-Source Research Article Search")
st.markdown("Search, summarize, cite, and generate audio for research articles.")


# ------------------------- SEARCH SECTION -------------------------
with st.expander("🔎 Search Research Articles"):
    st.subheader("Search Articles")
    query = st.text_input("Enter query:")
    source = st.selectbox("Select source", ["arxiv", "pubmed", "semantic_scholar", "openalex"])
    sort_by = st.selectbox("Sort by", ["relevance", "date"])
    limit = st.slider("Number of results", 1, 25, 10)

    if st.button("Search"):
        params = {
            "query": query,
            "source": source,
            "sort_by": sort_by,
            "limit": limit
        }
        with st.spinner("Searching..."):
            resp = requests.get(f"{API_BASE}/search-articles", params=params)
            if resp.status_code == 200:
                results = resp.json()["results"]
                for idx, res in enumerate(results):
                    st.markdown(f"**{idx+1}. {res.get('title', 'No Title')}**")
                    st.write(res.get("abstract", ""))
                    if "url" in res:
                        st.markdown(f"[🔗 Read more]({res['url']})")
                    st.markdown("---")
            else:
                st.error(f"Error: {resp.json().get('detail')}")


# ------------------------ URL PROCESSING -------------------------
with st.expander("🌐 Process Paper from URL"):
    st.subheader("Process from URL")
    url = st.text_input("Enter research paper URL:")

    if st.button("Process URL"):
        with st.spinner("Processing URL..."):
            res = requests.post(f"{API_BASE}/process-url", json={"url": url})
            if res.status_code == 200:
                data = res.json()
                st.write("### ✏️ Category", data["category"])
                st.write("### 📝 Summary", data["summary"])
                st.write("### 📜 Citation", data["citation"])
                st.audio(f"{API_BASE}/{data['audio_url']}", format="audio/mp3")
            else:
                st.error(f"Failed: {res.json().get('detail')}")


# ------------------------ DOI PROCESSING -------------------------
with st.expander("📘 Process Paper from DOI"):
    st.subheader("Process from DOI")
    doi = st.text_input("Enter DOI")

    if st.button("Process DOI"):
        with st.spinner("Processing DOI..."):
            res = requests.post(f"{API_BASE}/process-doi", json={"doi": doi})
            if res.status_code == 200:
                data = res.json()
                st.write("### ✏️ Category", data["category"])
                st.write("### 📝 Summary", data["summary"])
                st.write("### 📜 Citation", data["citation"])
                st.audio(f"{API_BASE}/{data['audio_url']}", format="audio/mp3")
            else:
                st.error(f"Failed: {res.json().get('detail')}")


# ------------------------ PDF PROCESSING -------------------------
with st.expander("📄 Upload PDF"):
    st.subheader("Upload a research paper PDF")

    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file and st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            files = {"file": (pdf_file.name, pdf_file, "application/pdf")}
            res = requests.post(f"{API_BASE}/upload-pdf/", files=files)
            if res.status_code == 200:
                data = res.json()
                st.write("### ✏️ Classification", data["classification"])
                st.write("### 📝 Summary", data["summary"])
                st.write("### 📜 Citation", data["citations"])
                st.audio(f"{API_BASE}/audio/{data['audio_file']}", format="audio/mp3")
            else:
                st.error(f"Error: {res.json().get('detail')}")


# ------------------------ SYNTHESIZE MULTIPLE PDFs -------------------------
with st.expander("🔗 Synthesize Multiple Papers"):
    st.subheader("Upload multiple PDFs for synthesis")
    pdf_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

    if pdf_files and st.button("Synthesize Papers"):
        with st.spinner("Synthesizing..."):
            files = [("files", (file.name, file, "application/pdf")) for file in pdf_files]
            res = requests.post(f"{API_BASE}/synthesize-papers/", files=files)
            if res.status_code == 200:
                st.write("### 🧠 Synthesis")
                st.write(res.json()["synthesis"])
            else:
                st.error(f"Error: {res.json().get('detail')}")

import streamlit as st
import requests

FASTAPI_BASE_URL = "http://127.0.0.1:8000"  # Update if deployed elsewhere

st.set_page_config(page_title="Research Paper Assistant", layout="wide")
st.title("📚 Multi-Agent Research Paper Assistant")

# ---------------------------- Section 1: Process a Single Paper (URL or PDF) ---------------------------- #
st.header("📄 Process Research Paper")

option = st.radio("Choose Input Method", ("🔗 URL", "📄 PDF Upload"))

if option == "🔗 URL":
    url_input = st.text_input("Enter research paper URL")
    if st.button("Process URL"):
        if url_input:
            with st.spinner("Processing URL..."):
                response = requests.post(f"{FASTAPI_BASE_URL}/process-url", json={"url": url_input})
                if response.status_code == 200:
                    result = response.json()
                    st.success(result["message"])

                    st.subheader("📝 Paper Metadata")
                    st.json(result["paper_metadata"])

                    st.subheader("🧠 Classification")
                    st.json(result["classification"])

                    st.subheader("📋 Summary")
                    st.write(result["summary"])

                    st.subheader("🔍 Synthesized Summary")
                    st.write(result["synthesized_summary"])

                    st.subheader("📚 Citation")
                    st.code(result["citations"])

                    st.subheader("🔊 Audio Summary")
                    st.audio(f"{FASTAPI_BASE_URL}/audio/{result['audio_file']}")
                else:
                    st.error(f"Error: {response.text}")

elif option == "📄 PDF Upload":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file and st.button("Process PDF"):
        with st.spinner("Processing PDF..."):
            response = requests.post(
                f"{FASTAPI_BASE_URL}/upload-pdf/",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            )
            if response.status_code == 200:
                result = response.json()
                st.success(result["message"])

                st.subheader("🧠 Classification")
                st.json(result["classification"])

                st.subheader("📋 Summary")
                st.write(result["summary"])

                st.subheader("🔍 Synthesized Summary")
                st.write(result["synthesized_summary"])

                st.subheader("📚 Citation")
                st.code(result["citations"])

                st.subheader("🔊 Audio Summary")
                st.audio(f"{FASTAPI_BASE_URL}/audio/{result['audio_file']}")
            else:
                st.error(f"Error: {response.text}")

# ---------------------------- Section 2: Cross-Paper Synthesis ---------------------------- #
st.markdown("---")
st.header("🧠 Cross-Paper Synthesis")

multi_files = st.file_uploader("Upload multiple PDFs for synthesis", type=["pdf"], accept_multiple_files=True)

if multi_files and st.button("Synthesize Papers"):
    with st.spinner("Synthesizing across papers..."):
        try:
            files = [("files", (file.name, file.getvalue(), "application/pdf")) for file in multi_files]
            response = requests.post(f"{FASTAPI_BASE_URL}/synthesize-papers/", files=files)

            if response.status_code == 200:
                synthesis_result = response.json()
                st.success("✅ Synthesis complete!")
                st.subheader("📘 Synthesized Knowledge")
                st.write(synthesis_result["synthesis"])
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to synthesize papers: {e}")

# ---------------------------- Section 3: Search Research Articles ---------------------------- #
st.markdown("---")
st.header("🔍 Search Research Articles")

available_sources = ["arxiv", "pubmed", "openalex"]
sort_options = ["relevance", "recency"]

source = st.selectbox("Select Data Source", available_sources)
query = st.text_input("Enter Search Query")
sort_by = st.selectbox("Sort By", sort_options)
limit = st.slider("Number of Articles", min_value=1, max_value=50, value=10)

if st.button("Search Articles"):
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching..."):
            params = {
                "source": source,
                "query": query,
                "sort_by": sort_by,
                "limit": limit
            }

            try:
                response = requests.get(f"{FASTAPI_BASE_URL}/search-articles", params=params)
                if response.status_code == 200:
                    results = response.json()["results"]

                    if results:
                        st.success(f"🔎 Found {len(results)} articles from {source}")
                        for i, article in enumerate(results, start=1):
                            st.markdown(f"### {i}. {article.get('title', 'No Title')}")
                            if "authors" in article:
                                st.markdown(f"👨‍🔬 **Authors**: {', '.join(article['authors'])}")
                            if "abstract" in article:
                                st.markdown(f"📄 **Abstract**: {article['abstract'][:500]}...")
                            if "url" in article:
                                st.markdown(f"[🔗 View Full Paper]({article['url']})", unsafe_allow_html=True)
                            st.markdown("---")
                    else:
                        st.warning("No articles found for the given query.")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to fetch articles: {e}")

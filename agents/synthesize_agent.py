import logging
from typing import List
from transformers import pipeline

# ---------------- Logging ---------------- #
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ---------------- Constants ---------------- #
MAX_CHUNK_LENGTH = 1000  # Token/character length per chunk

# ---------------- Local Summarizer ---------------- #
# Uses local transformer summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ---------------- Helper: Chunk and Summarize ---------------- #
def summarize_text(text: str, max_chunk_length: int = MAX_CHUNK_LENGTH) -> str:
    """
    Summarize a single long text using chunked approach.
    """
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    summaries = []

    for i, chunk in enumerate(chunks):
        try:
            logger.debug(f"Summarizing chunk {i + 1}/{len(chunks)}")
            result = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
            summaries.append(result[0]["summary_text"])
        except Exception as e:
            logger.error(f"Chunk {i + 1} summarization failed: {str(e)}")
            summaries.append(f"[Error in chunk summarization: {str(e)}]")

    return " ".join(summaries)

# ---------------- Cross-Paper Synthesis ---------------- #
def cross_paper_synthesis(paper_texts: List[str]) -> str:
    """
    Performs cross-paper synthesis by summarizing multiple paper texts into a unified synthesis.
    """
    logger.info(f"Starting synthesis for {len(paper_texts)} papers")
    combined_summary = []

    for idx, paper in enumerate(paper_texts):
        logger.info(f"Summarizing paper {idx + 1}")
        summary = summarize_text(paper)
        combined_summary.append(summary)

    try:
        final_input = " ".join(combined_summary)
        logger.info("Generating final combined synthesis...")
        return summarize_text(final_input)  # Final mega-summary
    except Exception as e:
        logger.error(f"Error in final synthesis: {str(e)}")
        return f"[Error in final synthesis: {str(e)}]"

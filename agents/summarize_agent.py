from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize(text: str, max_chunk_len: int = 1024) -> str:
    chunks = [text[i:i + max_chunk_len] for i in range(0, len(text), max_chunk_len)]
    all_summaries = []

    for i, chunk in enumerate(chunks):
        try:
            result = summarizer(
                chunk,
                max_length=512,   # Increase summary length
                min_length=150,   # Ensure it's not too short
                do_sample=False
            )
            summary_text = result[0]['summary_text']
            all_summaries.append(summary_text)
        except Exception as e:
            print(f"[Summarization Error on chunk {i}] {e}")
            continue

    return " ".join(all_summaries)

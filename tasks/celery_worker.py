from celery import Celery
from agents.search_agent import search_paper
from agents.process_agent import process_paper
from agents.classify_agent import classify_paper
from agents.summarize_agent import summarize
from agents.synthesize_agent import synthesize
from agents.audio_agent import generate_audio
from agents.citation_agent import generate_citation

# Initialize Celery with Redis as the broker
celery = Celery(__name__, broker="redis://localhost:6379/0")

@celery.task
def process_task(topic, file_path, paper_url, doi):
    """
    Process the research paper and generate necessary outputs like summary, synthesis, audio, and citation.
    
    Args:
        topic (str): The topic for classification.
        file_path (str): Path to the uploaded paper.
        paper_url (str): URL of the paper (if available).
        doi (str): DOI of the paper (if available).
    
    Returns:
        dict: Contains summary, synthesis, audio path, and citation.
    """
    try:
        # Step 1: Process the paper (extract content, metadata, etc.)
        paper_data = process_paper(file_path, paper_url, doi)

        # Step 2: Classify the paper based on the provided topic
        paper_data['topic'] = classify_paper(paper_data['content'], topic)

        # Step 3: Summarize the paper's content
        summary = summarize(paper_data['content'])

        # Step 4: Synthesize cross-paper information (based on the topic)
        synthesis = synthesize(topic)

        # Step 5: Convert the summary into an audio file
        audio_path = generate_audio(summary, paper_data['id'])

        # Step 6: Generate the citation for the paper
        citation = generate_citation(paper_data['id'])

        # Return the results as a dictionary
        return {
            "summary": summary,
            "synthesis": synthesis,
            "audio_path": audio_path,
            "citation": citation
        }
    except Exception as e:
        # In case of any error, log and return an error message
        return {"error": str(e)}


from fastapi import APIRouter
from pydantic import BaseModel
from agents.classify_agent import classify_content_with_topics

router = APIRouter()

class ClassificationRequest(BaseModel):
    text: str
    topics: list[str]
    top_k: int = 3

@router.post("/classify-topics")
async def classify_text(request: ClassificationRequest):
    try:
        result = classify_content_with_topics(
            text=request.text,
            topics=request.topics,
            top_k=request.top_k
        )
        return {"classified_topics": result}
    except Exception as e:
        return {"error": f"Topic classification failed: {e}"}
    
# routes/classify.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def classify_topic(text: str, topic_list: list[str]):
    for topic in topic_list:
        if topic.lower() in text.lower():
            return {"classified_topic": topic}
    return {"classified_topic": "Unknown"}


from fastapi import FastAPI

app = FastAPI(
    title="AI Enterprise Chatbot",
    description="Hybrid SQL + RAG chatbot for enterprise document Q&A",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
from openai import OpenAI

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using only the provided document excerpts.

Rules:
- Only use information from the provided excerpts. Do not use outside knowledge.
- If the excerpts don't contain enough information to answer the question, say so clearly instead of guessing.
- Be concise and direct.
- Do not mention "excerpts" or "chunks" in your answer — just answer naturally, as if you already knew this information.
"""


def generate_answer(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return "I couldn't find any relevant information in the uploaded documents to answer that question."

    context = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)

    user_prompt = f"""Document excerpts:
{context}

Question: {question}

Answer the question using only the information above."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()
    logger.info(f"rag_answer_generated question={question!r} chunks_used={len(chunks)}")
    return answer


from openai import OpenAI

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

REFUSAL_MESSAGE = (
    "I couldn't find enough information in the uploaded documents "
    "to answer that."
)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using only the provided document excerpts.

Rules:
- Only use information from the provided document excerpts.
- Every factual claim must be directly supported by the excerpts.
- Never invent names, projects, files, events, dates, numbers, or other details.
- If the excerpts do not contain enough information, reply exactly:
  "I couldn't find enough information in the uploaded documents to answer that."
- Previous user questions are conversation context only. They are never a source of facts.
- Be concise and direct.
- Do not mention "excerpts" or "chunks" in your answer.
"""


def generate_answer(
    question: str,
    chunks: list[dict],
    history: list[dict] | None = None,
) -> str:
    if not chunks:
        return REFUSAL_MESSAGE

    context = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)

    user_prompt = f"""Document excerpts:
{context}

Question: {question}

Answer only from the document excerpts above."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if history:
        user_questions = [
            message["content"]
            for message in history
            if message["role"] == "user"
        ]

        if user_questions:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Previous user questions "
                        "(context only, never a source of facts):\n"
                        + "\n".join(user_questions)
                    ),
                }
            )

    messages.append(
        {"role": "user", "content": user_prompt},
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    logger.info(
        "rag_answer_generated question=%r chunks_used=%d",
        question,
        len(chunks),
    )

    return answer
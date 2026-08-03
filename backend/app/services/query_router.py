from openai import OpenAI

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

CLASSIFY_PROMPT = """You classify user questions into one of two categories:
- "sql" — the question is about structured/tabular data (numbers, counts, comparisons, filtering rows, spreadsheet-style data)
- "document" — the question is about content written in documents (facts, descriptions, explanations, anything from a PDF/Word/text file)

Respond with ONLY the single word "sql" or "document". No explanation.
"""


def classify_question(question: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    result = response.choices[0].message.content.strip().lower()
    logger.info(f"question_classified question={question!r} type={result}")
    return result if result in ("sql", "document") else "document"
    
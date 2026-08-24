from openai import OpenAI

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

CLASSIFY_PROMPT = """You classify user questions into one of two categories:
- "sql" — the question asks for records, rows, people, values, counts, comparisons, filters, or spreadsheet-style data. For example, requests such as "show all rejected users" or "give me information about employees with a certification status" are SQL questions.
- "document" — the question is about content written in documents: facts, explanations, policies, or anything from a PDF, Word, or text file.

Respond with ONLY the single word "sql" or "document". No explanation.
"""

_SQL_SIGNAL_WORDS = (
    "how many", "count", "average", "sum", "total", "maximum", "minimum",
    "highest", "lowest", "compare", "filter", "sort", "greater than",
    "less than",
)

_SQL_LIST_WORDS = (
    "show", "list", "find", "get", "give", "display", "retrieve",
)

_SQL_RECORD_WORDS = (
    "user", "users", "employee", "employees", "record", "records",
    "row", "rows", "customer", "customers", "client", "clients",
    "applicant", "applicants", "certification", "status",
    "application", "applications",
)


def classify_question(question: str, previous_route: str | None = None) -> str:
    lowered = question.lower()

    has_strong_sql_signal = any(
        word in lowered for word in _SQL_SIGNAL_WORDS
    )

    asks_for_records = (
        any(word in lowered for word in _SQL_LIST_WORDS)
        and any(word in lowered for word in _SQL_RECORD_WORDS)
    )

    if has_strong_sql_signal or asks_for_records:
        logger.info(
            "question_classified question=%r type=sql "
            "(structured-data signal) previous_route=%s",
            question,
            previous_route,
        )
        return "sql"

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": CLASSIFY_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )

    result = response.choices[0].message.content.strip().lower()

    logger.info(
        "question_classified question=%r type=%s previous_route=%s",
        question,
        result,
        previous_route,
    )

    return result if result in ("sql", "document") else "document"
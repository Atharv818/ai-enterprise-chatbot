from openai import OpenAI

from app.core.config import settings

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

SYSTEM_PROMPT = """You are a SQL generator for a PostgreSQL database.

Rules you must always follow:
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any other write/DDL statement.
- Only use tables and columns that are explicitly listed in the provided schema. Never invent table or column names.
- For any comparison against text/string values (e.g. status, category, or name fields), always use ILIKE instead of = for case-insensitive matching, since the exact casing of stored data is unknown. For example, use `column ILIKE 'rejected'` instead of `column = 'Rejected'`.
- If the conversation history shows a previous question and its generated SQL, treat the current question as a follow-up on that same filtered result set unless it clearly asks about something entirely different. For example, if the previous query filtered for rejected users and the new question says "these" or "of these" or "from these", carry that same filter forward into the new query rather than ignoring it.
- Return ONLY the raw SQL query. No explanation, no markdown formatting, no code fences, no commentary.
- If the question cannot be answered using the given schema, return exactly: SELECT 'UNSUPPORTED_QUERY' AS error;
"""


def generate_sql(question: str, schema_context: str, history: list[dict] | None = None) -> str:
    user_prompt = f"""Available tables and columns:
{schema_context}

Question: {question}

Write a single PostgreSQL SELECT query that answers this question."""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

    return sql

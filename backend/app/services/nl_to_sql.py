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
- Return ONLY the raw SQL query. No explanation, no markdown formatting, no code fences, no commentary.
- If the question cannot be answered using the given schema, return exactly: SELECT 'UNSUPPORTED_QUERY' AS error;
"""


def generate_sql(question: str, schema_context: str) -> str:
    user_prompt = f"""Available tables and columns:
{schema_context}

Question: {question}

Write a single PostgreSQL SELECT query that answers this question."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    sql = response.choices[0].message.content.strip()

    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

    return sql


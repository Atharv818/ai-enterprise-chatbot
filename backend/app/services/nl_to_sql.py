from openai import OpenAI
from sqlalchemy import text
import logging
from app.core.config import settings
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

CATEGORICAL_COLUMNS = ["group_name", "application", "certification_decision", "department"]


def get_categorical_values(table_names: list[str], db, columns: list[str] | None = None) -> dict[str, dict[str, list[str]]]:
    """Fetch real distinct values per table so the LLM stops guessing spellings."""
    columns = columns or CATEGORICAL_COLUMNS
    result: dict[str, dict[str, list[str]]] = {}
    for table_name in table_names:
        table_values: dict[str, list[str]] = {}
        for col in columns:
            try:
                rows = db.execute(
                    text(f'SELECT DISTINCT "{col}" FROM "{table_name}" WHERE "{col}" IS NOT NULL LIMIT 50')
                )
                vals = [r[0] for r in rows]
                if vals:
                    table_values[col] = vals
            except Exception:
                continue
        if table_values:
            result[table_name] = table_values
    return result

SYSTEM_PROMPT = """You are a SQL generator for a PostgreSQL database.

Rules you must always follow:
- Only generate SELECT statements. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, or any other write/DDL statement.
- Only use tables and columns that are explicitly listed in the provided schema. Never invent table or column names.
- For any comparison against text/string values (e.g. status, category, or name fields), always use ILIKE instead of = for case-insensitive matching, since the exact casing of stored data is unknown. For example, use `column ILIKE 'rejected'` instead of `column = 'Rejected'`.
- If a list of "known values" is provided below for a column, you MUST match the user's wording to the closest value in that list and use that exact value (including underscores, spacing, and punctuation) in the query — never the user's literal phrasing. For example, if the known values include "GxP_Admin" and the user writes "gxp admin", generate `ILIKE 'GxP_Admin'`, not `ILIKE 'gxp admin'`.
- Date-like columns (e.g. last_review) are stored as TEXT, not as a native date/timestamp type, and values may appear as either 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MI:SS'. Never compare these columns with = or ILIKE against a month/year phrase. Instead, always cast the column with ::date and use a half-open range. For a specific month and year, use: column::date >= 'YYYY-MM-01' AND column::date < 'YYYY-(MM+1)-01' (roll over to the next year for December). For a specific exact date, use: column::date = 'YYYY-MM-DD'. Always compute the correct calendar boundaries yourself.
- If the conversation history shows a previous question and its generated SQL, treat the current question as a follow-up on that same filtered result set unless it clearly asks about something entirely different. For example, if the previous query filtered for rejected users and the new question says "these" or "of these" or "from these", carry that same filter forward into the new query rather than ignoring it.
- Return ONLY the raw SQL query. No explanation, no markdown formatting, no code fences, no commentary.
- If the question cannot be answered using the given schema, return exactly: SELECT 'UNSUPPORTED_QUERY' AS error;
"""

def generate_sql(
    question: str,
    schema_context: str,
    table_names: list[str],
    db,
    history: list[dict] | None = None,
) -> str:
    categorical_values = get_categorical_values(table_names, db)

    known_values_block = ""
    if categorical_values:
        known_values_block = "\nKnown values for categorical columns (per table):\n"
        for table_name, cols in categorical_values.items():
            known_values_block += f'Table "{table_name}":\n'
            for col, vals in cols.items():
                known_values_block += f'  - "{col}": {", ".join(str(v) for v in vals)}\n'

    user_prompt = f"""Available tables and columns:
{schema_context}
{known_values_block}
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

    logger.info(f"generated_sql: {sql!r} | question={question!r}")

    return sql
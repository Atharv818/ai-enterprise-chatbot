def format_sql_answer(question: str, columns: list[str], rows: list[dict], total_count: int) -> str:
    """
    Turn raw SQL result counts/rows into a natural-language answer,
    replacing the old templated 'Found N result(s).' output.
    """
    if total_count == 0:
        return (
            "I couldn't find any records matching that. "
            "Double-check the spelling of the group, application, or user ID, "
            "or try rephrasing the question."
        )

    if total_count == 1 and len(columns) == 1:
        column = columns[0]
        value = rows[0][column]
        field_label = column.replace("_", " ")
        return f"The {field_label} is {value}."

    if total_count == 1:
        return "Here's what I found:"

    return f"Here are the {total_count} matching results:"
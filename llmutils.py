import os
import requests
import json
from dotenv import load_dotenv
import re

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def nl_to_sql(user_query, schema):
    """Converts a natural language query to a SQL query using a free OpenRouter model."""
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY not found in .env file."

    # --- SYSTEM PROMPT ---
    prompt = f"""
    You are an expert PostgreSQL assistant. Your task is to convert a user's question into a valid PostgreSQL query based on the provided schema.

    **Database Schema:**
    {schema}
    ---
    **Here is an example of a perfect response:**
    User Question: "Show me the top 5 highest paid employees and their department names"
    SQL Query:
    SELECT e.name, e.salary, d.name AS department_name FROM employees e JOIN departments d ON e.department_id = d.id ORDER BY e.salary DESC LIMIT 5;
    ---
    **Now, your turn:**

    User Question:
    "{user_query}"

    **Instructions:**
    1.  Carefully analyze the user question and the schema to construct the correct query.
    2.  If the question involves similarity (e.g., "like", "similar to"), use the vector column with the placeholder `[EMBEDDING]`.
    3.  **IMPORTANT**: You MUST output ONLY the raw SQL query, ending with a semicolon.
    4.  DO NOT include any explanations, analysis, markdown, or any other text.

    **SQL Query:**
    """

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "openai/gpt-oss-20b:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })
        )
        response.raise_for_status()

        result = response.json()
        raw_response = result['choices'][0]['message']['content'].strip()

        # --- SQL PARSER ---
        match = re.search(r'(SELECT|WITH).*?;', raw_response, re.IGNORECASE | re.DOTALL)

        if match:
            # Extract the first full SQL statement that was found.
            sql_query = match.group(0)
            return sql_query
        else:
            # Fallback for if the model forgets the semicolon.
            match = re.search(r'(SELECT|WITH)\s+.*', raw_response, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0).strip()
            else:
                return f"Error: Could not parse a valid SQL query from the LLM's response. Raw response: '{raw_response}'"

    except requests.exceptions.RequestException as e:
        return f"Error calling OpenRouter API: {e}"

def is_safe_query(query):
    """A simple validation to prevent destructive queries."""
    if query.strip().lower().startswith("error:"):
        return False

    query_lower = query.strip().lower()

    # Ensure it's primarily a SELECT or WITH query for safety
    if not (query_lower.startswith('select') or query_lower.startswith('with')):
        return False

    # A simple check for obviously destructive keywords in the main body
    # This is not a perfect security measure.
    disallowed_keywords = ['drop', 'delete', 'update', 'insert', 'truncate', 'alter', 'grant', 'revoke']
    for keyword in disallowed_keywords:
        if keyword in query_lower.split():
            return False

    return True

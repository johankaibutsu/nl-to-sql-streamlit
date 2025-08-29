import streamlit as st
import pandas as pd
from dbutils import get_schema_representation, execute_query
from llmutils import nl_to_sql, is_safe_query
from sentence_transformers import SentenceTransformer
import numpy as np
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="NL to SQL Search Interface",
    page_icon="🤖",
    layout="wide"
)

# --- Model Loading ---
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_embedding_model()

# --- Main App UI ---
st.title("🗂️ Natural Language Search for Your Database")
st.write("Ask a question about the data, and we'll translate it to SQL, run it, and show you the results.")

# Display schema
schema = get_schema_representation()
with st.expander("View Database Schema"):
    st.code(schema, language='text')

# User input
user_query = st.text_area(
    "Enter your question in plain English:",
    placeholder="e.g., 'Show me the top 5 highest paid employees and their department names' or 'Show me all the orders'"
)

if st.button("🔍 Search"):
    if user_query:
        with st.spinner("Translating your question into SQL..."):
            generated_sql = nl_to_sql(user_query, schema)

            # --- Hybrid Search Logic ---
            # Check if the generated SQL contains the [EMBEDDING] placeholder
            if '[EMBEDDING]' in generated_sql:
                st.info("Performing a hybrid vector search...")
                # Extract the text to be embedded from the original user query
                # This is a simple regex, could be improved with more advanced NLP
                match = re.search(r'(?:like|similar to|related to) an? "([^"]+)"|an? ([^"]+)"', user_query, re.IGNORECASE)
                if match:
                    # Find the first non-None group
                    text_to_embed = next((g for g in match.groups() if g is not None), None)

                    if text_to_embed:
                        st.write(f"Found semantic term: **'{text_to_embed}'**")
                        # Generate the embedding
                        embedding = model.encode(text_to_embed)
                        # Convert to string format for SQL query
                        embedding_str = str(embedding.tolist())
                        # Replace placeholder with the actual embedding vector
                        final_sql = generated_sql.replace("'[EMBEDDING]'", f"'{embedding_str}'")
                    else:
                        st.error("Could not extract the term for vector search. Please rephrase your query like 'products similar to \"smart watch\"'.")
                        final_sql = None
                else:
                    st.error("Could not identify the item for semantic search. Please rephrase your query.")
                    final_sql = None
            else:
                final_sql = generated_sql

        if final_sql:
            st.subheader("Generated SQL Query")
            st.code(final_sql, language='sql')

            # --- Safety Check and Execution ---
            if is_safe_query(final_sql):
                with st.spinner("Executing query..."):
                    results = execute_query(final_sql)
                    st.subheader("Results")
                    if isinstance(results, pd.DataFrame):
                        if results.empty:
                            st.warning("Query executed successfully, but returned no results.")
                        else:
                            st.dataframe(results, use_container_width=True)
                    else:
                        # Display error message from db_utils
                        st.error(results)
            else:
                st.error("Query was blocked as it contained potentially unsafe keywords (e.g., DROP, DELETE, UPDATE). Please rephrase your query to be read-only.")
    else:
        st.warning("Please enter a question.")

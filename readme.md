# Natural Language Search Interface for PostgreSQL

A powerful natural language search interface that converts plain English queries into SQL and executes them against a PostgreSQL database using vector embeddings and LLM-powered query translation.

## 🚀 Features

- **Natural Language to SQL**: Convert plain English queries to SQL using LLM models
- **Hybrid Search**: Combines vector similarity search with traditional SQL queries
- **Vector Embeddings**: Uses pgvector extension for semantic search capabilities
- **SQL Injection Protection**: Validates and sanitizes all generated queries
- **Interactive UI**: Clean Streamlit interface for easy querying
- **Real-time Results**: Instant query execution and result display

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+ (installed locally)
- OpenRouter API key or OpenAI API key (You have to modify the model url in llmutils.py file)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repo-url>
cd <folder-name>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL Database

```bash
# Start PostgreSQL service (varies by OS)
# For macOS with Homebrew:
brew install PostgreSQL
brew services start postgresql
```

### 4. Create Database and Enable Extensions

```sql
-- Connect to PostgreSQL as superuser
psql postgres

-- Create a new user and database
CREATE USER myuser WITH PASSWORD 'mypassword';
CREATE DATABASE nldb OWNER myuser;

-- Connect to the new database
\c nldb;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nldb
DB_USER=myuser
DB_PASSWORD=mypassword

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 6. Initialize Database Schema and Data

```bash
python setupdb.py
```
This script will create the tables, generate fake data using Faker, and compute and store vector embeddings for text fields using sentence-transformers.

## 🚀 Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Demo Flow
1. Show the Streamlit interface.
2. Ask a simple SQL query like: 'How many employees are in each department?'
3. Show the generated SQL and the result table.


https://github.com/user-attachments/assets/9ebdeab7-2694-4ea5-834e-f0cb5631f7ef


## Suggestions for Improving System Effectiveness
### Advanced SQL Validation & Generation:
1. LLM to Structured Output: Instead of generating raw SQL, instruct the LLM to output a JSON object representing the query ({ "select_columns": [...], "table": "...", "joins": [...], "filters": [...] }). The Python code would then safely construct the SQL query from this JSON using a library like pypika, completely eliminating the risk of SQL injection.
2. SQL Parser: Use a library like sqlparse in Python to parse the LLM-generated SQL. This allows to inspect the query's structure, identify its type (SELECT, UPDATE), and enforce stricter rules before execution.
### Smarter Hybrid Search Agent:
LLM-Powered Router: Create a "router" prompt that first analyzes the user's intent. The LLM's first task would be to decide if a vector search is needed, what text to embed, and which column to search against. This is more robust than the simple regex used in the prototype.
- Example Plan: For a query like "Show me orders for products like a smart watch placed in the last month," the agent would generate a plan:
    - VECTOR_SEARCH: Find product.ids for "smart watch" using products.name_embedding.
    - SQL_QUERY: SELECT * FROM orders WHERE product_id IN (<results_from_step_1>) AND order_date > '...';
### Data Visualization:
Instead of just showing a table, detect the type of data returned. If the data contains numbers and categories (e.g., "sales per department"), automatically generate a bar chart using st.bar_chart(). If it has time-series data, use st.line_chart(). This makes the insights much easier to digest.


## 🙏 Acknowledgments

- OpenRouter for LLM API access
- pgvector for PostgreSQL vector extensions
- Streamlit for the web interface framework

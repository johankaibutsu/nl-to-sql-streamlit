import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def get_schema_representation():
    """Generates a string representation of the database schema for the LLM."""
    schema = """
    PostgreSQL Database Schema:

    1. departments (List of company departments)
       - id (SERIAL PRIMARY KEY): Unique department ID
       - name (VARCHAR(100)): Department name (e.g., HR, Engineering)

    2. employees (Employee details)
       - id (SERIAL PRIMARY KEY): Unique identifier for an employee
       - name (VARCHAR(100)): Full name
       - department_id (INT, FK -> departments.id): Employee's department
       - email (VARCHAR(255)): Email address
       - salary (DECIMAL(10,2)): Monthly salary

    3. products (Product catalog)
       - id (SERIAL PRIMARY KEY): Unique product ID
       - name (VARCHAR(100)): Product name
       - price (DECIMAL(10,2)): Price per unit
       - name_embedding (vector(384)): Vector embedding of the product name for semantic search.

    4. orders (Customer orders data)
       - id (SERIAL PRIMARY KEY): Unique order ID
       - customer_name (VARCHAR(100)): Name of the customer
       - employee_id (INT, FK -> employees.id): Employee who handled the order
       - order_total (DECIMAL(10,2)): Total order amount
       - order_date (DATE): Date of order
       - customer_name_embedding (vector(384)): Vector embedding of the customer's name.

    Relationships:
    - employees.department_id references departments.id
    - orders.employee_id references employees.id

    Vector Search:
    - To perform a semantic search on product names, use the L2 distance operator '<->' on the 'name_embedding' column.
    - Example: SELECT name FROM products ORDER BY name_embedding <-> (embedding_vector) LIMIT 5;
    """
    return schema.strip()


def execute_query(query):
    """Executes a SQL query and returns the result as a pandas DataFrame."""
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query(query, conn)
            return df
        except (Exception, psycopg2.Error) as error:
            return f"Error executing query: {error}"
        finally:
            conn.close()
    return "Failed to connect to the database."

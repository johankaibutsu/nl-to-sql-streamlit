import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from faker import Faker
from sentence_transformers import SentenceTransformer
import numpy as np
import random

load_dotenv()

# --- Database Connection ---
try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cur = conn.cursor()
    print("✅ Database connection successful")
except psycopg2.OperationalError as e:
    print(f"❌ Could not connect to the database. Please check your .env settings and ensure PostgreSQL is running. Error: {e}")
    exit()

# --- Embedding Model ---
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded")

# --- Faker for Data Generation ---
fake = Faker()

def create_tables():
    """Creates the database tables."""
    print("Creating tables...")
    commands = [
        """
        DROP TABLE IF EXISTS orders, products, employees, departments CASCADE;
        """,
        """
        CREATE TABLE departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
        """,
        """
        CREATE TABLE employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department_id INT REFERENCES departments(id),
            email VARCHAR(255) UNIQUE NOT NULL,
            salary DECIMAL(10, 2)
        );
        """,
        """
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2),
            name_embedding vector(384)
        );
        """,
        """
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            employee_id INT REFERENCES employees(id),
            order_total DECIMAL(10, 2),
            order_date DATE,
            customer_name_embedding vector(384)
        );
        """
    ]
    for command in commands:
        cur.execute(command)
    conn.commit()
    print("✅ Tables created successfully")

def populate_data():
    """Populates the tables with sample data and embeddings."""
    print("Populating data...")

    # Departments
    departments = [('HR',), ('Engineering',), ('Sales',), ('Marketing',)]
    cur.executemany("INSERT INTO departments (name) VALUES (%s);", departments)

    # Employees
    employees_data = []
    for _ in range(20):
        employees_data.append((fake.name(), random.randint(1, 4), fake.email(), random.uniform(50000, 120000)))
    execute_values(cur, "INSERT INTO employees (name, department_id, email, salary) VALUES %s", employees_data)

    # Products
    products_data = []
    product_names = [
        "Quantum Laptop", "Starlight Phone", "Eco-friendly Water Bottle", "Smart Coffee Mug",
        "Wireless Ergonomic Keyboard", "4K Ultra-HD Monitor", "Noise-Cancelling Headphones",
        "Portable SSD Drive 1TB", "AI-Powered Smart Watch", "Gamer's Mechanical Keyboard"
    ]
    product_embeddings = model.encode(product_names)
    for i, name in enumerate(product_names):
        products_data.append((name, random.uniform(50, 2000), product_embeddings[i].tolist()))
    execute_values(cur, "INSERT INTO products (name, price, name_embedding) VALUES %s", products_data)

    # Orders
    orders_data = []
    customer_names = [fake.name() for _ in range(50)]
    customer_embeddings = model.encode(customer_names)
    for i in range(50):
        orders_data.append((
            customer_names[i],
            random.randint(1, 20),
            random.uniform(20, 5000),
            fake.date_between(start_date='-2y', end_date='today'),
            customer_embeddings[i].tolist()
        ))
    execute_values(cur, "INSERT INTO orders (customer_name, employee_id, order_total, order_date, customer_name_embedding) VALUES %s", orders_data)

    conn.commit()
    print("✅ Data populated successfully")

if __name__ == "__main__":
    create_tables()
    populate_data()
    cur.close()
    conn.close()
    print("🎉 Database setup complete!")

import streamlit as st
import psycopg2  # PostgreSQL connection library
import numpy as np

# Function to query the database
def query_database(query, params=None):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname="postgres", user="postgres", password="Akash@123", host="localhost"
    )
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    return results

# Function to convert natural language query to SQL (you will need to improve this)
def convert_to_sql(query):
    # Simple examples of query conversion to SQL
    if "employees with salary" in query:
        # Example: Query to retrieve employees with salary greater than 5000
        return "SELECT name, salary FROM employees WHERE salary > 5000"
    
    elif "orders from today" in query:
        # Example: Query to retrieve orders placed today
        return "SELECT * FROM orders WHERE order_date = CURRENT_DATE"
    
    elif "products similar to" in query:
        # Example: Vector search for products similar to the given description
        product_description = "Laptop"  # You would dynamically extract this from the query
        
        # Generate vector embedding for the product description (for illustration)
        # In a real-world scenario, you would generate the embedding dynamically using a model
        query_embedding = np.array([0.1, 0.2, 0.3])  # Example vector embedding
        
        # Use pgvector to search for similar products based on vector similarity
        embedding_query = query_embedding.tolist()  # Convert numpy array to list
        embedding_query_str = str(embedding_query).replace('[', '{').replace(']', '}')
        
        return f"""
            SELECT p.id, p.name, p.price
            FROM products p
            JOIN product_embeddings pe ON p.id = pe.product_id
            WHERE pe.embedding <=> {embedding_query_str} < 0.5
        """
    
    # Add more conditions for other types of queries if needed
    else:
        return "SELECT * FROM products"

# Streamlit UI
st.title("Natural Language Search")
user_query = st.text_input("Enter your query")

if st.button("Search"):
    # Convert user query to SQL and validate here
    sql_query = convert_to_sql(user_query)  # Implement this function
    results = query_database(sql_query)
    st.write(results)

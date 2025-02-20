import streamlit as st
import psycopg2  # PostgreSQL connection library
import numpy as np
import openai

# Set your OpenAI API key
openai.api_key = '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'

# Function to query the database
def query_database(query, params=None):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="postgres", user="postgres", password="Akash@123", host="localhost"
        )
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)  # Execute query with params to prevent SQL injection
        else:
            cursor.execute(query)  # Execute the query

        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        return f"Error executing query: {e}"

# Function to generate SQL queries from natural language using GPT (OpenAI)
def convert_to_sql_with_gpt(query):
    try:
        # Prompt for GPT model to convert natural language to SQL
        prompt = f"Convert the following natural language query into a valid SQL query: '{query}'"
        response = openai.Completion.create(
            model="text-davinci-003",  # You can change to any other GPT model
            prompt=prompt,
            max_tokens=100
        )
        sql_query = response['choices'][0]['text'].strip()  # Get SQL query from the model's response
        return sql_query
    except Exception as e:
        return f"Error generating SQL query: {e}"

# Function to generate embeddings using OpenAI's API
def generate_embedding(query):
    try:
        response = openai.Embedding.create(input=query, model="text-embedding-ada-002")
        return response['data'][0]['embedding']  # Return the generated embedding
    except Exception as e:
        return f"Error generating embedding: {e}"

# Function to convert natural language to SQL for hybrid search (vector + SQL)
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
        product_description = query.split("products similar to")[-1].strip()  # Extract product description from query
        
        # Generate vector embedding for the product description using OpenAI
        query_embedding = generate_embedding(product_description)
        
        if isinstance(query_embedding, str):
            return query_embedding  # Return the error message if embedding generation failed
        
        # Use pgvector to search for similar products based on vector similarity
        embedding_query_str = str(query_embedding).replace('[', '{').replace(']', '}')
        
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
    sql_query = convert_to_sql(user_query)  # You can use convert_to_sql_with_gpt if needed
    
    if "Error" in sql_query:
        st.error(sql_query)  # Show error if query generation fails
    else:
        results = query_database(sql_query)
        if isinstance(results, str):
            st.error(results)  # Show error if query execution fails
        else:
            st.write(results)

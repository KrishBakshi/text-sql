import streamlit as st
import os
import sqlite3

import google.generativeai as genai
## Configure Genai Key

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function To Load Google Gemini Model and provide queries as response

def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-2.0-flash')
    response=model.generate_content([prompt[0],question])
    return response.text

## Fucntion To retrieve query from the database

def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cur=conn.cursor()
    cur.execute(sql)
    rows=cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

## Define Your Prompt
prompt = [
    """
    You are an expert at converting English questions into valid SQLite queries!

    The database you are using has a table named `my_table` with the following columns:
    respid, status, 
    D1 - Does your organization produce thought leadership content?,
    D2 - Are you involved in B2B thought leadership services purchasing and/or production decisions?,
    D3_1 (Age),
    D4 - Gender,
    D5 - Industry,
    D6 - Geography,
    D7_1 (Job title),
    D8 - Size of company,
    Reports, Articles, Blogs, Videos, Podcasts, Interactives, Events/Webinars, Other (various content formats),
    plus various other columns about business functions, budget, people involved, research, metrics, business outcomes, challenges, etc.

    Example 1:
    Question: How many survey responses are in the table?
    SQL: SELECT COUNT(*) FROM my_table;

    Example 2:
    Question: Show all records where the respondent's industry is 'Technology'.
    SQL: SELECT * FROM my_table WHERE [D5 - Industry] = "Technology";

    Example 3:
    Question: List all unique job titles.
    SQL: SELECT DISTINCT [D7_1 (Job title)] FROM my_table;

    Example 4:
    Question: What is the average size of companies?
    SQL: SELECT AVG([D8 - Size of company]) FROM my_table;

    Notes:
    - Always use exact column names, including special characters and spaces, inside square brackets `[ ]` if needed.
    - The output must be a single SQL statement only — no ``` or the word `sql` — just the query.
    """
]

def get_natural_language_response(question, sql, result):
    # Compose a prompt for Gemini to answer in natural language
    nl_prompt = f"""
        You are an expert data analyst.
        Given the following SQL query and its result, answer the user's question in clear, concise natural language.

        Question: {question}
        SQL: {sql}
        Result: {result}

        Answer:"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(nl_prompt)
    return response.text.strip()

## Streamlit App

st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

question=st.text_input("Input: ",key="input")

submit=st.button("Ask the question")

# if submit is clicked:
# if submit:
#     response=get_gemini_response(question,prompt)
#     print(response)
#     response=read_sql_query(response,"mydatabase.db")
#     st.subheader("The REsponse is")
#     for row in response:
#         print(row)
#         st.header(row)

if submit:
    response = get_gemini_response(question, prompt)
    print("Gemini raw response:", response)
    sql_lines = [line for line in response.split('\n') if line.strip().lower().startswith(('select', 'update', 'insert', 'delete', 'with'))]
    if not sql_lines:
        st.error("No valid SQL query found in the model response.")
    else:
        sql_query = sql_lines[0]
        print("SQL to execute:", sql_query)
        try:
            result = read_sql_query(sql_query, "mydatabase.db")
            # Convert result to a string for Gemini
            result_str = str(result)
            nl_response = get_natural_language_response(question, sql_query, result_str)
            st.subheader("Answer")
            st.write(nl_response)
        except Exception as e:
            st.error(f"SQL execution error: {e}")








import re
import streamlit as st
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import re

# Configure Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini model
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt, question])
    return response.text

# Execute SQL
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df

# Convert SQL + result to NL answer
def get_natural_language_response(question, sql, result):
    nl_prompt = f"""
    You are an expert data analyst.
    Given the SQL query and its result, answer the user's question in clear, concise natural language.

    Question: {question}
    SQL: {sql}
    Result: {result}

    Answer:"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(nl_prompt)
    return response.text.strip()

# Streamlit UI
st.set_page_config(page_title="Text-to-SQL Chatbot with Plots")
st.title("Text-to-SQL + Demographics Plotter 📊")

st.markdown("""
**Example questions you can ask:**
- *How many survey responses are there?*
- *What is the average age of respondents?*
- *Show the distribution of age.*
- *Plot the gender breakdown.*
- *How many people work in the Technology industry?*
- *List all unique job titles.*
- *Show the average company size by industry.*
""")

question = st.text_input("Ask your question:")
submit = st.button("Run")

if submit:
    prompt = """
    You are an expert at converting plain English questions into valid **SQLite** queries.

    📌 The database has a table named `my_table_clean` with these columns:
    - respid
    - status
    - D1 — Does your organization produce thought leadership content?
    - D2 — Are you involved in B2B thought leadership services purchasing and/or production decisions?
    - age
    - gender
    - industry
    - geography
    - job_title
    - company_size

    ✅ **Rules**
    - Always use exact column names, inside `[ ]` if needed.
    - Return **ONLY the raw SQL query**
    - Do NOT include markdown, and do NOT prepend "SQL:"
    - Always use `my_table_clean` as the table name.
    """

    sql_query = get_gemini_response(question, prompt).strip()
    sql_query = re.sub(r'```[\w]*', '', sql_query).replace('```', '').strip()
    st.info(f"Generated SQL: `{sql_query}`")

    try:
        df = read_sql_query(sql_query, "my_db_clean.db")
        st.dataframe(df)

        # Visualization logic
        lower_q = question.lower()

        if 'plot' in lower_q or 'distribution' in lower_q or 'show age' in lower_q or 'gender' in lower_q:
            fig, ax = plt.subplots()

            if 'age' in lower_q:
                col = [c for c in df.columns if 'age' in c.lower()][0]
                df[col] = pd.to_numeric(df[col], errors='coerce')
                sns.histplot(df[col].dropna(), bins=10, kde=True, ax=ax)
                ax.set_title('Age Distribution')
                ax.set_xlabel('Age')
                ax.set_ylabel('Count')

            elif 'gender' in lower_q:
                # Fix: use grouped query result directly
                labels = df.iloc[:, 0].tolist()
                sizes = df.iloc[:, 1].tolist()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                ax.set_title('Gender Breakdown')
                ax.axis('equal')

            st.pyplot(fig)

        # Natural language summary
        nl_answer = get_natural_language_response(question, sql_query, df.to_string(index=False))
        st.subheader("Answer")
        st.write(nl_answer)

    except Exception as e:
        st.error(f"Error: {e}")

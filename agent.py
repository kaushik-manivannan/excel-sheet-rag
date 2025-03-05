import pandas as pd
import boto3
from langchain_aws import BedrockLLM
import sqlite3
import streamlit as st 
import os

# Streamlit UI
st.title("Excel to SQLite Query using LLM")

# File upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    
    #get title:
    file_name = os.path.splitext(uploaded_file.name)[0]
    title = file_name.replace(" ", "_").title() 

    print("the title is: ", title)
    
    # Read Excel
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(('xlsx', 'xls')) else pd.read_csv(uploaded_file)
    st.write("### Uploaded Data")
    st.dataframe(df)

    
    # Connect to SQLite and save data
    
    conn = sqlite3.connect(title)
    
    cursor = conn.cursor()

    table_name = title

    df.to_sql(title, conn, if_exists="replace", index=False)
    st.write("Data stored in SQLite database successfully!")

    # get column names: 
    cursor.execute(f"PRAGMA table_info({title})")
    schema = cursor.fetchall()
  
    # Query input
    user_query = st.text_input("Enter a query about the dataset:")
    
    if st.button("Run Query") and user_query:
        # Initialize Bedrock LLM
        bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
        llm = BedrockLLM(client=bedrock_client, model_id="amazon.titan-tg1-large")
        

   
        #The output should be formated with the tag <SQL> at the beginning.
        # add tags 
        system_prompt = (
            f"Write a line of SQL query in plain text to query an SQLite database named {title}.\
            The database is already created\
            Just provide the executable code with out extra content\
            The schema of the database is {schema}\
            The query is: '{user_query}'. DO NOT INCLUDE COMMENTS OR ANYTHING THAT IS NOT RELATED TO THE CODE!. Do not include >>>\
            \
            "
            
        )
        
        response = llm.invoke(system_prompt + user_query).strip()
        
        # # Execute the SQL query
        # try:
            
        #     cursor.execute(response)
        #     results = cursor.fetchall()
        #     st.write("### Query Results")
        #     st.write(pd.DataFrame(results))
        # except Exception as e:
        #     st.error(f"Error executing query: {e}")
        
        # conn.close()

        #response = llm.invoke(system_prompt + query ).strip()

        print(response)

        if not response.lower().startswith("select"):
            st.write(f"Error: LLM-generated SQL query is invalid: {response}")
            exit()

        #convert to executable string 
        executable_string = f"cursor.execute('{response}')"

        #execute 
        exec(executable_string)
        result = cursor.fetchall()  # Fetch the result properly
        st.write("### Query Results")


        # system_prompt2 = 

        # response2 = llm.invoke(system_prompt2 + user_query).strip()

        st.write(result)

        # Close the database connection
        conn.close()









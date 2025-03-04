import pandas as pd
import boto3
from langchain_aws import BedrockLLM
import sqlite3



#initalize llm 
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
llm = BedrockLLM(client=bedrock_client, model_id="amazon.titan-tg1-large")

#read excel path
excel_path = 'USAHousingDataset.csv'
df = pd.read_excel(excel_path)
# print(df.info())

#create sql database 
conn = sqlite3.connect('housing_info.db')
cursor = conn.cursor()

#tablename 
table_name = 'housing_info'

#convert pandas df to sql df 
df.to_sql(table_name, conn, if_exists ='replace', index = False)
#print(' df converted to sql successfully ')

# get column names: 
cursor.execute("PRAGMA table_info(housing_info)")
columns = [col[1] for col in cursor.fetchall()]  # Column names are in the second field
#print("Column Names:", columns)


#query and system prompt 
query = input('Please enter a question about the housing data: ') 


# questions
#what year is the greatest number of bedrooms built?
#what is the avg number of bedrooms 

system_prompt = f"Write lines of python code in plain text to query an SQLite database named 'housing_info.db'. The database is already created\
Just provide the executable code with out extra content\
The columns in the database are: {columns}\
The query is: '{query}'. DO NOT INCLUDE COMMENTS OR ANYTHING THAT IS NOT RELATED TO THE CODE!. Do not include >>> Store the final answer in results\
\
"

response = llm.invoke(system_prompt + query ).strip()
#print("Response: ")
#print(response)

if not response.lower().startswith("select"):
    print(f"Error: LLM-generated SQL query is invalid: {response}")
    exit()

#convert to executable string 
executable_string = f"cursor.execute('{response}')"

#execute 
exec(executable_string)
result = cursor.fetchall()  # Fetch the result properly
print("Result:\n", result)

# Close the database connection
conn.close()







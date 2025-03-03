import pandas as pd
import boto3
from langchain_aws import BedrockLLM
from sqlalchemy import create_engine
#import csvtosql as cs

import sqlite3

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
llm = BedrockLLM(client=bedrock_client, model_id="amazon.titan-tg1-large")

excel_path = 'USAHousingDataset.csv'
df = pd.read_excel(excel_path)
print(df.info())


conn = sqlite3.connect('housing_info.db')
cursor = conn.cursor()

table_name = 'housing_info'

df.to_sql(table_name, conn, if_exists ='replace', index = False)
print(' df converted to sql successfully ')

cursor.execute("SELECT * FROM housing_info LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

query = 'how many houses are built in 1979?'

system_prompt = f"Write lines of python code in plain text to query an SQLite database named 'housing_info.db'. The database is already created\
Just provide the executable code with out extra content\
The columns in the database are: ['Price', 'Bedrooms', 'Bathrooms', 'SquareFeet', 'YearBuilt', 'GarageSpaces', 'LotSize', 'ZipCode', 'CrimeRate', 'SchoolRating']\
The query is: '{query}'. DO NOT INCLUDE COMMENTS OR ANYTHING THAT IS NOT RELATED TO THE CODE!. Do not include >>> Store the final answer in results\
\
"


response = llm.invoke(system_prompt + query ).strip()
print("Response: ")
print(response)


executable_string = f"cursor.execute('{response}')"
print("Formatted Executable String:")
print(executable_string)  # Debugging output to verify

exec(executable_string)
result = cursor.fetchone()  # Fetch the result properly
print("Query Result:", result)



# Close the database connection
conn.close()







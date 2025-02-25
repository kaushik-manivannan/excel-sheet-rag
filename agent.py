# agent generates python code that 
# run the generated code 
# store value 
# return vallue 

#


import pandas as pd
import boto3


# Load Excel File into a Pandas DataFrame
excel_path = "Salary.csv"  #file path 
df = pd.read_csv(excel_path)

print(df.head())
print(df.columns)
print(df['Salary'].mean())

# Initialize AWS Bedrock Client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Use Amazon Titan LLM
#llm = BedrockLLM(client=bedrock_client, model_id="amazon.titan-tg1-large")


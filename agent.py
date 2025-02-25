# generates python code that 
# run the generated code 
# store value 
# return vallue 

#

import pandas as pd
import boto3
import json

# Load Excel File into a Pandas DataFrame
excel_path = "USAHousingDataset.csv"  #file path 
df = pd.read_excel(excel_path)

print(df.head())
print(df.columns)
#print(df['Salary'].mean())

# Initialize AWS Bedrock Client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

query = "calculate the average total math score?"

def generate_code(query):
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-tg1-large",  # Ensure this is correct
        body=json.dumps({
            "inputText": f"Write a Python script for: {query}",  # Use inputText instead of prompt for Titan
            "textGenerationConfig": {
                "maxTokenCount": 200,
                "temperature": 0,
            }
       
        }),
    )  
    #load json response 
    response_body = json.loads(response["body"].read().decode("utf-8"))


    return response_body.get("results", [{}])[0].get("outputText", "No code generated")



print("\nQuery Sent to AWS Bedrock:")
print(query)


generated_code = generate_code(query)
print("\nGenerated Python Code:")
print(generated_code)

import pandas as pd
import boto3
from langchain_experimental import agents
from langchain_aws import BedrockLLM
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import warnings 

warnings.filterwarnings("ignore")

excel_path = "school_scores.csv"  # Update with your actual file path
df = pd.read_csv(excel_path)


bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")
llm = BedrockLLM(temperature= 0, client=bedrock_client, model_id="amazon.titan-tg1-large")

# is this an agent executor / does it need to be 
agent_executor = create_csv_agent(llm, excel_path, verbose = True, allow_dangerous_code = True)

print(df.head())

print("The avg total math score is", round(df['Total Math'].mean(),2))
print("The avg year is", df['Year'].mean())

query = "What is average Year? "
agent_executor.run(query)
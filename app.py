
import pandas as pd
import boto3
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_aws import BedrockLLM
from langchain.memory import ConversationBufferMemory

# look into LangGraph?

# Load Excel File into a Pandas DataFrame
excel_path = "Salary.csv"  # Update with your actual file path
df = pd.read_csv(excel_path)

print(df.head())
print(df.columns)
print(df['Salary'].mean())

# Initialize AWS Bedrock Client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Use Amazon Titan LLM
llm = BedrockLLM(client=bedrock_client, model_id="amazon.titan-tg1-large")

# Define a Tool to Query Excel Data
def query_excel(query: str):
    query = "average salary score"
    """Processes a query and returns relevant data from the Excel sheet."""
    if "average salary score" in query.lower():
        print('in if statement')
        avg_math = df['Salary'].mean()
        # Modified: Fixed formatting by removing extra space inside the format specifier.
        return f"The average Salary is: {avg_math:.2f}."
    elif "total number of records" in query.lower():
        return f"The total number of records in the dataset is {len(df)}."
    else:
        return "I can only process limited queries on the dataset."

# Define tools for the agent
tools = [
    Tool(
        name="Excel_Query_Tool",
        func=query_excel,
        description="Use this tool to analyze data from the Excel sheet."
    )
]

# Set up memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize the LangChain Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True
)



# Run the Agent to Query Excel Data
# ----------------------------------------------------------------
# Modified: Added the missing "Action Input:" line in the documentation.
# Action: Excel Query Tool(query="average total math score")
# Action Input: None
# ----------------------------------------------------------------
response = agent.invoke("what is average salary score?")

print(response)


# agent generates python code that 
# run the generated code 
# store value 
# return vallue 
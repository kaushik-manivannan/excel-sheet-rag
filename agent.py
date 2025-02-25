from dotenv import load_dotenv
import os
from langchain.agents import AgentExecutor, AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from tools.search_tools import SearchExcelTool
from tools.calculation_tools import CalculationTool
from tools.visualization_tools import VisualizationTool

# Load environment variables
load_dotenv()

def create_agent_executor(vector_db, excel_file_path, sheets_info):
    """
    Create an agent executor with tools for Excel data analysis.
    """
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    
    # Create tools
    search_tool = SearchExcelTool(vector_db)
    calculation_tool = CalculationTool(excel_file_path)
    visualization_tool = VisualizationTool(excel_file_path)
    
    # Get the structured tools
    tools = [
        Tool(
            name="SearchExcel",
            func=search_tool.search_excel_data,
            description="Useful for searching information in the Excel dataset. Input: a question about the data."
        ),
        calculation_tool.get_tool(),  # Use the structured tool
        Tool(
            name="GenerateChart",
            func=visualization_tool.generate_chart,
            description="Useful for generating charts from Excel data. Input should be a JSON string with keys: 'sheet_name', 'x_column', 'y_column', and optional 'chart_type' ('line', 'bar', 'scatter')."
        )
    ]
    
    # Use a different agent type that works better with structured tools
    from langchain.agents import AgentType, initialize_agent
    
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,  # This agent type works better with structured tools
        verbose=True
    )
    
    return agent_executor
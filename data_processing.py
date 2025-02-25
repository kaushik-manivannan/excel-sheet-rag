from dotenv import load_dotenv
import os
import pandas as pd
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings

# Load environment variables
load_dotenv()

def process_excel_file(file_path):
  """
  Process an Excel file and prepare it for vectorization.
  Returns processed data and sheet information.
  """
  # Load Excel File - all sheets
  excel_data = pd.read_excel(file_path, sheet_name=None)
  
  # Process each sheet
  processed_data = []
  sheets_info = {}
  
  for sheet_name, df in excel_data.items():
    # Store sheet information
    sheets_info[sheet_name] = {
        "columns": list(df.columns),
        "rows": len(df),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    
    # Convert data frame to text chunks for vectorization
    sheet_text = f"Sheet: {sheet_name}\n"
    sheet_text += df.to_string(index=False)
    
    # Add metadata about columns
    sheet_text += f"\nColumns: {', '.join(df.columns)}"
    sheet_text += f"\nNumber of rows: {len(df)}"
    
    # Add sample data for each column to help with understanding
    sheet_text += "\nColumn examples:"
    for col in df.columns:
        sample_values = df[col].dropna().head(3).tolist()
        sample_str = ", ".join([str(val) for val in sample_values])
        sheet_text += f"\n- {col}: {sample_str}"
    
    processed_data.append({
        "content": sheet_text, 
        "metadata": {"sheet": sheet_name}
    })
    
  return processed_data, sheets_info

def create_vector_db(processed_data):
    """
    Create a vector database from processed Excel data.
    """
    # Import necessary modules
    import chromadb
    from chromadb.config import Settings
    from langchain_community.vectorstores import Chroma
    from langchain_openai.embeddings import OpenAIEmbeddings
    import uuid
    import os
    import tempfile
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []
    
    for item in processed_data:
        splits = text_splitter.split_text(item["content"])
        for split in splits:
            documents.append({
                "content": split, 
                "metadata": item["metadata"]
            })
    
    # Create embeddings
    embeddings = OpenAIEmbeddings()
    texts = [doc["content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    # Create a unique directory for this instance
    persist_directory = os.path.join(tempfile.gettempdir(), f"chroma_{uuid.uuid4().hex}")
    os.makedirs(persist_directory, exist_ok=True)
    
    # Create Chroma client with explicit settings
    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create a unique collection
    collection_name = f"collection_{uuid.uuid4().hex}"
    collection = client.create_collection(name=collection_name)
    
    # Create Langchain Chroma wrapper
    vector_db = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings
    )
    
    # Add documents to the collection
    vector_db.add_texts(texts=texts, metadatas=metadatas)
    
    return vector_db
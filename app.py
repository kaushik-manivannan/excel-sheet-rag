import streamlit as st
import os
from data_processing import process_excel_file, create_vector_db
from agent import create_agent_executor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Excel Data Assistant", layout="wide")

# App title and description
st.title("Excel Data Assistant")
st.write("Upload an Excel file and ask questions about your data")

# Initialize session state variables if they don't exist
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "excel_file_path" not in st.session_state:
    st.session_state.excel_file_path = None
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None
if "sheets_info" not in st.session_state:
    st.session_state.sheets_info = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# File uploader in the sidebar
with st.sidebar:
    st.header("Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        excel_file_path = "temp_upload.xlsx"
        with open(excel_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Add a button to process the file
        if st.button("Process Excel File") or not st.session_state.file_processed:
            with st.spinner("Processing Excel file..."):
                try:
                    # Process and create vector DB
                    processed_data, sheets_info = process_excel_file(excel_file_path)
                    vector_db = create_vector_db(processed_data)
                    
                    # Save to session state
                    st.session_state.vector_db = vector_db
                    st.session_state.excel_file_path = excel_file_path
                    st.session_state.sheets_info = sheets_info
                    
                    # Create agent
                    st.session_state.agent_executor = create_agent_executor(
                        vector_db, excel_file_path, sheets_info
                    )
                    
                    st.session_state.file_processed = True
                    st.success("Excel file processed successfully!")
                    
                    # Add a debug message
                    st.write(f"Agent executor created: {st.session_state.agent_executor is not None}")
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
        
        # Display file info
        if st.session_state.sheets_info:
            st.subheader("File Information")
            for sheet, info in st.session_state.sheets_info.items():
                with st.expander(f"Sheet: {sheet}"):
                    st.write(f"Columns: {', '.join(info['columns'])}")
                    st.write(f"Rows: {info['rows']}")

# Main chat interface
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about your Excel data"):
    # Check if an Excel file has been uploaded
    if not st.session_state.agent_executor:
        # Display a more helpful message
        st.warning("Please upload and process an Excel file first before asking questions.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
          with st.spinner("Thinking..."):
            try:
              # Execute the agent without expecting intermediate_steps
              response = st.session_state.agent_executor.invoke({"input": prompt})
              
              # Extract the final output
              final_response = response.get("output", "I couldn't find an answer to your question.")
              
              # Display the final answer
              st.markdown(final_response)
              
              # Add AI response to chat history
              st.session_state.messages.append({"role": "assistant", "content": final_response})
                
            except Exception as e:
              error_message = f"Error generating response: {str(e)}"
              st.error(error_message)
              st.info("I couldn't find that information in the Excel file. Please try a different question or make sure the data is in the uploaded file.")
              
              # Add error message to chat history
              st.session_state.messages.append({"role": "assistant", "content": "I couldn't find that information in the Excel file."})
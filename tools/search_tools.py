import json

class SearchExcelTool:
    """Tool for searching Excel data using vector similarity."""
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
    
    def search_excel_data(self, query):
      """
      Search for information in the Excel dataset based on the query.
      """
      try:
        # Use the vector store to retrieve relevant information
        results = self.vector_db.similarity_search(query, k=3)
        
        if not results:
            return "No relevant information found in the Excel file."
        
        # Format the results in a more readable way
        formatted_results = "Here's what I found in the Excel file:\n\n"
        
        for i, doc in enumerate(results, 1):
            content = doc.page_content
            metadata = doc.metadata
            
            formatted_results += f"From sheet '{metadata['sheet']}':\n{content}\n\n"
        
        return formatted_results
      
      except Exception as e:
          return f"Error searching Excel data: {str(e)}"
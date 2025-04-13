# llm_connector.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiConnector:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_answer(self, query, context):
        """Generate answer using Gemini with context from OneNote"""
        try:
            # Format context
            formatted_context = "\n\n".join([f"Document: {doc['content']}\nSource: {doc['source']}" for doc in context])
            
            # Create prompt
            prompt = f"""You are an AI assistant that answers questions based on the user's OneNote content. 
Answer the following question using ONLY the provided context from OneNote notebooks.
If the answer cannot be found in the provided context, say "I couldn't find information about this in your notes."
Do not make up information that is not in the context.

CONTEXT:
{formatted_context}

QUESTION: {query}

ANSWER:"""
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return f"I encountered an error generating your answer: {str(e)}"
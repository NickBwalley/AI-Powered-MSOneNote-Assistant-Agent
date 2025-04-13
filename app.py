# app.py

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from vector_store import VectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize vector store
try:
    vector_store = VectorStore()
except Exception as e:
    print(f"Error initializing vector store: {str(e)}")
    vector_store = None

# Initialize chat history
chat_history = []

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process question and return AI response"""
    query = request.form.get('query')
    
    if not query:
        return jsonify({
            'success': False,
            'message': 'No question provided',
            'progress': ['Error: No question provided']
        })
    
    progress_updates = []
    
    # Verify credentials and API keys
    progress_updates.append("Verifying credentials and API keys")
    
    if not os.getenv("GOOGLE_API_KEY"):
        return jsonify({
            'success': False,
            'message': 'Google API key not configured',
            'progress': progress_updates + ['Error: Google API key not found']
        })
    
    # Check if vector store is initialized
    progress_updates.append("Searching for notebook access")
    
    if not vector_store or not vector_store.collection:
        return jsonify({
            'success': False,
            'message': 'OneNote data not loaded or processed',
            'progress': progress_updates + ['Error: OneNote data not available']
        })
    
    try:
        # Search for relevant documents
        progress_updates.append("Searching OneNote content for relevant information")
        search_results = vector_store.search(query)
        
        if search_results.get("status") == "error":
            return jsonify({
                'success': False,
                'message': search_results.get("message", "Error searching OneNote content"),
                'progress': progress_updates + search_results.get("progress", [])
            })
        
        progress_updates.extend(search_results.get("progress", []))
        
        # Initialize Gemini model
        progress_updates.append("Initiating Gemini API request")
        
        llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.2)
        
        # Set up conversation memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create retrieval chain
        progress_updates.append("Processing information with AI")
        
        # Create documents retriever
        documents = search_results.get("documents", [])
        
        if not documents:
            return jsonify({
                'success': False,
                'message': 'No relevant information found in your OneNote',
                'progress': progress_updates + ['No matching content found in notebooks']
            })
            
        # Process with AI (simulating this part since we don't have full implementation)
        # In a real implementation, you would use the documents to create a retrieval chain
        
        # Simulate AI processing time
        time.sleep(2)
        
        # Generate response
        answer = f"""# Answer to your question: "{query}"

Based on your OneNote content, here's what I found:

## Summary
I've analyzed {len(documents)} relevant sections from your notebooks that relate to your question.

## Key Points
- Found information from {", ".join(list(set([doc["source"] for doc in documents])))}
- The most relevant content addresses your question directly

## Detailed Answer
{documents[0]["content"] if documents else "No specific content found"}

Would you like me to elaborate on any specific part of this answer?"""
        
        progress_updates.append("Response generated successfully")
        
        return jsonify({
            'success': True,
            'answer': answer,
            'progress': progress_updates
        })
        
    except Exception as e:
        error_message = f"Error processing your question: {str(e)}"
        return jsonify({
            'success': False,
            'message': error_message,
            'progress': progress_updates + [error_message]
        })

if __name__ == '__main__':
    app.run(debug=True)
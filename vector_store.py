# vector_store.py

import os
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self):
        """Initialize the vector store with ChromaDB and Google Generative AI embeddings"""
        try:
            self.vector_db_path = os.getenv("VECTOR_DB_PATH")
            if not self.vector_db_path:
                raise ValueError("VECTOR_DB_PATH environment variable not set")
                
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
                
            # Initialize embeddings
            self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            
            # Initialize ChromaDB
            self.client = chromadb.Client(Settings(
                persist_directory=self.vector_db_path,
                anonymized_telemetry=False
            ))
            
            # Create collection
            self.collection = self.client.get_or_create_collection("onenote_content")
            
        except Exception as e:
            print(f"Error initializing VectorStore: {str(e)}")
            self.collection = None
            raise
    
    def process_documents(self, documents):
        """Process documents and store in vector database"""
        if not documents:
            print("No documents provided for processing")
            return {"status": "error", "message": "No documents provided"}
            
        if not self.collection:
            print("Vector database collection not initialized")
            return {"status": "error", "message": "Vector database not initialized"}
            
        progress_updates = []
        
        # Text splitter for chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        
        progress_updates.append(f"Starting to process {len(documents)} documents")
        
        # Process each document
        processed_count = 0
        for i, doc in enumerate(documents):
            try:
                # Extract content and metadata
                content = doc["content"]
                source = doc["source"]
                
                # Split text into chunks
                chunks = text_splitter.split_text(content)
                
                progress_updates.append(f"Document {i+1}: Split into {len(chunks)} chunks")
                
                # Add each chunk to the collection
                for j, chunk in enumerate(chunks):
                    chunk_id = f"doc_{i}_chunk_{j}"
                    
                    # Generate embedding
                    embedding = self.embeddings.embed_query(chunk)
                    
                    # Add to collection
                    self.collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{"source": source}]
                    )
                
                processed_count += 1
                progress_updates.append(f"Processed document {i+1}/{len(documents)}: {source}")
            
            except Exception as e:
                error_msg = f"Error processing document {i}: {str(e)}"
                print(error_msg)
                progress_updates.append(error_msg)
        
        result = {
            "status": "success" if processed_count > 0 else "error",
            "message": f"Processed {processed_count}/{len(documents)} documents successfully",
            "progress": progress_updates
        }
        
        return result
    
    def search(self, query, n_results=5):
        """Search the vector database for relevant documents"""
        progress_updates = []
        
        try:
            if not self.collection:
                raise ValueError("Vector database collection not initialized")
                
            progress_updates.append("Generating query embedding")
            
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            progress_updates.append(f"Searching collection for top {n_results} results")
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                documents.append({
                    "content": doc,
                    "source": metadata["source"]
                })
            
            progress_updates.append(f"Found {len(documents)} relevant documents")
            
            return {
                "status": "success",
                "documents": documents,
                "progress": progress_updates
            }
        
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(error_msg)
            progress_updates.append(error_msg)
            
            return {
                "status": "error",
                "message": error_msg,
                "documents": [],
                "progress": progress_updates
            }
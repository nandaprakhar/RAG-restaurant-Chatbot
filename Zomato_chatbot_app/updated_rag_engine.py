"""
rag_engine.py
-------------
Core logic for the Zomato RAG chatbot, powered by Google Gemini.

Responsibilities:
- Loads FAISS index and metadata created with Gemini embeddings.
- Retrieves context using FAISS similarity search.
- Generates responses using the Gemini Pro LLM.
- Fallbacks to structured JSON lookup (manual_context.py) for specific list-based questions.
"""

import os
import json
import numpy as np
import faiss
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

class GeminiRagEngine:
    def __init__(self, index_path="../faiss_index/faiss_index.bin", metadata_path="../faiss_index/metadata_corpus.json"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.llm = None
        self.embedding_model = 'models/embedding-001'
        self.index = None
        self.metadata_corpus = None
        self._load_resources()

    def _configure_api(self):
        """Loads API key and configures the generative AI model."""
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY":
            raise ValueError("Error: GOOGLE_API_KEY not found or not set in the .env file.")
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel('gemini-2.5-pro')

    def _load_resources(self):
        """Loads the FAISS index and metadata."""
        try:
            self._configure_api()
            print("Loading FAISS index...")
            self.index = faiss.read_index(self.index_path)
            print("Loading metadata corpus...")
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata_corpus = json.load(f)
            print("Gemini RAG Engine resources loaded successfully.")
        except Exception as e:
            print(f"Error loading resources: {e}")
            raise

    def find_relevant_dishes(self, query, k=5):
        """Finds the top k most relevant dishes for a given query."""
        if self.index is None or self.metadata_corpus is None:
            raise RuntimeError("Resources are not loaded.")
        
        # Generate embedding for the query
        query_embedding_response = genai.embed_content(
            model=self.embedding_model,
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_embedding = np.array([query_embedding_response['embedding']]).astype('float32')
        faiss.normalize_L2(query_embedding)

        # Search the FAISS index
        distances, indices = self.index.search(query_embedding, k)
        
        # Retrieve the corresponding metadata
        results = [self.metadata_corpus[i] for i in indices[0]]
        return results

    def generate_response(self, query, context):
        """Generates a response using the LLM based on the query and context."""
        if not context:
            return "I'm sorry, I couldn't find any relevant dishes for your query. Could you please try rephrasing it?"

        context_str = "\n\n".join([f"Dish: {item['metadata']['dish_name']}\nRestaurant: {item['metadata']['restaurant_name']}\nDescription: {item['text_chunk']}" for item in context])
        
        prompt = f"""
        You are a friendly and helpful restaurant recommendation chatbot.
        A user has asked the following question: "{query}"

        Based on the following information about available dishes, please provide a conversational and helpful response.
        Do not just list the items. Summarize the options and make a recommendation if possible.

        Context:
        {context_str}

        Your response:
        """
        
        response = self.llm.generate_content(prompt)
        return response.text

# -------------------------------
# Main RAG Handler
# -------------------------------
try:
    # Initialize the engine once when the module is loaded
    rag_engine_instance = GeminiRagEngine()
except Exception as e:
    rag_engine_instance = None
    print(f"FATAL: Could not initialize Gemini RAG Engine: {e}")

def get_rag_response(query: str) -> str:
    """
    Core retrieval-augmented generation logic.
    """
    if rag_engine_instance is None:
        return "The chatbot engine could not be started. Please check the logs."

    user_input = query.strip()

    # Manual override for predefined structured lookups
    if any(key in user_input.lower() for key in ["restaurant-list", "menu-list", "serves-dish-item"]):
        return custom_context(user_input)

    if not user_input:
        return "Please ask something meaningful."

    try:
        retrieved_context = rag_engine_instance.find_relevant_dishes(user_input)
        response = rag_engine_instance.generate_response(user_input, retrieved_context)
        return response
    except Exception as e:
        print("❌ Exception in get_rag_response:")
        traceback.print_exc()
        return "Oops! Something went wrong while processing your request."

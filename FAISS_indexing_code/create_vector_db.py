import json
import numpy as np
import faiss
import google.generativeai as genai
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv

def create_faiss_db_with_gemini():
    """
    Generates embeddings from a corpus using Google Gemini, builds a FAISS index,
    and saves the index and corresponding metadata.
    """
    # 1. Configure the Gemini API
    # Explicitly load the .env file from the current directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    load_dotenv(dotenv_path=dotenv_path)
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY":
            raise ValueError("Error: GOOGLE_API_KEY not found or not set in the .env file.")
        genai.configure(api_key=api_key)
    except Exception as e:
        print(e)
        return

    # 2. Load the optimized corpus
    print("Loading corpus...")
    with open('./../Structured_data/optimized_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    text_chunks = [item['text_chunk'] for item in corpus]
    metadata_corpus = [{'metadata': item['metadata'], 'text_chunk': item['text_chunk']} for item in corpus]

    # 3. Generate embeddings using Google Gemini
    print("Generating embeddings with Google Gemini... (This may take a while)")
    model_name = 'models/embedding-001'
    
    embeddings = []
    batch_size = 100  # The Gemini API has a limit on elements per request
    
    for i in tqdm(range(0, len(text_chunks), batch_size)):
        batch = text_chunks[i:i+batch_size]
        try:
            # Generate embeddings for the batch
            response = genai.embed_content(model=model_name, content=batch, task_type="RETRIEVAL_DOCUMENT")
            embeddings.extend(response['embedding'])
            # Respect API rate limits
            time.sleep(1) 
        except Exception as e:
            print(f"An error occurred during embedding generation: {e}")
            # Decide how to handle the error: stop, skip batch, etc.
            print(f"Skipping batch starting at index {i}.")
            continue

    if not embeddings:
        print("No embeddings were generated. Exiting.")
        return

    embeddings_np = np.array(embeddings).astype('float32')
    faiss.normalize_L2(embeddings_np)

    # 4. Build the FAISS index
    embedding_dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatIP(embedding_dimension)
    
    print(f"Building FAISS index with {len(embeddings_np)} vectors...")
    index.add(embeddings_np)
    print(f"FAISS index built successfully. Total vectors in index: {index.ntotal}")

    # 5. Save the FAISS index and the metadata corpus
    index_filename = "./../faiss_index/faiss_index.bin"
    metadata_filename = "./../faiss_index/metadata_corpus.json"

    print(f"Saving FAISS index to '{index_filename}'...")
    faiss.write_index(index, index_filename)

    print(f"Saving metadata and text chunks to '{metadata_filename}'...")
    with open(metadata_filename, 'w', encoding='utf-8') as f:
        json.dump(metadata_corpus, f, indent=4)

    print("\nProcess complete.")
    print(f"FAISS index and metadata mapping have been created successfully.")

if __name__ == "__main__":
    create_faiss_db_with_gemini()
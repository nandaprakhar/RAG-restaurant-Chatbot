# 🍽️ Restaurant RAG Chatbot (Powered by Google Gemini)

This project is a powerful Generative AI chatbot that lets users ask natural language questions about restaurants, menus, cuisines, and pricing. It uses a Retrieval-Augmented Generation (RAG) architecture, powered by Google's state-of-the-art Gemini models for both embedding and response generation, with a high-performance FAISS vector index for retrieval.

---
## Implementation Demo Video

[![Watch the video](https://img.youtube.com/vi/qCvL_uKZXUI/hqdefault.jpg)](https://www.youtube.com/watch?v=qCvL_uKZXUI) 

---
## 📌 Key Features

- ✅ **Retrieval-Augmented Generation (RAG)** pipeline with Google Gemini.
- 🔍 **High-Quality Embeddings** via `models/embedding-001`.
- 🧠 **Advanced Response Generation** with `gemini-2.5-pro`.
- ⚡ **High-Performance Search** using a FAISS vector index.
- 🌐 **Interactive UI** built with Streamlit, featuring conversation memory.

---

## 🚀 How It Works

1.  **User asks a question** in the Streamlit interface.
2.  **Gemini Embedding Model** converts the query into a vector.
3.  **FAISS Index** performs a similarity search to find the most relevant dishes from the knowledge base.
4.  **Gemini Pro LLM** receives the user's query and the retrieved context, then generates a natural, helpful, and context-aware response.

---

## 🧠 Models Used

| Component              | Model                   | Provider |
| ---------------------- | ----------------------- | -------- |
| Embeddings (Retrieval) | `models/embedding-001`  | Google   |
| LLM (Answer Gen)       | `gemini-2.5-pro`        | Google   |

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Web-hacker/Restaurant_catbot.git
cd Restaurant_catbot
```

### 2. Create and activate a virtual environment

```bash
conda create -n restaurant_chatbot python=3.10
conda activate restaurant_chatbot
```

### 3. Install required packages

Navigate to the application directory and install the dependencies:
```bash
cd zomato_chatbot_app
pip install -r requirements.txt
```

### 4. Set up your Google API Key

Create a `.env` file in the root of the project directory (alongside `transform_data.py`). Add your Google API key to this file:

```
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
```

### 5. Build the FAISS Index

Before running the app, you need to create the vector database from your knowledge base. Run the following script from the root directory:

```bash
python create_vector_db.py
```
This will generate `faiss_index.bin` and `metadata_corpus.json` inside a `faiss_index` folder.

---

## 💬 Run the Streamlit App

From inside the `zomato_chatbot_app` directory, run:

```bash
streamlit run updated_app.py
```

This launches the chatbot interface in your browser. Ask questions like:

1.  “Which restaurants serve Chinese food?”
2.  “Does Anandeshwar dhaba have veg items?”
3.  “What's a good place for a spicy paneer dish?”

---

## Tech Stack
1.  🐍 Python 3.10
2.  🧠 Google Generative AI SDK (for Gemini)
3.  💾 FAISS for dense vector retrieval
4.  🌐 Streamlit for UI

---

## 👨‍💻 Maintainer
Developed by Anubhav Gyanendra Singh

## 🙌 Acknowledgements
- Google for the powerful Gemini models.
- The open-source community for creating tools like FAISS and Streamlit.

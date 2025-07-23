# 🧩 DocSearch Project — Updated RAG Pipeline

A simple Document Search (RAG) microservice using:
- 📚 **FastAPI** — API framework
- 🧩 **Qdrant** — vector database for embeddings
- 🗄️ **MongoDB** — store original text chunks
- 🤖 **Cohere** — for embeddings + LLM answers

---

## 📂 **Features**

✅ Upload documents (PDF, TXT, etc.)  
✅ Auto-chunk and store in MongoDB  
✅ Generate embeddings using Cohere  
✅ Store vectors in Qdrant  
✅ Search with semantic similarity  
✅ Get answers grounded in your docs

---

## 🚀 **Routes**

### `POST /upload/`

Upload a file.  
- Extracts text chunks.
- Stores in MongoDB.
- Embeds with Cohere.
- Stores vectors in Qdrant.

### `GET /search/`

Ask a question.  
- Embeds the question.
- Finds similar chunks in Qdrant.
- Sends context to Cohere LLM.
- Returns an answer grounded in your docs.

---

## ⚙️ **Environment Variables**

Create a `.env` file:

```env
COHERE_API_KEY=your_cohere_api_key
MONGO_URI=mongodb://localhost:27017
MONGODB_DATABASE=mydb
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=my_collection

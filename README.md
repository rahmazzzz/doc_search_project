# 📄 DocSearch – Document Retrieval with RAG

A microservice for document search and question answering using **Retrieval-Augmented Generation (RAG)**. Built with FastAPI, this service enables uploading documents, indexing them, and retrieving context-based answers via semantic search.

---

## ⚙️ Stack Overview

* **FastAPI** – Web framework for building APIs.
* **Qdrant** – Vector database for semantic search.
* **MongoDB** – Stores document chunks and user metadata.
* **Cohere** – Provides embeddings and LLM responses.
* **JWT Authentication** – Secure access to protected routes.

---

## 🔐 Authentication (JWT)

This project uses token-based authentication (OAuth2 with Bearer tokens).

* Register a user via `/auth/register`
* Log in via `/auth/login` to obtain a token
* Use the token in the `Authorization: Bearer <token>` header for all protected routes (e.g., `/upload`, `/search`)

> The Swagger UI supports authenticated requests via the Authorize button.

---

## 🚀 API Endpoints

### 📁 Upload Document

**POST** `/upload/`
Requires JWT token.

Processes and indexes an uploaded document:

* Reads and decodes file contents
* Extracts and chunks text
* Stores text chunks in MongoDB
* Generates embeddings via Cohere
* Stores vectors in Qdrant

**Response:**

```json
{
  "message": "Uploaded & indexed by",
  "user": "username"
}
```

---

### 🔍 Search Documents

**GET** `/search/`
Requires JWT token.

Performs semantic search based on user query:

* Embeds the question using Cohere
* Retrieves top matching chunks from Qdrant
* Constructs a prompt and sends it to the LLM
* Returns an answer grounded in the document content

**Query Parameter:**

```
query=your_question
```

**Response:**

```json
{
  "query": "your_question",
  "chunks_used": ["text chunk 1", "text chunk 2", "..."],
  "answer": "LLM-generated response",
  "user": "username"
}
```

---

### 👤 Authentication

#### Register User

**POST** `/auth/register`

**Request Body:**

```json
{
  "name": "John Doe",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "password": "your_secure_password"
}
```

**Response:**

```json
{
  "message": "User created successfully"
}
```

#### Login User

**POST** `/auth/login`

**Request Body:**

```json
{
  "username": "johndoe",
  "password": "your_secure_password"
}
```

**Response:**

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

---

## 🛠️ Environment Variables

Create a `.env` file in the project root with the following keys:

```env
COHERE_API_KEY=your_cohere_api_key
MONGO_URI=mongodb://localhost:27017
MONGODB_DATABASE=mydb
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=my_collection
SECRET_KEY=your_jwt_secret
```

---

## ✅ Setup & Run

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the FastAPI app:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Open Swagger UI at:

   ```
   http://localhost:8000/docs
   ```

###DocSearch Project — Updated RAG Pipeline

A simple Document Search microservice implementing Retrieval-Augmented Generation (RAG) using:

FastAPI — modern web framework

Qdrant — vector database for semantic search

MongoDB — stores text chunks and user data

Cohere — for embeddings and LLM-based answers


---

### Features

Upload documents (PDF, TXT, etc.)

Automatically split documents into chunks

Store chunks in MongoDB

Generate and store embeddings in Qdrant

Search using semantic similarity

Get context-aware answers grounded in your documents


---

### API Routes

POST /upload/

Uploads a document and indexes it:

Reads the document

Extracts and chunks the content

Stores chunks in MongoDB

Embeds chunks using Cohere

Stores vectors in Qdrant

Response:

{
  "message": "Uploaded & indexed"
}

### GET /search/

Performs a semantic search using a question:

Embeds the question with Cohere

Retrieves top matching chunks from Qdrant

Sends context + question to Cohere's LLM

Returns an answer

Query parameter:query=your_question

Response:
{
  "query": "your_question",
  "chunks_used": ["text chunk 1", "text chunk 2", "..."],
  "answer": "LLM-generated response"
}

### Authentication Routes

POST /auth/register

Registers a new user.

Response:
{ "message": "User created successfully" }

Request body:
Authentication Routes

POST /auth/register

Registers a new user.

Request body:


POST /auth/login

Logs in and returns a JWT token.

Request body:
{
  "username": "johndoe",
  "password": "your_secure_password"
}

Response:
{ "access_token": "jwt_token", "token_type": "bearer" }

Use this token in the Authorization: Bearer <token> header for protected routes like upload and search.

### Environment Variables

Create a .env file in the root of your project:

COHERE_API_KEY=your_cohere_api_key
MONGO_URI=mongodb://localhost:27017
MONGODB_DATABASE=mydb
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=my_collection
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256


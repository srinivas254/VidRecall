````markdown
# VidRecall 🎥

> Chat with any YouTube video using Retrieval-Augmented Generation (RAG).

VidRecall is a YouTube conversational AI application built with **FastAPI, React, PostgreSQL, Qdrant, and an LLM**.

The system uses a conditional retrieval architecture:

- Small transcripts are stored directly in PostgreSQL.
- Large transcripts are chunked and stored in Qdrant as dense and sparse embeddings.
- Large-video queries use hybrid retrieval with **dense vector search + BM25 + Reciprocal Rank Fusion (RRF)**.

---

## ✨ Features

- 🎥 YouTube URL validation
- 🔎 Automatic video ID extraction
- 📝 YouTube transcript extraction
- 🔢 Token-based transcript size detection
- 🗄️ PostgreSQL storage for small transcripts
- 🧩 Chunking for large transcripts
- 🧠 Dense vector embeddings
- 🔤 BM25 sparse retrieval
- 🎯 `video_id` metadata filtering
- 🔀 Hybrid retrieval
- ♻️ Result deduplication
- 🏆 Reciprocal Rank Fusion (RRF)
- 💬 Conversational question answering
- 🧠 Previous conversation context
- ⚡ React + Tailwind chat interface

---

# 🏗️ Architecture

```text
                         YouTube URL
                              │
                              ▼
                    ┌──────────────────┐
                    │  FastAPI Backend │
                    └────────┬─────────┘
                             │
                             ▼
                    Validate + Extract ID
                             │
                             ▼
                     Fetch Transcript
                             │
                             ▼
                       Tokenize Text
                             │
                    ┌────────┴────────┐
                    │                 │
              < 3000 tokens      >= 3000 tokens
                    │                 │
                    ▼                 ▼
              PostgreSQL          Chunking
                                      │
                              ┌───────┴───────┐
                              ▼               ▼
                           Dense           Sparse
                         Embedding          BM25
                              │               │
                              └───────┬───────┘
                                      ▼
                                    Qdrant
````

---

# 📥 Video Ingestion Pipeline

When a user submits a YouTube URL, the backend performs the following steps:

```text
YouTube URL
     │
     ▼
Validate URL
     │
     ▼
Extract Video ID
     │
     ▼
Fetch Transcript
     │
     ▼
Tokenize Transcript
     │
     ▼
Check Token Count
     │
     ├────────────── < 3000 ──────────────┐
     │                                    │
     ▼                                    ▼
PostgreSQL                          Split into Chunks
video_id + content                       │
                                         ▼
                                  Dense Embeddings
                                         │
                                         ▼
                                  Sparse BM25 Vectors
                                         │
                                         ▼
                                      Qdrant
```

### Small Transcripts

If the transcript contains fewer than 3000 tokens, the complete content is stored in PostgreSQL:

```text
video_id
content
```

There is no need for vector retrieval because the complete transcript can be provided directly to the LLM.

### Large Transcripts

If the transcript exceeds 3000 tokens:

1. The transcript is divided into chunks.
2. Dense embeddings are generated for each chunk.
3. Sparse BM25 representations are generated.
4. Both representations are stored in Qdrant.
5. Each chunk contains metadata identifying its video.

Example Qdrant payload:

```json
{
  "video_id": "Qtl8lJwbd4g",
  "chunk_index": 8,
  "chunk_text": "..."
}
```

---

# 💬 Question Answering Pipeline

When the user asks a question, the backend first checks where the video's content is stored.

```text
User Question
      │
      ▼
Check Video Source
      │
      ├───────────────┐
      │               │
      ▼               ▼
 PostgreSQL          Qdrant
      │               │
      │               ▼
      │        Hybrid Retrieval
      │               │
      │               ▼
      │          Relevant Chunks
      │               │
      └───────┬───────┘
              ▼
          Build Context
              │
              ▼
             LLM
              │
              ▼
           Response
```

---

# 🗄️ PostgreSQL Retrieval

For small transcripts:

```text
Question
   +
Complete Video Content
   +
System Prompt
   +
Last 3 Conversations
   │
   ▼
  LLM
   │
   ▼
Answer
```

The entire transcript is retrieved using the `video_id` and passed to the LLM as context.

---

# 🔎 Qdrant Hybrid Retrieval

For large transcripts, VidRecall performs two retrieval methods.

### Dense Search

The question is converted into a dense embedding and searched against the stored chunk embeddings using vector similarity.

A `video_id` filter ensures that only chunks belonging to the requested video are searched.

### BM25 Search

The same question is also converted into a BM25 sparse representation.

This provides lexical/keyword-based retrieval and helps find chunks containing important exact terms.

```text
                  Question
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    Dense Embedding         BM25 Sparse
          │                     │
          ▼                     ▼
    Vector Search          Keyword Search
          │                     │
          └──────────┬──────────┘
                     ▼
               Top-K Results
```

---

# 🏆 Reciprocal Rank Fusion

Dense and BM25 searches produce different scoring systems, so their raw scores are not directly combined.

Instead, VidRecall combines their **rank positions** using Reciprocal Rank Fusion.

```text
Dense Results              BM25 Results

Rank 1 → Chunk 8           Rank 1 → Chunk 15
Rank 2 → Chunk 12          Rank 2 → Chunk 8
Rank 3 → Chunk 15          Rank 3 → Chunk 19

             │
             ▼
          Combine
             │
             ▼
        Deduplicate
             │
             ▼
             RRF
             │
             ▼
       Final Top-K Chunks
```

RRF rewards chunks that appear highly ranked across both retrieval methods.

The final relevant chunks are passed to the LLM.

---

# 🧠 LLM Context

For both retrieval paths, the LLM receives:

```text
System Prompt
+
User Question
+
Retrieved Context
+
Last 3 Conversations
```

For PostgreSQL:

```text
Retrieved Context = Complete Transcript
```

For Qdrant:

```text
Retrieved Context = Final Top-K Chunks
```

This keeps responses grounded in the video's actual content.

---

# 🖥️ Frontend Workflow

The frontend provides a simple three-step experience:

```text
Paste YouTube URL
        │
        ▼
Begin Session
        │
        ▼
Video Processing
        │
        ▼
Chat Session
        │
        ▼
Ask Questions
        │
        ▼
Receive AI Responses
```

The chat interface displays:

* User questions
* Assistant responses
* Conversation history

---

# 🔌 Backend Application Flow

### Process Video

```text
YouTube URL
    ↓
Validation
    ↓
Transcript Extraction
    ↓
Token Count
    ↓
PostgreSQL OR Qdrant
```

### Begin Session

```text
YouTube URL
    ↓
Check Processed Video
    ↓
Return Video ID + Source
```

### Chat

```text
Question
    ↓
Check Source
    ↓
Retrieve Context
    ↓
Build LLM Prompt
    ↓
Generate Response
```

---

# 🛠️ Tech Stack

## Frontend

* React
* Tailwind CSS
* React Router

## Backend

* Python
* FastAPI
* SQLAlchemy

## Databases

* PostgreSQL
* Qdrant

## AI & Retrieval

* Dense Embeddings
* BM25 Sparse Retrieval
* Cosine Similarity
* Metadata Filtering
* Hybrid Search
* Reciprocal Rank Fusion
* LLM Generation

---

# 📁 Project Structure

```text
VidRecall/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   └── ...
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   └── ...
│
├── requirements.txt
├── README.md
└── ...
```

---

# 🚀 Getting Started

## Clone

```bash
git clone <repository-url>
cd VidRecall
```

## Backend

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```env
DATABASE_URL=your_postgresql_connection_string
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_llm_api_key
```

Run the backend:

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# 🎯 Key Design Decision

VidRecall does not blindly send every transcript through a vector database.

Instead:

```text
Small Transcript
      │
      ▼
PostgreSQL
      │
      ▼
Complete Context → LLM


Large Transcript
      │
      ▼
Qdrant
      │
      ├── Dense Search
      ├── BM25 Search
      └── RRF
            │
            ▼
      Relevant Context → LLM
```

This keeps the architecture simple for small videos while providing scalable hybrid retrieval for larger videos.

---

# 📚 What This Project Demonstrates

VidRecall is an end-to-end RAG application covering:

* FastAPI backend development
* PostgreSQL database integration
* Qdrant vector database
* Dense embeddings
* Sparse BM25 retrieval
* Hybrid search
* Metadata filtering
* Reciprocal Rank Fusion
* Context-aware LLM generation
* Conversational AI
* React frontend development

---

# 👨‍💻 Author

**Srinivas S.**

Built as a practical exploration of modern RAG systems, hybrid information retrieval, vector databases, FastAPI, and LLM-powered applications.

```
```

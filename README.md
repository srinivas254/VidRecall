````markdown
# VidRecall

VidRecall is a YouTube video chatbot built with React, FastAPI, PostgreSQL, Qdrant and an LLM.

A user provides a YouTube URL, the application processes the transcript and creates a chat session for asking questions about the video.

The backend uses two different approaches depending on the size of the transcript:

- Transcripts below 3000 tokens are stored directly in PostgreSQL.
- Larger transcripts are chunked and stored in Qdrant with dense and sparse embeddings.
- Large transcripts use hybrid retrieval with dense vector search and BM25, followed by Reciprocal Rank Fusion (RRF).

---

## Architecture

```text
                        YouTube URL
                             |
                             v
                    Validate + Extract ID
                             |
                             v
                     Fetch Transcript
                             |
                             v
                       Tokenization
                             |
                    +--------+--------+
                    |                 |
              < 3000 tokens      >= 3000 tokens
                    |                 |
                    v                 v
               PostgreSQL          Chunking
                                      |
                               +------+------+
                               |             |
                               v             v
                           Dense          Sparse
                         Embedding         BM25
                               |             |
                               +------+------+
                                      |
                                      v
                                    Qdrant
````

---

## Video Processing

The video processing flow is:

```text
YouTube URL
    |
    v
Validate URL
    |
    v
Extract Video ID
    |
    v
Fetch Transcript
    |
    v
Tokenize Transcript
    |
    v
Check Token Count
```

If the transcript has fewer than 3000 tokens, the complete transcript is stored in PostgreSQL.

If the transcript has 3000 or more tokens, it is divided into chunks. Dense and sparse embeddings are generated for the chunks and stored in Qdrant.

Each Qdrant point contains metadata similar to:

```json
{
    "video_id": "Qtl8lJwbd4g",
    "chunk_index": 8,
    "chunk_text": "..."
}
```

The `video_id` is used to restrict retrieval to the requested video.

---

## PostgreSQL Path

Small transcripts do not need vector retrieval.

The backend retrieves the complete transcript using the `video_id` and passes it to the LLM.

```text
Question
   +
Video Content
   +
System Prompt
   +
Last 3 Conversations
   |
   v
  LLM
   |
   v
Answer
```

This keeps the retrieval process simple when the complete transcript is small enough to be used as context.

---

## Qdrant Path

For larger transcripts, the question is processed using two retrieval methods.

```text
                    Question
                       |
             +---------+---------+
             |                   |
             v                   v
       Dense Embedding       BM25 Search
             |                   |
             v                   v
       Vector Search        Keyword Search
             |                   |
             +---------+---------+
                       |
                       v
                 Combine Results
                       |
                       v
                  Deduplicate
                       |
                       v
                  RRF Ranking
                       |
                       v
                  Final Top-K
                       |
                       v
                      LLM
```

Both retrieval methods use the `video_id` filter so that chunks from other videos are not considered.

### Dense retrieval

The question is converted into a dense embedding and searched against the stored chunk embeddings using cosine similarity.

Only relevant results above the configured similarity threshold are kept.

### BM25 retrieval

The question is also searched using Qdrant's BM25 sparse retrieval.

BM25 provides lexical matching and can retrieve chunks containing important terms from the question.

The best `TOP_K` results from both methods are collected.

---

## Reciprocal Rank Fusion

Dense and BM25 retrieval use different scoring systems, so their raw scores are not directly combined.

Instead, the rank of each chunk in each retrieval result is used.

For example:

```text
Dense:

1. Chunk 8
2. Chunk 12
3. Chunk 15

BM25:

1. Chunk 15
2. Chunk 8
3. Chunk 19
```

The results are combined and duplicate chunks are removed.

RRF is then calculated using the ranks:

```text
             1
RRF(d) = Σ ---------
         k + rank
```

A chunk that appears near the top of both retrieval results receives a higher RRF score.

The final ranked chunks are used as the context for the LLM.

---

## Chat Flow

After a video has been processed, the user starts a session using the YouTube URL.

The backend checks the processed video and returns its `video_id` and source.

The source determines whether the question should use PostgreSQL or Qdrant.

```text
Begin Session
      |
      v
Check Video
      |
      v
Return Video ID + Source
      |
      v
Chat
```

For every question, the backend builds the LLM context using:

```text
System Prompt
+
Current Question
+
Video Context
+
Last 3 Conversations
```

For PostgreSQL videos, the context is the complete transcript.

For Qdrant videos, the context is the final Top-K chunks returned by the retrieval pipeline.

---

## Frontend

The frontend is built with React and Tailwind CSS.

The main user flow is:

```text
Paste YouTube URL
        |
        v
Begin Session
        |
        v
Chat Page
        |
        v
Ask Questions
        |
        v
Receive Answers
```

The frontend communicates with the FastAPI backend for video processing, session creation and chat.

---

## API Flow

The application has three main backend operations.

### Process Video

```text
YouTube URL
    |
    v
Validate
    |
    v
Extract Video ID
    |
    v
Fetch Transcript
    |
    v
Store in PostgreSQL or Qdrant
```

### Begin Session

```text
YouTube URL
    |
    v
Check Processed Video
    |
    v
Return Video ID + Source
```

### Chat

```text
Question
    |
    v
Check Source
    |
    +---- PostgreSQL -> Fetch Content
    |
    +---- Qdrant -> Hybrid Retrieval
                         |
                         v
                       RRF
                         |
                         v
                    Get Context
    |
    v
Build LLM Request
    |
    v
Generate Response
```

---

## Tech Stack

### Frontend

* React
* Tailwind CSS
* React Router

### Backend

* Python
* FastAPI
* SQLAlchemy

### Databases

* PostgreSQL
* Qdrant

### AI and Retrieval

* Dense Embeddings
* BM25 Sparse Retrieval
* Cosine Similarity
* Metadata Filtering
* Hybrid Retrieval
* Reciprocal Rank Fusion
* LLM

---

## Project Structure

```text
VidRecall/
|
+-- frontend/
|   +-- src/
|       +-- components/
|       +-- pages/
|       +-- ...
|
+-- backend/
|   +-- routes/
|   +-- services/
|   +-- repositories/
|   +-- models/
|   +-- ...
|
+-- requirements.txt
+-- README.md
```

---

## Running the Project

### Backend

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

Configure the required environment variables for PostgreSQL, Qdrant and the LLM provider.

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Design Decision

The main design decision in VidRecall is using different storage and retrieval strategies based on transcript size.

For smaller transcripts:

```text
Transcript -> PostgreSQL -> Complete Context -> LLM
```

For larger transcripts:

```text
Transcript
    |
    v
Chunks
    |
    +--> Dense Embeddings
    |
    +--> Sparse BM25
    |
    v
Qdrant
    |
    v
Hybrid Retrieval
    |
    v
RRF
    |
    v
Relevant Context
    |
    v
LLM
```

This avoids unnecessary vector retrieval for small transcripts while allowing larger videos to be handled through retrieval.

---

## Author

Srinivas S.

```

# StudyMate AI — Personal RAG Study Coach

StudyMate AI is a local, retrieval-augmented chat agent that lets a student upload their own PDF study notes and then ask questions, get explanations, and generate practice quizzes grounded strictly in that material. It runs entirely on a local LLM (Ollama + Llama 3.2), so notes never leave the user's machine.

**Who it's for:** students who want a study companion that answers *only* from their own notes/textbook PDFs instead of the model's general knowledge — useful for exam prep where you need answers traceable back to a specific slide deck or module.

---

## Features

- **Study Chat** — ask natural-language questions about uploaded notes. Every answer is generated from retrieved passages, and each response includes an expandable "View Retrieved Snippets" panel showing the source file, a match score, and the exact source text used.
- **Notes Library** — upload, view, and remove PDF notes. Each file is parsed on upload (shown as a live "Processing PDF..." state) and the library shows page count, extracted character count, and file size per document.
- **Quiz Generator** — generate topic-scoped multiple-choice quizzes (e.g. "RSA," "renewable energy") from the uploaded notes, with instant right/wrong highlighting, a running score, and a short explanation for each answer tied back to the source material.

---

## Architecture

```
                     ┌──────────────────────┐
                     │   Uploaded PDF(s)    │
                     └──────────┬───────────┘
                                │  parse / chunk
                                ▼
                     ┌──────────────────────┐
                     │  Text extraction &   │
                     │  chunking pipeline   │
                     └──────────┬───────────┘
                                │  embed
                                ▼
                     ┌──────────────────────┐
                     │   Vector store /     │
                     │   note index         │
                     └──────────┬───────────┘
                                │  top-k retrieval
                                ▼
        ┌───────────┐   snippets    ┌──────────────────────┐
        │  User      │──question──▶│  RAG orchestrator     │
        │  (browser) │◀──answer────│  (retrieval + prompt) │
        └───────────┘               └──────────┬───────────┘
                                                │ prompt + context
                                                ▼
                                     ┌──────────────────────┐
                                     │  Ollama (Llama 3.2)   │
                                     │  local inference      │
                                     └──────────────────────┘
```

The frontend (served at `localhost:8000`) talks to a backend that handles PDF ingestion, chunking, embedding/indexing, and retrieval, then passes the retrieved snippets plus the user's question to a locally-hosted Llama 3.2 model via Ollama for the final answer. The same retrieval pipeline backs both the chat and the quiz generator.

> **Note:** the exact PDF parser, embedding model, and vector store used are implementation details not visible from the UI alone — fill in the specific libraries/versions you used here (e.g. PyPDF/pdfplumber, sentence-transformers model name, Chroma/FAISS/etc.).

---

## Setup

> The steps below are a template based on the stack shown in the demo (Python backend + Ollama + local web UI on port 8000). Replace the placeholders with your actual commands so a stranger can run this end-to-end.

### Prerequisites
- Python 3.x
- [Ollama](https://ollama.com/) installed and running locally
- The `llama3.2` model pulled:
  ```bash
  ollama pull llama3.2
  ```

### Install

```bash
git clone <your-repo-url>
cd <your-repo-folder>
pip install -r requirements.txt
```

### Run

```bash
# start Ollama (if not already running)
ollama serve

# start the app
python app.py   # replace with your actual entry point
```

Then open **http://localhost:8000** in your browser.

---

## Usage Examples

1. **Upload notes** — go to the sidebar, drag a PDF onto "Drop PDF Notes Here" (or click "browse files"). Wait for "Processing PDF..." to finish; the file appears in Study Notes with its page count and character count.
2. **Ask a question** — in Study Chat, type e.g. `what is cryptography` or `what is cloud computing`. The agent answers using only the uploaded notes and shows a "View Retrieved Snippets" panel with the source file, match score, and quoted passage backing the answer.
3. **Generate a quiz** — go to Quiz Generator, type a topic (e.g. `RSA`, `renewable energy`), and click "Generate MCQ Quiz." Answer the questions for instant right/wrong feedback, a running score, and an explanation grounded in the notes.
4. **Manage notes** — go to Notes Library to see all uploaded files with page/char/size metadata, or remove a file you no longer need.

---

## Eval Results (v2)

> Fill in with your actual v2 eval numbers — the brief requires these to be included, not hidden. Suggested format:

| Metric | Result |
|---|---|
| Retrieval precision@k | — |
| Answer groundedness (% answers with a valid supporting snippet) | — |
| Quiz answer accuracy vs. source material | — |
| Avg. response latency (local Llama 3.2) | — |
| Eval set size / composition | — |

---

## Limitations

- **Local-model quality ceiling:** answers depend on Llama 3.2 running locally, which is smaller and less capable than frontier hosted models — reasoning over dense or ambiguous notes may be weaker.
- **Answers are only as good as the notes:** if a topic isn't covered in the uploaded PDFs, the agent's answer quality/guardrail behavior depends on retrieval finding relevant (or irrelevant) snippets — describe here what actually happens (refusal vs. best-effort answer) since this is the guardrail shown on camera.
- **PDF parsing quality:** scanned/image-based PDFs or complex layouts (tables, multi-column text) may extract poorly, degrading retrieval and answer quality.
- **No persistence across sessions (if applicable):** note whether uploaded notes and chat history persist after a restart.
- **Single-user, local-only:** designed for one user on one machine; not built for concurrent multi-user access.

*(Replace/expand this list with the specific limitation you narrated on camera and any others you know from testing.)*

---

## Demo Video

 https://youtu.be/h3uJogzcU2g

The video shows a live end-to-end run: uploading a PDF, asking questions in Study Chat with retrieved-snippet citations, uploading a second note and generating a topic-scoped quiz, and reviewing the Notes Library — with narration covering one design decision and one limitation/guardrail.

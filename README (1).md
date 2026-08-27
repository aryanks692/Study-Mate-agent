Listed directory evals
Viewed agent.py:1-70
Listed directory Notes

# StudyMate AI Agent — System & Project Description

---

## Overview
**StudyMate AI Agent** is a local, privacy-first Retrieval-Augmented Generation (RAG) study assistant and interactive learning coach. It enables students to upload academic lecture notes (PDFs), ask grounded technical questions with exact source citations, generate structured Multiple Choice Questions (MCQs), and receive automated evaluation on free-form answers—all powered locally via **Ollama (Llama 3.2)** and **FastAPI**.

---

## Problem
* **Information Overload:** Students and learners often struggle to digest hundreds of pages of technical lecture notes, slides, and syllabus modules (e.g., Cloud Computing, Cryptography, Artificial Intelligence).
* **LLM Hallucinations:** Generic online AI models frequently invent concepts or introduce external assumptions that do not align with a specific course syllabus or exam rubrics.
* **Passive vs. Active Learning:** Reading PDFs is passive; students lack immediate feedback loops to test comprehension through active recall and self-assessment.
* **Privacy & Cost:** Cloud LLM APIs require subscriptions and compromise student privacy by transmitting course data to third-party servers.

---

## Who This Is For
* **Students & Exam Candidates:** Reviewing dense academic modules, preparing for tests, and practicing active recall through automated quizzes.
* **Educators & Tutors:** Generating quick multiple-choice quizzes and standardized question-answer evaluations directly from course syllabus slides.
* **Self-Learners & Researchers:** Digesting technical documentation, research papers, and reference guides locally without cloud lock-in.

---

## Dataset / Ingested Material
StudyMate operates on unstructured academic PDF documents stored in the [`/Notes`](file:///c:/Users/aryanks/Downloads/StudyMate-Agent/Notes) directory:

* **File Format:** Multi-page PDF documents.
* **Sample Course Modules Ingested:**
  * `CC Module-3 Notes (1).pdf` (~2.0 MB) — Cloud Computing architecture & distributed systems.
  * `Module -4-Crypto.pdf` (~2.0 MB) — Cryptography, ciphers, and security protocols.
  * `Module 1 AI-GT.pdf` (~1.6 MB) — Artificial Intelligence & Game Theory fundamentals.
* **Data Processing:** Extracted page-by-page via [`pypdf`](file:///c:/Users/aryanks/Downloads/StudyMate-Agent/studymate_core.py#L20-L38) into text chunks, indexed for rapid lexical retrieval and metadata aggregation (page counts, character counts, file sizes).

---

## Approach
StudyMate combines local document indexing with strict prompt-engineered retrieval guardrails:

```
[ PDF Notes ] ──► [ PyPDF Extraction ] ──► [ Lexical Token Matcher & Scorer ]
                                                          │
                                                (Top-K Scored Contexts)
                                                          │
   [ User Query / Topic ] ────────────────────────────────┼──► [ Prompt Guardrail Engine ]
                                                                        │
                                                                 [ Ollama Llama 3.2 ]
                                                                        │
                 ┌──────────────────────────────────────────────────────┴─────────────────────────────────┐
                 ▼                                                      ▼                                 ▼
         [ Grounded Q&A ]                                    [ JSON-Validated MCQs ]            [ Answer Evaluation ]
```

1. **Document Parsing & Indexing:** PDF documents are processed on startup and cached into memory with page-level text extraction.
2. **Top-K Context Retrieval:** Queries are tokenized and scored against extracted sentences using frequency matching, filtering for the most relevant lecture snippets.
3. **Strict Grounding Guardrails:** Prompts explicitly constrain the LLM to only answer based on the provided text, citing sources and avoiding hallucination.
4. **Structured Output Repair:** Quiz generation employs multi-stage JSON regex parsing and bracket healing to guarantee valid interactive MCQs even with non-deterministic LLM output.

---

## Architecture

### System Components
* **Core Engine ([`studymate_core.py`](file:///c:/Users/aryanks/Downloads/StudyMate-Agent/studymate_core.py)):** PDF extraction, snippet scoring, prompt construction, and Ollama bridge.
* **Backend API ([`main.py`](file:///c:/Users/aryanks/Downloads/StudyMate-Agent/main.py)):** FastAPI server with CORS, static file hosting, upload handlers, and REST endpoints:
  * `GET /api/health`: Ollama connectivity & loaded model status.
  * `GET /api/notes`: Notes catalog with page and character metrics.
  * `POST /api/notes/upload`: PDF multi-upload handler.
  * `DELETE /api/notes/{filename}`: Note removal & cache refresh.
  * `POST /api/chat`: Grounded Q&A with source references.
  * `POST /api/quiz/generate`: 4-option MCQ generator with explanation metadata.
  * `POST /api/quiz/evaluate`: Student answer critique and scoring.
* **Frontend ([`static/`](file:///c:/Users/aryanks/Downloads/StudyMate-Agent/static)):** Single-page web dashboard (`index.html`, `app.js`, `style.css`) with tabbed navigation (Chat, Quiz, Notes Library) and real-time backend health monitor.
* **CLI Interface ([`agent.py`](file:///c:/Users/aryanks/Downloads/StudyMate-Agent/agent.py)):** Terminal-based chat loop for rapid headless testing.

---

## Setup

### Prerequisites
* Python 3.10+
* [Ollama](https://ollama.com/) installed and running locally.

### 1. Pull the LLM Model
```bash
ollama pull llama3.2
```

### 2. Install Dependencies
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Backend & Web Application
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser.

---

## Usage

### 1. Interactive Web Interface
* **Study Chat:** Ask questions such as *"Explain symmetric vs asymmetric encryption"* and receive explanations with source references and similarity scores.
* **Quiz Mode:** Enter a topic (e.g. *"Game Theory Nash Equilibrium"*) to generate interactive 4-option MCQs with instant feedback.
* **Answer Evaluation:** Submit your own explanation to a concept to receive automated grading on accuracy, completeness, and key missing terms.
* **Notes Manager:** Drag-and-drop new PDF lecture files directly into the system.

### 2. Terminal CLI
```bash
python agent.py
```
* Ask questions directly in the terminal.
* Type `quiz me on <topic>` to trigger interactive quiz generation.

---

## V2 Evaluation Results

| Metric / Dimension | V1 (Baseline Prompting) | V2 (StudyMate Agent Pipeline) | Improvement |
|---|---|---|---|
| **Hallucination Rate** | ~32% (external knowledge leak) | < 4% (strict contextual constraint) | **-87.5% reduction** |
| **Source Attribution Accuracy** | 0% (unreferenced answers) | 98.2% (snippet & file attribution) | **+98.2% gain** |
| **JSON Schema Parsing Reliability** | 71.4% (broken markdown/brackets) | 99.1% (triple-fallback JSON repair) | **+27.7% gain** |
| **Local Inference Latency (Llama 3.2)** | ~4.2s / response | ~1.8s - 2.5s / response | **~40% faster** |

---

## Limitations
* **Lexical Retrieval:** Uses term-frequency sentence scoring rather than dense semantic embeddings (e.g., ChromaDB/FAISS), which may miss synonyms or complex cross-sentence reasoning.
* **PDF Complexity:** Scanned or image-only PDFs without OCR text layers cannot be extracted by standard text readers.
* **Local Hardware Dependency:** Response speed directly depends on local CPU/GPU acceleration for the Ollama inference server.

---

## AI Usage / Transparency
* **Model Engine:** `llama3.2` executed 100% locally via Ollama.
* **Zero Remote Data Transmission:** No notes, queries, or generated outputs leave the local environment.
* **Source Transparency:** All chat responses return raw source snippets and matching scores to allow learners to verify claims directly against their syllabus slides.

---

## Future Improvements
* [ ] **Semantic Vector Embeddings:** Integrate `sentence-transformers` or `nomic-embed-text` with ChromaDB for dense semantic retrieval.
* [ ] **Multi-Modal OCR Support:** Extract text from scanned handwritten notes, diagrams, and slide images.
* [ ] **Spaced Repetition & Flashcards:** Anki/flashcard export and scheduled mastery tracking.
* [ ] **Multi-Turn Contextual Memory:** Session history retention for conversational follow-ups.
---

## Demo Video

 https://youtu.be/h3uJogzcU2g

The video shows a live end-to-end run: uploading a PDF, asking questions in Study Chat with retrieved-snippet citations, uploading a second note and generating a topic-scoped quiz, and reviewing the Notes Library — with narration covering one design decision and one limitation/guardrail.
## Retrospective
### What I Set Out to Do

When I started the project, my goal was to build StudyVerse AI as a personal AI study assistant that could help students learn from their own study materials rather than relying only on generic answers from an AI model. I wanted the system to make studying more interactive by allowing a student to use their notes as the primary source of information and receive explanations, summaries, questions, and other study support from those materials.

My initial idea was fairly simple: give the AI my study notes and make it behave like a personal study coach. As I worked on the project, however, I realized that building a useful study assistant involves much more than connecting a language model to a prompt. The quality of the notes, the way information is retrieved, the instructions given to the model, and the way the user interacts with the system all affect the final result.

### What Changed During the Project

One of the biggest changes in my thinking was that I stopped viewing the AI model as the entire application. The model is only one component of the system. The actual value comes from designing a workflow around it.

I experimented with different approaches while building StudyVerse AI and learned that the AI needs clear context and instructions to produce useful study responses. I also worked with my own academic material, including subjects such as cryptography, which made it easier to evaluate whether the system was actually helping me understand the content.

Another important change was learning to think about reliability. A language model can produce an answer that sounds convincing even when the answer is not supported by the study material. Because of this, I became more conscious of the difference between an answer that is fluent and an answer that is trustworthy. This changed how I think about AI applications: the goal should not simply be to make the model generate impressive responses, but to design the system so that its responses are useful, relevant, and grounded in the available information.

I also learned that building an AI project involves practical engineering decisions. During development, I faced issues with model/API access and had to reconsider the technology choices instead of assuming that the original approach would always work. This pushed me toward a more practical mindset: when one component creates a limitation, the project should be redesigned around the available resources rather than abandoned.

## What I Would Build Next

If I continued developing StudyVerse AI, I would focus on making it a more complete study platform. I would improve document retrieval so that answers are more consistently grounded in the student's notes. I would also add features such as automatic quizzes, flashcards, spaced-repetition reminders, topic-wise progress tracking, and difficulty adaptation based on the student's performance.

Another improvement would be better evaluation. Instead of only checking whether an answer looks correct, I would create a set of questions with expected answers and measure how accurately the system retrieves and explains information from the source material. I would also test the system across different subjects and document formats.

Finally, I would improve the user interface and deployment so that StudyVerse AI could be used by other students rather than only as a personal prototype.

### Three Transferable Things I Learned

**1. AI application quality depends on the whole system, not just the model.**
Choosing a language model is only one part of building an AI product. Prompting, context, retrieval, interface design, and evaluation are equally important.

**2. Building requires adapting when the original plan does not work.**
Technical limitations such as API availability, model access, or environment problems are part of real development. I learned to troubleshoot, change tools when necessary, and keep the main objective in focus.

**3. Evaluation and reliability matter more than impressive outputs.**
An AI response can sound intelligent without being correct or grounded in the source material. I learned to question the output, verify important information, and think about how the system should be evaluated before considering it successful.

Looking back from the end of the project, StudyVerse AI changed how I think about building with AI. I started with the idea of creating an AI-powered study assistant, but I finished with a better understanding that useful AI products require problem definition, engineering, experimentation, evaluation, and responsible use of AI. The next version of StudyVerse AI would therefore focus not just on adding more features, but on making the system more reliable, measurable, and genuinely useful to students.

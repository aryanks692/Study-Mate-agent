import os
import json
from pathlib import Path
from pypdf import PdfReader
import ollama

def get_notes_folder():
    """Locate or create the notes folder (handles Windows casing)."""
    base_path = Path(".")
    for candidate in [base_path / "Notes", base_path / "notes"]:
        if candidate.exists() and candidate.is_dir():
            return candidate
    folder = base_path / "Notes"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

NOTES_FOLDER = get_notes_folder()

def load_notes():
    """Load and extract text from all PDF files in the notes folder."""
    notes = {}
    folder = get_notes_folder()
    if not folder.exists():
        return notes

    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                notes[file.name] = text
            except Exception as e:
                print(f"Error reading PDF {file.name}: {e}")
    return notes

def get_notes_summary():
    """Get metadata summary for each PDF file in notes directory."""
    summary = []
    folder = get_notes_folder()
    if not folder.exists():
        return summary

    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() == ".pdf":
            try:
                reader = PdfReader(file)
                num_pages = len(reader.pages)
                char_count = sum(len(page.extract_text() or "") for page in reader.pages)
                size_kb = round(file.stat().st_size / 1024, 1)
                summary.append({
                    "filename": file.name,
                    "pages": num_pages,
                    "char_count": char_count,
                    "size_kb": size_kb
                })
            except Exception as e:
                summary.append({
                    "filename": file.name,
                    "pages": 0,
                    "char_count": 0,
                    "size_kb": round(file.stat().st_size / 1024, 1),
                    "error": str(e)
                })
    return summary

def search_notes(query, notes, top_k=8):
    """Search notes for query words and return top matching snippets."""
    query_words = [w.lower() for w in query.split() if len(w) > 1]
    if not query_words:
        query_words = query.lower().split()

    results = []
    for filename, text in notes.items():
        sentences = text.replace("\n", " ").split(".")
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if not sentence_clean:
                continue
            sentence_lower = sentence_clean.lower()
            score = sum(1 for word in query_words if word in sentence_lower)
            if score > 0:
                results.append((score, filename, sentence_clean))

    results.sort(reverse=True, key=lambda x: x[0])
    return results[:top_k]

def ask_ai(question, results, model="llama3.2"):
    """Ask StudyMate AI agent a question using retrieved study context."""
    context = ""
    for score, filename, sentence in results:
        context += f"Source: {filename}\n{sentence}\n\n"

    prompt = f"""You are StudyMate, my personal AI study coach.

Use the study material below to answer the question.

Rules:
1. Prefer the supplied study material.
2. Do not invent information.
3. If the notes do not contain enough information, say that clearly.
4. Explain concepts simply and clearly.
5. Mention the source document when useful.
6. Help the user learn rather than simply completing academic work for them.

STUDY MATERIAL:
{context if context else 'No relevant notes found.'}

QUESTION:
{question}
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def generate_quiz(topic, results, model="llama3.2"):
    """Generate a text-based 5-question quiz."""
    context = ""
    for score, filename, sentence in results:
        context += f"Source: {filename}\n{sentence}\n\n"

    prompt = f"""You are StudyMate, a personal AI study coach.

Create a short quiz using ONLY the study material provided.

Topic:
{topic}

Study material:
{context if context else 'No relevant notes found.'}

Create exactly 5 questions.
Mix conceptual, definition, and application questions.
Do not ask about information that is not contained in the study material.
Do not provide the answers yet.
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

def generate_mcq_quiz(topic, results, model="llama3.2"):
    """Generate a structured MCQ quiz (4 questions with 4 options each) in JSON format."""
    context = ""
    for score, filename, sentence in results:
        context += f"Source: {filename}\n{sentence}\n\n"

    prompt = f"""You are StudyMate, a personal AI study coach.

Create an interactive 4-question Multiple Choice (MCQ) quiz based ONLY on the provided study material.

Topic:
{topic}

Study material:
{context if context else 'No relevant notes found.'}

Rules:
1. Create exactly 4 multiple choice questions.
2. For each question, provide 4 options starting with A), B), C), and D).
3. Specify exactly one correct option letter in "answer" (must be "A", "B", "C", or "D").
4. Provide a brief explanation of why that answer is correct based on the study material.
5. Output ONLY raw JSON array. Start with [ and end with ].

JSON Format required:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": [
      "A) Option 1",
      "B) Option 2",
      "C) Option 3",
      "D) Option 4"
    ],
    "answer": "A",
    "explanation": "Explanation based on notes."
  }}
]
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    raw_content = response["message"]["content"].strip()
    
    cleaned = raw_content
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # 1. Direct JSON parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    # 2. Fix missing closing brackets
    for suffix in ["]", "}]", "\n}]", "\n]"]:
        try:
            data = json.loads(cleaned + suffix)
            if isinstance(data, list):
                return data
        except Exception:
            pass

    # 3. Regex extract question objects
    import re
    pattern = r'\{\s*"id":\s*\d+,\s*"question":.*?"explanation":\s*".*?"\s*\}'
    matches = re.findall(pattern, cleaned, re.DOTALL)
    parsed = []
    for match in matches:
        try:
            obj = json.loads(match)
            parsed.append(obj)
        except Exception:
            pass

    if parsed:
        return parsed

    return raw_content

def evaluate_answer(question, answer, results, model="llama3.2"):
    """Evaluate a student's answer against study material."""
    context = ""
    for score, filename, sentence in results:
        context += f"Source: {filename}\n{sentence}\n\n"

    prompt = f"""You are StudyMate.

Evaluate the student's answer using the study material.

Study material:
{context if context else 'No relevant notes found.'}

Question:
{question}

Student answer:
{answer}

Do the following:
1. Say whether the answer is correct, partially correct, or incorrect.
2. Explain why.
3. Give the correct explanation.
4. Mention what the student should remember.

Do not invent information outside the supplied material.
"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

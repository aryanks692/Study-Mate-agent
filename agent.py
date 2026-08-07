from pathlib import Path
from pypdf import PdfReader
import ollama

NOTES_FOLDER = Path("notes")


# -----------------------------
# 1. LOAD NOTES
# -----------------------------

def load_notes():
    notes = {}

    for file in NOTES_FOLDER.iterdir():

        if file.suffix.lower() == ".pdf":

            reader = PdfReader(file)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            notes[file.name] = text

    return notes


# -----------------------------
# 2. SEARCH NOTES
# -----------------------------

def search_notes(query, notes):

    query_words = query.lower().split()

    results = []

    for filename, text in notes.items():

        sentences = text.replace("\n", " ").split(".")

        for sentence in sentences:

            sentence_lower = sentence.lower()

            score = sum(
                1
                for word in query_words
                if word in sentence_lower
            )

            if score > 0:

                results.append(
                    (
                        score,
                        filename,
                        sentence.strip()
                    )
                )

    results.sort(reverse=True)

    return results[:8]


# -----------------------------
# 3. ASK AI
# -----------------------------

def ask_ai(question, results):

    context = ""

    for score, filename, sentence in results:

        context += f"""
Source: {filename}

{sentence}
"""


    prompt = f"""
You are StudyMate, my personal AI study coach.

Use the study material below to answer the question.

Rules:

1. Prefer the supplied study material.
2. Do not invent information.
3. If the notes do not contain enough information,
   say that clearly.
4. Explain concepts simply.
5. Mention the source document when useful.
6. Help the user learn rather than simply completing
   academic work for them.

STUDY MATERIAL:

{context}

QUESTION:

{question}
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -----------------------------
# 4. GENERATE QUIZ
# -----------------------------

def generate_quiz(topic, results):

    context = ""

    for score, filename, sentence in results:

        context += f"""
Source: {filename}

{sentence}
"""


    prompt = f"""
You are StudyMate, a personal AI study coach.

Create a short quiz using ONLY the study material provided.

Topic:
{topic}

Study material:
{context}

Create exactly 5 questions.

Mix:
- conceptual questions
- definition questions
- application questions

Do not ask about information that is not contained
in the study material.

Do not provide the answers yet.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -----------------------------
# 5. EVALUATE ANSWER
# -----------------------------

def evaluate_answer(question, answer, results):

    context = ""

    for score, filename, sentence in results:

        context += f"""
Source: {filename}

{sentence}
"""


    prompt = f"""
You are StudyMate.

Evaluate the student's answer using the study material.

Study material:
{context}

Question:
{question}

Student answer:
{answer}

Do the following:

1. Say whether the answer is correct, partially correct,
   or incorrect.
2. Explain why.
3. Give the correct explanation.
4. Mention what the student should remember.

Do not invent information outside the supplied material.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -----------------------------
# 6. LOAD STUDY MATERIAL
# -----------------------------

notes = load_notes()

print("===================================")
print("       StudyMate AI Agent")
print("===================================")

print("\nLoaded study material:")

for filename, text in notes.items():

    print(
        f"- {filename}: "
        f"{len(text)} characters"
    )


# -----------------------------
# 7. CHAT LOOP
# -----------------------------

while True:

    user_input = input("\nYou: ")

    if user_input.lower() in [
        "exit",
        "quit",
        "bye"
    ]:

        print("StudyMate: Goodbye!")
        break


    # -------------------------
    # QUIZ MODE
    # -------------------------

    if user_input.lower().startswith("quiz me on"):

        topic = user_input[11:].strip()

        results = search_notes(
            topic,
            notes
        )

        if not results:

            print(
                "\nStudyMate: "
                "I couldn't find this topic in your notes."
            )

            continue

        quiz = generate_quiz(
            topic,
            results
        )

        print("\nStudyMate — Quiz:")
        print(quiz)

        continue


    # -------------------------
    # NORMAL STUDY MODE
    # -------------------------

    results = search_notes(
        user_input,
        notes
    )

    if not results:

        print(
            "\nStudyMate: "
            "I couldn't find relevant information "
            "in your study notes."
        )

        continue


    answer = ask_ai(
        user_input,
        results
    )

    print("\nStudyMate:")
    print(answer)
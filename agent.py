from studymate_core import (
    load_notes,
    search_notes,
    ask_ai,
    generate_quiz,
    evaluate_answer
)

# -----------------------------
# 1. LOAD STUDY MATERIAL
# -----------------------------

notes = load_notes()

print("===================================")
print("       StudyMate AI Agent")
print("===================================")

print("\nLoaded study material:")

for filename, text in notes.items():
    print(f"- {filename}: {len(text)} characters")


# -----------------------------
# 2. CHAT LOOP
# -----------------------------

while True:
    try:
        user_input = input("\nYou: ")
    except (KeyboardInterrupt, EOFError):
        print("\nStudyMate: Goodbye!")
        break

    if user_input.lower().strip() in ["exit", "quit", "bye"]:
        print("StudyMate: Goodbye!")
        break

    if not user_input.strip():
        continue

    # -------------------------
    # QUIZ MODE
    # -------------------------
    if user_input.lower().startswith("quiz me on"):
        topic = user_input[11:].strip()
        results = search_notes(topic, notes)

        if not results:
            print("\nStudyMate: I couldn't find this topic in your notes.")
            continue

        quiz = generate_quiz(topic, results)
        print("\nStudyMate — Quiz:")
        print(quiz)
        continue

    # -------------------------
    # NORMAL STUDY MODE
    # -------------------------
    results = search_notes(user_input, notes)

    if not results:
        print("\nStudyMate: I couldn't find relevant information in your study notes.")
        continue

    answer = ask_ai(user_input, results)
    print("\nStudyMate:")
    print(answer)
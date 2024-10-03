import json
from fuzzywuzzy import process
import streamlit as st

# Load data from the JSON file
def load_data(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Save data to the JSON file
def save_data(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Intelligent matching using fuzzy logic (across all categories)
def fuzzy_match(question, data):
    all_questions = []
    category_map = {}
    
    # Loop through all categories and questions
    for category, qa_pairs in data.items():
        for q in qa_pairs.keys():
            all_questions.append(q)
            category_map[q] = category  # Map questions to categories
    
    # Use fuzzy matching to find the closest match
    best_match, score = process.extractOne(question, all_questions)
    
    if score > 75:  # Only consider matches with a score above 75%
        matched_category = category_map[best_match]
        return best_match, data[matched_category][best_match], matched_category
    return None, None, None

# Feedback mechanism to improve answers
def get_feedback(question, answer, category, data):
    feedback = st.radio(f"Was the answer to '{question}' helpful?", ('yes', 'no'), key=f"feedback_radio_{question}")
    if feedback == 'no':
        new_answer = st.text_input("Please provide the correct answer:", key=f"feedback_input_{question}")
        if st.button("Submit Feedback", key=f"feedback_button_{question}"):
            if new_answer:
                data[category][question] = new_answer
                st.success("Thank you for your feedback. The answer has been updated.")
                save_data('learned_data.json', data)

# Chatbot logic
def chatbot():
    data = load_data('learned_data.json')  # Load data from the JSON file

    st.title("Chatbot Interface")

    user_input = st.text_input("Type 'start' to begin or 'exit' to quit:", key="user_input").strip().lower()

    if user_input == 'exit':
        st.write("Chatbot: Thank you for your time. Goodbye!")

    elif user_input == 'start':
        user_question = st.text_input("Ask your question:", key="question_input").strip()

        # Fuzzy logic for question matching
        if user_question:
            selected_question, answer, matched_category = fuzzy_match(user_question, data)
            
            if selected_question:
                st.write(f"Did you mean: '{selected_question}'?")
                if st.button("Yes, show answer", key=f"fuzzy_yes_button_{selected_question}"):
                    st.write(f"Chatbot: {answer}")
                    get_feedback(selected_question, answer, matched_category, data)
            else:
                st.warning("No close matches found. Please try rephrasing your question.")
    
    else:
        st.warning("Please type 'start' or 'exit'.")

if __name__ == "__main__":
    chatbot()

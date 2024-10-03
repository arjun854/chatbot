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

# Display categories and allow the user to choose one
def display_categories(data):
    st.write("### Available Categories:")
    categories = list(data.keys())
    selected_category = st.selectbox("Select a category", categories, key="category_selectbox")
    return selected_category

# Display questions in a selected category and allow the user to choose one
def display_questions(data, category):
    st.write(f"### Questions in '{category}':")
    questions = list(data[category].keys())
    
    if questions:
        selected_question = st.selectbox("Select a question", questions, key=f"question_selectbox_{category}")
        return selected_question
    else:
        st.write("No questions available in this category.")
        return None

# Intelligent matching using fuzzy logic (used as a fallback if no exact match is found)
def fuzzy_match(question, data):
    all_questions = []
    category_map = {}
    for category, qa_pairs in data.items():
        for q in qa_pairs.keys():
            all_questions.append(q)
            category_map[q] = category

    # Use fuzzy matching to find the closest match
    best_match, score = process.extractOne(question, all_questions)
    if score > 75:  # Only consider matches with a score above 75%
        category = category_map[best_match]
        return best_match, data[category][best_match], category
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

# Add a new question and answer to an existing category
def add_new_qa(data, category):
    question = st.text_input("Enter the new question:", key="new_question_input")
    answer = st.text_input("Enter the answer:", key="new_answer_input")
    
    if st.button("Add Question", key="add_question_button"):
        # Add the new question and answer to the category
        if question and answer:
            data[category][question] = answer
            st.success("New question and answer added successfully!")
            save_data('learned_data.json', data)
        else:
            st.error("Both question and answer fields must be filled!")

# Edit an existing question and answer
def edit_qa(data, category, question):
    if question:  # Ensure a question is selected before proceeding
        st.write(f"Current Question: {question}")
        new_question = st.text_input("Enter the new question (or leave blank to keep it the same):", key=f"edit_new_question_input_{question}")
        new_answer = st.text_input("Enter the new answer (or leave blank to keep it the same):", key=f"edit_new_answer_input_{question}")

        if st.button("Update Question", key=f"update_question_button_{question}"):
            # Update question and answer
            if new_question:
                data[category][new_question] = data[category].pop(question)  # Rename the question
            if new_answer:
                data[category][new_question if new_question else question] = new_answer

            st.success("Question and answer updated successfully!")
            save_data('learned_data.json', data)

# Delete an existing question
def delete_qa(data, category, question):
    if question:  # Ensure a question is selected before proceeding
        if st.button("Delete Question", key=f"delete_question_button_{question}"):
            del data[category][question]
            st.success("Question deleted successfully!")
            save_data('learned_data.json', data)

# Chatbot logic
def chatbot():
    data = load_data('learned_data.json')  # Load data from the JSON file

    st.title("Chatbot Interface")

    user_input = st.text_input("Type 'start' to begin or 'exit' to quit:", key="user_input").strip().lower()

    if user_input == 'exit':
        st.write("Chatbot: Thank you for your time. Goodbye!")

    elif user_input == 'start':
        category = display_categories(data)
        question = display_questions(data, category)

        # If there are no questions, prompt to add a new question
        if question is None:  # No questions available
            st.write("You can add your first question for this category.")
            add_new_qa(data, category)
        else:
            # Provide the answer to the selected question
            answer = data[category][question]
            st.write(f"Chatbot: {answer}")

            # Ask for feedback on the answer
            get_feedback(question, answer, category, data)

            # Show options to add, edit, or delete a question
            option = st.radio("Would you like to:", 
                              ("Add a new question", 
                               "Edit the selected question", 
                               "Delete the selected question", 
                               "Continue without changes"), 
                              key="options_radio")

            if option == "Add a new question":
                add_new_qa(data, category)
            elif option == "Edit the selected question":
                edit_qa(data, category, question)
            elif option == "Delete the selected question":
                delete_qa(data, category, question)

    else:
        st.warning("Please type 'start' or 'exit'.")

if __name__ == "__main__":
    chatbot()

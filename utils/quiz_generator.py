from openai import OpenAI
import os
import json
import re

from utils.pdf_reader import extract_text_from_pdf, download_pdf_from_firebase

def generate_quiz(file_path):

    download_pdf_from_firebase(file_path)
    text = extract_text_from_pdf("uploads/temp.pdf")


    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    input_content = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user", 
                "content": (
                    "Create a 10-question multiple-choice quiz based on the following text. "
                    "Format the response in this exact structure:\n\n"
                    "1. Question text\n"
                    "   a) Option 1\n"
                    "   b) Option 2\n"
                    "   c) Option 3\n"
                    "   d) Option 4\n"
                    "Answer: (correct option letter)\n\n"
                    "Text:\n" + text
                )   
            }
        ],
        )
    response_content = input_content.choices[0].message.content
    return response_content



def format_quiz_to_json(response_content):
    """
    parses the generated quiz text and formats it into a JSON structure.
    the quiz follows a structured format like:

    {
        question: "What is Capital of France?",
        options: ["a) Paris", "b) London", "c) Berlin", "d) Rome"],
        answer: "a"
    }
    """
    quiz = []
    questions = re.split(r"\n\d+\.", response_content)  # split by numbered questions

    # skip empty first split
    for question in questions[0:]:  
        lines = question.strip().split("\n")
        if len(lines) < 5:  # ensure there is a question, 4 options, and an answer
            continue
        
        question_text = lines[0].strip()
        options = [f"{chr(65+i)}. {line[3:].strip()}" for i, line in enumerate(lines[1:5])]  # formatting options
        answer_line = next((line for line in lines if line.lower().startswith("answer:")), None)

        if answer_line:
            answer = answer_line.split(":")[1].strip().lower()  # getting the answer
        else:
            answer = None

        quiz.append({
            "question": question_text,
            "options": options,
            "answer": answer
        })

    return json.dumps({"quiz": quiz}, indent=4)  # convert to JSON format




from openai import OpenAI
import os
import json
import re

from utils.pdf_reader import extract_text_from_pdf, download_pdf_from_firebase


def count_tokens(messages):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages  # Pass the messages here
    )
    return response.usage.total_tokens


def chunk_text(text, max_chunk_size=1500):
    # breaks the text into chunks based on max_chunk_size token limit
    chunks = []
    words = text.split(' ')
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word.split())  # Approximate token length by word count

        if current_length >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
    if current_chunk:  # Append the last chunk if there's remaining text
        chunks.append(' '.join(current_chunk))

    return chunks


def generate_quiz(file_path):
    download_pdf_from_firebase(file_path)
    text = extract_text_from_pdf("uploads/temp.pdf")

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # Break the text into chunks
    text_chunks = chunk_text(text, max_chunk_size=1500)

    # Build the initial message
    message = {
        "role": "user",
        "content": (
            "Create a 5-question multiple-choice quiz based on the following text. "
            "Format the response in this exact structure:\n\n"
            "1. Question text\n"
            "   a) Option 1\n"
            "   b) Option 2\n"
            "   c) Option 3\n"
            "   d) Option 4\n"
            "Answer: (correct option letter)\n\n"
            "Text:\n"
        )
    }

    quiz_response = ""
    total_tokens = 0

    # Process text chunks and stop when reaching the token limit
    for chunk in text_chunks:
        message["content"] += chunk
        messages = [message]

        # Get token count before sending the request
        tokens_in_message = count_tokens(messages)
        total_tokens += tokens_in_message

        # Stop if total token count exceeds limit
        if total_tokens > 16385:
            print("Token limit exceeded. Stopping processing.")
            break

        input_content = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        # Access the response content
        quiz_response += input_content.choices[0].message.content

    return quiz_response


def format_quiz_to_json(response_content):
    """
    Parses the generated quiz text and formats it into a JSON structure.
    The quiz follows a structured format like:

    {
        "question": "What is Capital of France?",
        "options": ["a) Paris", "b) London", "c) Berlin", "d) Rome"],
        "answer": "a"
    }
    """
    quiz = []
    questions = re.split(r"(?:^|\n)\s*\d+[\.\)]\s*", response_content)  # Split by numbered questions

    # Skip empty first split
    for question in questions:  
        lines = question.strip().split("\n")
        if len(lines) < 6:  # Ensure there is a question, 4 options, and an answer
            continue
        
        question_text = lines[0].strip()

        # Format to "A. option text"
        options = []
        for i in range(4):
            raw = lines[i + 1].strip()
            label = chr(65 + i)  # A, B, C, D
            option_text = re.sub(r"^[a-dA-D]\)", "", raw).strip()
            options.append(f"{label}. {option_text}")
        
        # get answer letter
        answer_line = next((line for line in lines if line.lower().startswith("answer:")), None)
        if answer_line:
            match = re.search(r"\(?([a-dA-D])\)?", answer_line)
            answer = match.group(1).lower() if match else None
        else:
            answer = None

        quiz.append({
            "question": question_text,
            "options": options,
            "answer": answer
        })

    return json.dumps({"quiz": quiz}, indent=4)  # convert to JSON format




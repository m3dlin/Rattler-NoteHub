from transformers import T5ForConditionalGeneration, T5Tokenizer

from pdf_reader import extract_text_from_pdf,download_pdf_from_firebase
from database import get_note

# Load the fine-tuned T5 model specifically for question generation
model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-small-qg-hl")
tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-small-qg-hl", legacy=False)

def generate_question(text):
    # Make the prompt more specific, asking for a question based on the content of the text
    input_text = f"Generate a multiple-choice question with four options, including the correct answer, based on the following text. Provide the question and the options in this format: Question: <question> A) <option1> B) <option2> C) <option3> D) <option4>: {text}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")

    # Generate the question
    outputs = model.generate(input_ids, max_length=150, num_beams=4, early_stopping=True)
    question = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return question

# Example text
download_pdf_from_firebase(get_note(44).file_path)
extracted_text = extract_text_from_pdf("uploads/temp.pdf")
question = generate_question(extracted_text)
print(question)

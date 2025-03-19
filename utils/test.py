import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from nltk import pos_tag
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from pdf_reader import download_pdf_from_firebase,extract_text_from_pdf
from database import get_note

# Download necessary resources for NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

def preprocess_text(text):
    # Tokenize sentences and words
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    
    # Remove stopwords and non-alphanumeric tokens
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    words = [
        lemmatizer.lemmatize(word.lower()) 
        for word in words 
        if word.isalnum() and word.lower() not in stop_words
    ]
    
    return sentences, words

def extract_key_terms(text):
    # Tokenize words and filter out non-alphanumeric words
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum() and len(word) > 3]
    
    tagged_words = pos_tag(words)
    key_terms = [word for word, tag in tagged_words if tag in ['NN', 'NNP', 'JJ']]
    
    # Get the most common key terms
    fdlist = FreqDist(key_terms)
    common_terms = [word for word, _ in fdlist.most_common(20)]
    return common_terms

def get_distractors(word, key_terms):
    distractors = set()

    # Use WordNet to find synonyms and hypernyms
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            distractors.add(lemma.name().replace("_", " "))
        for hypernym in syn.hypernyms():
            for lemma in hypernym.lemmas():
                distractors.add(lemma.name().replace("_", " "))

    # Remove the correct word from distractors and fill in with key terms if not enough choices
    distractors.discard(word)
    distractors = list(distractors)
    
    while len(distractors) < 3:
        sample = random.choice(key_terms)
        if sample != word and sample not in distractors:
            distractors.append(sample)

    return distractors[:3]

def classify_sentences(sentences):
    # Use TF-IDF to vectorize sentences and classify their relevance
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences)
    y = [1 if len(s.split()) > 4 else 0 for s in sentences]  # Rule: long sentences are 'good'
    
    classifier = LogisticRegression()
    classifier.fit(X, y)
    
    return classifier.predict(X)

def generate_questions(text):
    sentences, _ = preprocess_text(text)
    key_terms = extract_key_terms(text)
    
    # Ensure there are enough key terms to generate a quiz
    if len(key_terms) < 4:
        print("Not enough key terms extracted to generate quiz.")
        return []
    
    # Classify sentences and select relevant ones
    sentence_labels = classify_sentences(sentences)
    relevant_sentences = [s for s, label in zip(sentences, sentence_labels) if label == 1]

    if len(relevant_sentences) == 0:
        print("No relevant sentences found for quiz generation.")
        return []
    
    quiz = []
    
    # Varied question types
    for term in key_terms:
        for sent in relevant_sentences:
            if term in sent and len(sent) > len(term) + 10:
                # **1. Fill-in-the-Blank Question**
                question = sent.replace(term, "____")
                if len(question.split()) <= 12:
                    distractors = get_distractors(term, key_terms)
                    options = [term] + distractors
                    random.shuffle(options)
                    quiz.append(('Fill-in-the-Blank', question, options, term))
                    break
                
                # **2. True/False Question**
                if random.random() > 0.5:  # Randomly choose whether to create T/F question
                    true_or_false = f"True or False: {sent}"
                    quiz.append(('True/False', true_or_false, ['True', 'False'], 'True'))
                    break
                
                # **3. Definition-Based Question**
                if random.random() > 0.5:  # Random chance to create definition-based questions
                    definition_question = f"What is the meaning of {term}?"
                    distractors = get_distractors(term, key_terms)
                    options = [term] + distractors
                    random.shuffle(options)
                    quiz.append(('Definition', definition_question, options, term))
                    break

                # **4. Multiple Choice Question**
                if random.random() > 0.5:  # Random chance to create a MCQ
                    mcq_question = f"Which of the following is related to {term}?"
                    distractors = get_distractors(term, key_terms)
                    options = [term] + distractors
                    random.shuffle(options)
                    quiz.append(('Multiple Choice', mcq_question, options, term))
                    break
    
    return quiz if quiz else print("No valid questions could be generated.")

def print_quiz(quiz):
    for i, (qtype, question, options, answer) in enumerate(quiz, 1):
        print(f"Q{i} ({qtype}): {question}")
        for j, option in enumerate(options, start=1):
            print(f"  {j}. {option}")
        print(f"Answer: {answer}\n")


# Example Usage
# Assuming you have functions to download and extract text from a PDF, you can use them like this:
download_pdf_from_firebase(get_note(44).file_path)
text = extract_text_from_pdf("uploads/temp.pdf")
quiz = generate_questions(text)
print_quiz(quiz)
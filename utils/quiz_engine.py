import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.probability import FreqDist
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree

import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


import pdf_reader
from pdf_reader import download_pdf_from_firebase,extract_text_from_pdf
from database import get_note
"""
NOTES:

sentence tokenization: splits the text into  individual sentences.
word tokenization: splits the text into individual words.
- why we need to tokenize: to analyze the text and extract useful information from it.

stop words: common words that are removed from the text like 'the', 'is', 'and', etc.
- why we need to remove stop words: to focus on the important words in the text.

(part of speech)
pos_tag: used for identifying words as nouns, verbs, adjectives
- why we need pos_tag: nouns are usually the most important words in important concepts.

(named entity recognition)
ne_chunk: used for identifying named entities in the text like names, places, etc.
- why we need ne_chunk: to identify the important entities in the text.

(word frequency distribution)
FreqDist: used to find the most common words in the text.
- why we need FreqDist: to identify the important words to turn into questions.

"""

"""
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# used to download the necessary resources for NLTK
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('wordnet')
"""


def preprocess_text(text):
    # tokenize sentences
    sentences = sent_tokenize(text)

    # tokenize words and remove stop words
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    
    lemmatizer = WordNetLemmatizer()
    words = [
        lemmatizer.lemmatize(word.lower())  # reduces the word to its base form. ex: running -> run
        for word in word_tokenize(text) # tokenize words
        if word.isalnum() and word.lower() not in stop_words # remove stop words
    ]
    
    return sentences, words

def extract_key_terms(text):
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum() and len(word) > 3]

    tagged_words = pos_tag(words)

    # extract nouns (NN), proper nouns (NNP), and adjectives (JJ)
    key_terms = [word for word, tag in tagged_words if tag in ['NN', 'NNP', 'JJ']]

    # remove duplicates and get the most common terms
    fdlist = FreqDist(key_terms)
    common_terms = [word for word, _ in fdlist.most_common(20)]
    return common_terms


def get_distractors(word, key_terms):
    distractors = set()

    # getting synonyms and hypernyms (general words) from wordnet.
    # wordnet is a lexical database for the English language
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            distractors.add(lemma.name().replace("_", " "))
        for hypernym in syn.hypernyms():
            for lemma in hypernym.lemmas():
                distractors.add(lemma.name().replace("_", " "))

    # remove the correct word and limit choices
    distractors.discard(word)
    distractors = list(distractors)

    # fill with key_terms retrieved from the text if wordnet doesn't provide enough options
    while len(distractors) < 3:
        sample = random.choice(key_terms)
        if sample != word and sample not in distractors:
            distractors.append(sample)

    return distractors[:3]

def classify_sentences(sentences):
    # tf-idf vectorization helps identify the most important sentences
    vectorizer = TfidfVectorizer()

    # x is the vectorized sentences and y is the target
    # target (1 = good, 0 = bad), ideally this would be learned from a labeled dataset
    X = vectorizer.fit_transform(sentences)
    y = [1 if len(s.split()) > 4 else 0 for s in sentences]  # Simple rule: long sentences are 'good'
    
    classifier = LogisticRegression()
    classifier.fit(X, y)
    
    return classifier.predict(X)


def generate_questions(text):
    sentences, _ = preprocess_text(text)
    key_terms = extract_key_terms(text)
    
    # if there are not enough key terms, it's not possible to generate questions
    if len(key_terms) < 4:
        print("Not enough key terms extracted to generate quiz.")
        return []
    
    # classify sentences to find the most relevant ones
    sentence_labels = classify_sentences(sentences)
    relevant_sentences = [s for s, label in zip(sentences, sentence_labels) if label == 1]

    # if there are no relevant sentences, it's not possible to generate questions
    if len(relevant_sentences) == 0:
        print("No relevant sentences found for quiz generation.")
        return []
    
    quiz = []
    # for each key term, find a relevant sentence to generate a question
    for term in key_terms:
        for sent in relevant_sentences:
            # if the term is in the sentence and the sentence is long enough
            if term in sent and len(sent) > len(term) + 10:
                # shortening the sentence by removing irrelevant phrases
                question = sent.replace(term, "____")
                # making sure the question is good by checking the length
                if len(question.split()) <= 12:  # 12 words max per question
                    distractors = get_distractors(term, key_terms)
                    options = [term] + distractors
                    random.shuffle(options)
                    quiz.append((question, options, term))
                    break
    
    return quiz if quiz else print("No valid questions could be generated.")





def print_quiz(quiz):
    for i, (question, options, answer) in enumerate(quiz, 1):
        print(f"Q{i}: {question}")
        for j, option in enumerate(options, start=1):
            print(f"  {j}. {option}")
        print(f"Answer: {answer}\n") 

# Example Usage
download_pdf_from_firebase(get_note(44).file_path)
text = extract_text_from_pdf("uploads/temp.pdf")
quiz = generate_questions(text)
print_quiz(quiz)
import os
import pandas as pd
from textblob import TextBlob
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import cmudict
import nltk
nltk.download('cmudict', download_dir='nltk_data')
nltk.data.path.append('nltk_data')
nltk.download('punkt')

personal_pronouns = ["i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves"]

def load_words(file_path):
    with open(file_path, 'r') as file:
        words = file.read().splitlines()
    return words

def calculate_score(text, positive_words, negative_words):
    words = text.lower().split()
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words)
    return positive_score, negative_score

# POSITIVE AND NEGATIVE WORD TEXT FILE 
positive_words = load_words("positive-words.txt")
negative_words = load_words("negative-words.txt")

# EXTRACT THE TEXT FILE 
scraped_dir = 'scraped_content' 
excel_file_path = 'Output Data Structure.xlsx' 
df = pd.read_excel(excel_file_path)

# DIRECTORY FOR COMPLEX WORDS 
cmu_dict = cmudict.dict()

# CALCULATE THE SYLLABLES WORDS WITH THIS 
def count_syllables(word):
    if word.lower() in cmu_dict:
        return max([len(list(y for y in x if y[-1].isdigit())) for x in cmu_dict[word.lower()]])
    return 0

# TO CALCULATE THE FOG INDEX 
def calculate_fog_index(words, sentences, complex_word_count):
    average_sentence_length = len(words) / sentences
    percentage_complex_words = (complex_word_count / len(words)) * 100
    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)
    return fog_index

df['URL_ID'] = df['URL_ID'].astype(int)

for filename in os.listdir(scraped_dir):
    if filename.endswith('.txt'):
        filepath = os.path.join(scraped_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        blob = TextBlob(content)
        # POLARITY SCORE 
        polarity_score = blob.sentiment.polarity
        subjectivity_score = blob.sentiment.subjectivity
        
        sentences = sent_tokenize(content)
        total_sentence_length = sum(len(sent.split()) for sent in sentences)
        avg_sentence_length = total_sentence_length / len(sentences)
        
        # TOTAL NUMBER OF WORDS 
        total_words = sum(len(word_tokenize(sent)) for sent in sentences)
        avg_words_per_sentence = total_words / len(sentences)
        
        words = word_tokenize(content)
        total_word_length = sum(len(word) for word in words)
        avg_word_length = total_word_length / len(words)
        word_count = len(words)
        
        # SYLLABLES 
        total_syllables = sum(count_syllables(word) for word in words)
        syllables_per_word = total_syllables / len(words)
        
        # COMPLEX WORD COUNT 
        complex_word_count = sum(1 for word in words if len(cmu_dict.get(word.lower(), [])) > 2)
        total_words = len(words)
        complex_word_percentage = (complex_word_count / total_words) * 100 if total_words > 0 else 0

        # POSITIVE AND NEGATIVE SCORE CALCULATION 
        positive_score, negative_score = calculate_score(content, positive_words, negative_words)
        
        # PERSONAL PRONOUN COUNT 
        personal_pronoun_count = sum(1 for word in words if word.lower() in personal_pronouns)
        
        fog_index = calculate_fog_index(words, len(sentences), complex_word_count)
        
        
        file_number = filename.split('.')[0]
        file_number_numeric = int(file_number)
        
        print(f"Processing file: {filename}, File number: {file_number_numeric}")
        
        # TO THROUGH THE DATA TO EXCEL FILE 
        if file_number_numeric in df['URL_ID'].values:
            row_index = df[df['URL_ID'] == file_number_numeric].index[0]
            df.loc[row_index, 'POSITIVE SCORE'] = positive_score
            df.loc[row_index, 'NEGATIVE SCORE'] = negative_score
            df.loc[row_index, 'POLARITY SCORE'] = polarity_score
            df.loc[row_index, 'SUBJECTIVITY SCORE'] = subjectivity_score
            df.loc[row_index, 'AVG SENTENCE LENGTH'] = avg_sentence_length
            df.loc[row_index, 'PERCENTAGE OF COMPLEX WORDS'] = complex_word_percentage
            df.loc[row_index, 'FOG INDEX'] = fog_index
            df.loc[row_index, 'AVG NUMBER OF WORDS PER SENTENCE'] = avg_words_per_sentence
            df.loc[row_index, 'COMPLEX WORD COUNT'] = complex_word_count
            df.loc[row_index, 'WORD COUNT'] = word_count
            df.loc[row_index, 'SYLLABLE PER WORD'] = syllables_per_word
            df.loc[row_index, 'PERSONAL PRONOUNS'] = personal_pronoun_count
            df.loc[row_index, 'AVG WORD LENGTH'] = avg_word_length
            print("Updated scores for", filename)
        else:
            print("File number not found in DataFrame:", file_number_numeric)

df.to_excel(excel_file_path, index=False)
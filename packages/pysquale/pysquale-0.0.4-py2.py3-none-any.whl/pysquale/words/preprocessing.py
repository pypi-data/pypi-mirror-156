from typing import List
from nltk import word_tokenize, sent_tokenize
from .cleaning import to_lower
from . import STOPWORDS, STEMMER_DICT

def tokenize(text:str, target:str='word')->List[str]:
    """
    tokenize can only target word or sentence
    """
    tokenize_function = word_tokenize if target == 'word' else sent_tokenize
    text_list =  tokenize_function(to_lower(text))
    return text_list

def detokenize(text_list:List[str])->str:
    new_text = " ".join(text_list)
    return new_text

def remove_stopwords(word_list:List[str], additional_word_list:List=[])->List[str]:
    stopwords = STOPWORDS   
    stopwords.extend(additional_word_list)
    new_word_list = [word for word in word_list if word not in stopwords]
    return new_word_list

def stem(word_list:List[str], stem_algo:str='rlsp')->List[str]:
    stemmer = STEMMER_DICT.get(stem_algo)
    new_word_list = [stemmer.stem(word) for word in word_list]
    return new_word_list

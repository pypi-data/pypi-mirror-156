import re
from typing import List
import unicodedata
from . import PUNCTUATION_STRING, STOPWORDS

def remove_punctuation(text:str)->str:
    new_text = text.translate(str.maketrans('', '', PUNCTUATION_STRING))
    return new_text

def remove_accentuation(text:str)->str:
    new_text = ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))
    return new_text

def remove_email(text:str)->str:
    new_text = re.sub(r'\S*@\S*\s?', ' ', text)
    return new_text

def remove_numbers(text:str)->str:
    new_text = re.sub(r"$\d+\W+|\b\d+\b|\W+\d+$", ' ', text)
    return new_text

def remove_html(text:str)->str:
    new_text = re.sub(r"<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>",'',text)
    return new_text

def remove_url(text:str)->str:
    new_text = re.sub(r'(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}[-a-zA-Z0-9()@:%_+.~#?&/=]*)', ' ', text) 
    return new_text

def remove_extra_spaces(text:str)->str:
    new_text = " ".join(text.split()).strip()
    new_text = re.sub(r'\s+([?.!"])', r'\1', new_text)
    return new_text

def to_lower(text:str)->str:
    new_text = text.lower()
    return new_text

import os
from typing import Dict, List
import pkg_resources

DIR = os.path.dirname(__file__)
FILES_PATH = "files/"

def get_abbreviation_map()->Dict[str,str]:
    file_name = "abbreviations.txt"
    unparsed = read_file(file_name)
    abbreviation_map = {j[0]: j[1] for j in [i.split(' : ') for i in unparsed]}
    return abbreviation_map

def get_abbreviation_list():
    abbreviation_list = list(get_abbreviation_map().keys())
    return abbreviation_list

def get_punctuation_list()->List[str]:
    file_name = "punctuation.txt"
    punctuation_list = read_file(file_name)
    return punctuation_list

def get_punctuation_string()->str:
    punctuation_list = get_punctuation_list()
    punctuation_string = ''.join(punctuation_list)
    return punctuation_string

def get_stopwords()->List[str]:
    file_name = "stopwords.txt"
    stopwords = read_file(file_name)
    return stopwords

def get_last_names()->List[str]:
    file_name = "last_names.txt"
    last_names = read_file(file_name)
    return last_names

def get_female_names()->List[str]:
    file_name = "ibge_female_names.txt"
    female_names = read_file(file_name)
    return female_names

def get_male_names()->List[str]:
    file_name = "ibge_male_names.txt"
    male_names = read_file(file_name)
    return male_names

def read_file(file_name:str)->List[str]:
    path = FILES_PATH + file_name
    abs_file_path = pkg_resources.resource_filename(__name__, path)
    with open(abs_file_path, "r") as txt_file:
        file_content = txt_file.read()
        content_list = file_content.split("\n")
        return content_list

# def read_file(dir:str, relative_file_path:str, file_name:str)->List[str]:
#     abs_file_path = os.path.join(dir, relative_file_path, file_name)
#     with open(abs_file_path, "r") as txt_file:
#         file_content = txt_file.read()
#         content_list = file_content.split("\n")
#         return content_list

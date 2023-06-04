import pandas as pd
import string
from unidecode import unidecode
import re
import os

TRANSACTIONS_DATA_PATH = os.path.join(os.pardir, 'data', 'transactions.csv')

references = "ref .{10,25}\/\/.{10,20}\/\/c\s*n\s*t\s*r|ref .{10,25}\/|\d{9,15}\/\/c\s*n\s*t\s*r"
other_tokens = "for deel|to deel|deel|from|payment|transfer|received|\d{1,10}"
multi_spaces = "\s\s+"
end_spaces = "^\s+|\s+$"

punctuation_without_slashes = '!"#$%&\'()*+,-.:;<=>?@[]^_`{|}~'

def clean_description(s):
    s = unidecode(s).casefold()
    s = s.translate(s.maketrans({k: ' ' for k in punctuation_without_slashes}))
    return re.sub('\s\s+', ' ', s)

def remove_punctuation(s):
    return s.translate(s.maketrans({k: ' ' for k in string.punctuation}))

def find_user_in_description(s):
    s = unidecode(s).casefold() # Transforms unicode to ascii, dealing with accents and foreign languages, and transforms it to lowercase.
    s = re.sub(references, '', s) # Removes transaction reference code.
    s = remove_punctuation(s) # Transforms all punctuation to whitespace.
    s = re.sub(multi_spaces, ' ', s) #Transforms multiple spaces into one
    s = re.sub(other_tokens, '', s) # Removes other unnecessary tokens
    s = re.sub(multi_spaces, ' ', s) #Transforms multiple spaces into one again
    return re.sub(end_spaces, '', s) #Removes spaces at the beginning and end of the string


if __name__ == '__main__':
    df_transactions = pd.read_csv(TRANSACTIONS_DATA_PATH)
    df_transactions['clean_description'] = df_transactions['description'].apply(clean_description)
    df_transactions['found_user'] = df_transactions['description'].apply(find_user_in_description)
    df_transactions.to_csv(os.path.join(os.pardir, 'data', 'transactions_clean.csv'), index=False)
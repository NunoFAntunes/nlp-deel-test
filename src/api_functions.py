import pandas as pd
from thefuzz import fuzz
from thefuzz import process
from api_models import Transaction

def calculate_confidence_score (transaction_text, name):
    return fuzz.token_set_ratio(name, transaction_text)

def search_client_transactions(df_transactions, client_name):
    df_transactions['confidence'] = df_transactions['found_user'].apply(calculate_confidence_score, name=client_name)
    filtered_df = df_transactions[df_transactions['confidence'] > 60]
    found_hits = list(zip(filtered_df.id, filtered_df.confidence))
    list_of_hits = []
    for hit in found_hits:
        t = Transaction(id=hit[0], match_metric=hit[1])
        list_of_hits.append(t)
    return list_of_hits, len(list_of_hits)
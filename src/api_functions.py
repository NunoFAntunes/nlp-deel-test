from thefuzz import fuzz
from api_models.api_model_ex1 import Transaction as TransactionEx1
from api_models.api_model_ex2 import Transaction as TransactionEx2
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import pandas as pd
from clean_transactions import clean_description

model = SentenceTransformer('all-MiniLM-L6-v2')

#Exercise 1
def calculate_confidence_score (transaction_text, name):
    return fuzz.token_set_ratio(name, transaction_text)

def search_client_transactions(df_transactions, client_name):
    df_transactions['confidence'] = df_transactions['found_user'].apply(calculate_confidence_score, name=client_name)
    filtered_df = df_transactions[df_transactions['confidence'] > 60]
    found_hits = list(zip(filtered_df.id, filtered_df.confidence))
    list_of_hits = []
    for hit in found_hits:
        t = TransactionEx1(id=hit[0], match_metric=hit[1])
        list_of_hits.append(t)
    return list_of_hits, len(list_of_hits)


#Exercise 2

def encode_client_transactions(df_transactions):
    id_list = df_transactions['id'].to_list()
    descriptions = df_transactions['clean_description'].to_list()
    embeddings = model.encode(descriptions)
    tokens_size = embeddings.shape[1]
    df_id_vs_embeddings = pd.DataFrame(columns = ['id', 'embeddings'], data = zip(id_list, embeddings))
    return df_id_vs_embeddings, tokens_size


def calculate_similarity(row_embedding, query_embedding):
    return cos_sim(row_embedding, query_embedding).item() #Item converts tensor to float.


def search_closest_sentence(s, df_id_vs_embeddings):
    query_embedding = model.encode(clean_description(s)) # Using the same cleaning function for the query.
    df_id_vs_embeddings['similarity'] = df_id_vs_embeddings['embeddings'].apply(calculate_similarity, query_embedding=query_embedding)
    results_filtered = df_id_vs_embeddings[df_id_vs_embeddings['similarity'] > 0.5]
    results_filtered.sort_values(by='similarity', ascending=False, na_position='last', inplace=True)
    records = results_filtered.to_records(index=False)
    list_of_hits = []
    for record in records:
        t = TransactionEx2(id=record.id, embedding=record.embeddings.tolist())
        list_of_hits.append(t)
    return list_of_hits
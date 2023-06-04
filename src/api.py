from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os
from unidecode import unidecode
from api_functions import search_client_transactions, encode_client_transactions, search_closest_sentence
from api_models.api_model_ex1 import ClientTransactions as ClientTransactionsEx1
from api_models.api_model_ex2 import ClientTransactions as ClientTransactionsEx2
app = FastAPI()

# Currently the dataframe is loaded here. In a production environment, we would likely have a connection to a database or data source
TRANSACTIONS_DATA_PATH = os.path.join(os.pardir, 'data', 'transactions_clean.csv')
df_transactions = pd.read_csv(TRANSACTIONS_DATA_PATH)

# This is only ran once, when the server starts. The embeddings are calculated for all transactions and stored in a dataframe.
# This is only here for the sake fo simplicity of the exercise. In a real world scenario, we would likely store the embeddings in the database, and only
# calculate embeddings for descriptions that do not yet have them. 
df_id_vs_embeddings, tokens_size = encode_client_transactions(df_transactions)


@app.get("/client_transactions/name={client_name}")
def get_client_transactions(client_name):
    client_name = unidecode(client_name).casefold()
    transaction_list, total_matches = search_client_transactions(df_transactions, client_name)
    return ClientTransactionsEx1(
        transactions=transaction_list,
        total_number_of_matches=total_matches
    )
    

@app.get("/client_transactions/query={query}")
def get_closest_transactions(query):
    transaction_list = search_closest_sentence(query, df_id_vs_embeddings)
    return ClientTransactionsEx2(
        transactions=transaction_list,
        total_number_of_tokens_used=tokens_size
    )
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from api_functions import search_client_transactions
from api_models import ClientTransactions

app = FastAPI()

# Currently the dataframe is loaded here. In a production environment, we would likely have a connection to a database or data source
TRANSACTIONS_DATA_PATH = '../data/transactions_clean.csv'
df_transactions = pd.read_csv(TRANSACTIONS_DATA_PATH)


@app.get("/client_transactions/{client_name}")
def get_client_transactions(client_name):
    transaction_list, total_matches = search_client_transactions(df_transactions, client_name)
    return ClientTransactions(
        transactions=transaction_list,
        total_number_of_matches=total_matches
    )
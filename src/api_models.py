from pydantic import BaseModel
from typing import Union, List

class Transaction(BaseModel):
    id: str
    match_metric: float
    
class ClientTransactions(BaseModel):
    transactions: List[Transaction]
    total_number_of_matches: int
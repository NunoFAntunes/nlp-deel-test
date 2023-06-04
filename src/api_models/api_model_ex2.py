from pydantic import BaseModel
from typing import Union, List

class Transaction(BaseModel):
    id: str
    embedding: List
    
class ClientTransactions(BaseModel):
    transactions: List[Transaction]
    total_number_of_tokens_used: int
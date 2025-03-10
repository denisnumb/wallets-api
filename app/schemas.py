from pydantic import BaseModel
from enum import Enum
from uuid import UUID


class WalletResponse(BaseModel):
    uuid: UUID
    balance: float

class OperationType(Enum):
    WITHDRAW = 'WITHDRAW'
    DEPOSIT = 'DEPOSIT'

class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: float
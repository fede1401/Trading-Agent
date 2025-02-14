from enum import Enum

class AgentState(Enum):
    INITIAL = 'INITIAL'
    PURCHASE = 'PURCHASE'
    SALE = 'SALE'
    SALE_IMMEDIATE = 'SALE_IMMEDIATE'
    WAIT = 'WAIT'

from enum import Enum

class AgentState(Enum):
    INITIAL = 'INITIAL'
    PURCHASE = 'PURCHASE'
    SALE = 'SALE'
    WAIT = 'WAIT'

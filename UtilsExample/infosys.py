import sys

print(sys.path)

sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent1')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent2')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent3')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

from db import connectDB
import agentState


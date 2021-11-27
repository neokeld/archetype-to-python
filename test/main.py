from smart_contract_lark import smart_contract_lark
from exec_cond_demo import exec_cond_demo
from state_machine_demo import state_machine_demo

# Smart contract 1

smart_contract_lark = smart_contract_lark(holder="test")
assert smart_contract_lark.holder == "test", "Holder is not set in constructor"
smart_contract_lark.pay()

# Smart contract 2

exec_cond_demo = exec_cond_demo(value=10)
assert exec_cond_demo.value == 10, "Value is not set in constructor"
exec_cond_demo.setvalue(25)
assert exec_cond_demo.value == 25, "Value is not set in setter"

# Smart contract 3

state_machine_demo = state_machine_demo(holder="test")
assert state_machine_demo.currentState == "Created", "Current state is not set in constructor"
state_machine_demo.initialize()
assert state_machine_demo.currentState == "Initialized", "Current state is not set in initialize transition"
state_machine_demo.terminate()
assert state_machine_demo.currentState == "Terminated", "Current state is not set in terminate transition"

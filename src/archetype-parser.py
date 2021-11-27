import logging
from datetime import datetime, timedelta
from decimal import Decimal
from lark import Lark, logger, Tree, Token

logger.setLevel(logging.DEBUG)

# V1 started on 2021-11-14 to produce an AST from some archetype smart contracts code and interpret it
# ended on 2021-11-21
# Lark Grammar Reference: https://lark-parser.readthedocs.io/en/latest/grammar.html
# Lark Cheatsheet: https://lark-parser.readthedocs.io/en/latest/_static/lark_cheatsheet.pdf
# Archetype Reference: https://docs.archetype-lang.org/archetype-reference
# Archetype Examples: https://archetype-lang.org/

lark_ebnf_grammar = '''
start: "archetype" NAME "(" parameters* ")" (entry|transition|states)+

NAME: ("a".."z"|"_")+
parameters: PARAMETER_NAME ":" PARAMETER_TYPE
PARAMETER_NAME: ("a".."z"|"_")+
PARAMETER_TYPE: ("a".."z"|"_")+

entry: "entry" ENTRY_NAME "(" parameters* ")" _entry_code_block
transition: "transition" TRANSITION_NAME "()" _transition_code_block
states: "states" "=" ("|" STATE)+

ENTRY_NAME: ("a".."z"|"_")+
TRANSITION_NAME: ("a".."z"|"_")+
STATE: ("a".."z"|"A".."Z")+

_entry_code_block: "{" (transfer|called_by|require|effect)+ "}"
transfer: "transfer" "(" _simple_expr ")" "to holder"
called_by: "called by" "admin"
require: "require" "{" (REQUIRE_NAME ":" (_literal|NAME) COMPARATOR (_literal|NAME) ";")+ "}"

_transition_code_block: "{" (from|when|effect)+ "}"
from: "from" STATE "to" STATE
when: "when {" NAME COMPARATOR NUMBER "}"
effect: "effect" "{" (transfer|assignment) "}"

assignment: EFFECT_TARGET ":=" EFFECT_VALUE ";"

NUMBER: ("0".."9")+
COMPARATOR: ("<"|">"|"="|"<>"|"<="|">=")
REQUIRE_NAME: ("a".."z"|"_"|"0".."9")+
EFFECT_TARGET: ("a".."z"|"_"|"0".."9")+
EFFECT_VALUE: ("a".."z"|"_"|"0".."9")+

_simple_expr: _simple_expr _LBRACKET _simple_expr _RBRACKET
        | _LBRACKET _RBRACKET
        | _LBRACKET _simple_expr _RBRACKET
        | sum
        | product
        | minus
        | NOW
        | _literal

sum: _simple_expr "+" _simple_expr
product: _simple_expr "*" _simple_expr
minus: _simple_expr " - " _simple_expr

_literal: NUMBER
    | DURATION
    | DATE
    | PERCENT_LIT

_LBRACKET: "("
_RBRACKET: ")"
DURATION: ("0".."9"+"w"("0".."9"+"d")?("0".."9"+"h")?("0".."9"+"m")?("0".."9"+"s")?)|("0".."9"+"d"("0".."9"+"h")?("0".."9"+"m")?("0".."9"+"s")?)|("0".."9"+"h"("0".."9"+"m")?("0".."9"+"s")?)|("0".."9"+"m"("0".."9"+"s")?)|"0".."9"+"s"
DATE: "0".."9"~4"-""0".."9"~2"-""0".."9"~2
PERCENT_LIT: "0".."9"+"%"
NOW: "now"

%import common.WS
%ignore WS
'''

parser = Lark(lark_ebnf_grammar)

smart_contract_1 = '''
archetype smart_contract_lark(holder : address)
entry pay () {
  transfer (1 + 7% * (now - 2021-01-01 + 1w1d)) to holder
}
'''

smart_contract_2 = '''
archetype exec_cond_demo(value : nat)

entry setvalue (v : nat) {
  called by admin
  require {
    r1: transferred > value;
    r2: now < 2022-01-01;
  }
  effect {
    value := v;
  }
}
'''

smart_contract_3 = '''
archetype state_machine_demo(holder : address)

states =
| Created
| Initialized
| Terminated

transition initialize () {
  from Created to Initialized
  when { transferred > 10 }
}

transition terminate () {
  from Initialized to Terminated
  effect { transfer (1 + 1) to holder }
}
'''

parse_tree = parser.parse(smart_contract_2)
print(parse_tree.pretty())

def parse_int(left_expr, right_expr):
    if isinstance(left_expr, timedelta) and (isinstance(right_expr, int) or isinstance(right_expr, float)):
        return [left_expr.days, right_expr]
    elif (isinstance(left_expr, int) or isinstance(left_expr, float)) and isinstance(right_expr, timedelta):
        return [left_expr, right_expr.days]
    else:
        return [left_expr, right_expr]

def parse_timedelta(duration_string): #example: '3w8d4h34m18s'
    total_seconds = Decimal('0')
    prev_num = []
    for character in duration_string:
        if character.isalpha():
            if prev_num:
                num = Decimal(''.join(prev_num))
                if character == 'w':
                    total_seconds += num * 60 * 60 * 24 * 7
                elif character == 'd':
                    total_seconds += num * 60 * 60 * 24
                elif character == 'h':
                    total_seconds += num * 60 * 60
                elif character == 'm':
                    total_seconds += num * 60
                elif character == 's':
                    total_seconds += num
                prev_num = []
        elif character.isnumeric() or character == '.':
            prev_num.append(character)
    return timedelta(seconds=float(total_seconds))

def exec_expr(expr):
    if isinstance(expr, Tree):
        if expr.data == 'sum':
            a = exec_expr(expr.children[0])
            b = exec_expr(expr.children[1])
            [a, b] = parse_int(a, b)
            return a + b
        elif expr.data == 'product':
            a = exec_expr(expr.children[0])
            b = exec_expr(expr.children[1])
            [a, b] = parse_int(a, b)
            return a * b
        elif expr.data == 'minus':
            a = exec_expr(expr.children[0])
            b = exec_expr(expr.children[1])
            [a, b] = parse_int(a, b)
            return a - b
        else:
            return exec_expr(expr.children[0])
    elif isinstance(expr, Token):
        if expr.type == 'NUMBER':
            return int(expr.value)
        elif expr.type == 'PERCENT_LIT':
            return int(expr.value[:-1]) / 100.
        elif expr.type == 'DURATION':
            return parse_timedelta(expr.value)
        elif expr.type == 'DATE':
            return datetime.strptime(expr.value, '%Y-%m-%d').date()
        elif expr.type == 'NOW':
            return datetime.now().date()

states = []
state = ''

def exec_state(expr):
    global states
    global state
    for state in instruction.children:
        states.append(state.value)
    state = states[0]

def exec_transition(expr):
    global states
    global state
    if isinstance(expr, Token):
        if expr.type == 'TRANSITION_NAME':
            print(f"transition: {expr.value}")
    
    if isinstance(expr, Tree):
        if expr.data == 'from':
            print('from')
            if state == expr.children[0].value:
                new_state = expr.children[1].value
                if new_state in states :
                    state = new_state
            else:
                print("Bad transition in from")
        elif expr.data == 'when':
            print('when')
        elif expr.data == 'effect':
            print('effect')
            print(exec_expr(expr))

def run_instruction(instruction):
    if isinstance(instruction, Tree):
        if instruction.data == 'parameters':
            parameter_name = instruction.children[0].value
            parameter_type = instruction.children[1].value
            print(f"parameters: {parameter_name}:{parameter_type}")
        if instruction.data == 'entry':
            main_simple_expression = instruction.children[1]
            #print(main_simple_expression.pretty())
            print(exec_expr(main_simple_expression))
        if instruction.data == 'states':
            exec_state(instruction)
        if instruction.data == 'transition':
            for expr in instruction.children:
                exec_transition(expr)
    
    if isinstance(instruction, Token):
        if instruction.type == 'NAME':
            print(instruction.value)

for instruction in parse_tree.children:
    run_instruction(instruction)

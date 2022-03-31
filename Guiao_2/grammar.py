## Primeiro precisamos da GIC
grammar = '''
start: initializations code?
initializations: initialization SC (initialization SC)*
initialization: TYPE var (EQUAL operand)?
var: WORD (OS INT* CS)?
code: block+
block: atribution SC
     | condition
     | cycle
atribution: var EQUAL operand (operator operand)*
condition: IF boolexpr OB code CB (ELSE OB code CB)?
cycle: WHILE boolexpr OB code CB
boolexpr: OP operand (operator operand (AND operand operator operand)*)? CP
WHILE: "while"
IF: "if"
ELSE: "else"
OP: "("
CP: ")"
operand: value | var
operator: GT|LT|GET|GLT|EQUALS|DIFF|PLUS|MINUS|MULT|DIV
GT: ">"
LT: "<"
GET: ">="
GLT: "<="
EQUALS: "=="
DIFF: "!="
PLUS: "+"
MINUS: "-"
MULT:"*"
DIV:"/"
OB: "{"
CB: "}"
AND : "&&"
TYPE: "int" 
    | "float" 
    | "str"
EQUAL: "="
value: ESCAPED_STRING
     | FLOAT 
     | INT
SC: ";"
OS: "["
CS: "]"

%import common.WS
%import common.NEWLINE
%ignore WS
%ignore NEWLINE
%import common.INT
%import common.WORD
%import common.FLOAT
%import common.ESCAPED_STRING
'''
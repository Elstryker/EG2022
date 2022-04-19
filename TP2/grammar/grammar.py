## Primeiro precisamos da GIC
grammar = '''
start: code*
code: (declaration | instruction)+

instruction: atribution ";" -> instruction_atribution
           | condition      -> instruction_condition
           | cycle          -> instruction_cycle

atribution: var "=" expression 


var: WORD              
   | WORD "[" INT "]"   -> var_struct

condition: "if" "(" boolexpr ")" "{" code "}"                       
         | "if" "(" boolexpr ")" "{" code "}" "else" "{" code "}"   -> condition_else

cycle: while_cycle
     | do_while_cycle
     | repeat_cycle
     | for_cycle

while_cycle: "while" "(" boolexpr ")" "{" code "}"
do_while_cycle: "do" "{" code "}" "while" "(" boolexpr ")"
repeat_cycle: "repeat" "(" matexpr ")" "{" code "}"
for_cycle: "for" "(" atribution? ";" boolexpr? ";" atribution? ")" "{" code "}"

expression: operand     -> expression_var
          | boolexpr    -> expression_boolexpr
          | matexpr     -> expression_matexpr

matexpr: operand (MAT_OPERATOR operand)+

simple_bool_expr: (operand | matexpr) BOOL_OPERATOR (operand | matexpr)
boolexpr: simple_bool_expr (LOGIC simple_bool_expr)*

BOOL_OPERATOR: ">"|"<"|">="|"<="|"=="|"!="
MAT_OPERATOR: "+"|"-"|"*"|"/"

LOGIC : "&&"
      | "||"

operand: value | var

value: ESCAPED_STRING   -> value_string
     | FLOAT            -> value_float
     | INT              -> value_int
     | BOOL             -> value_bool

%import common.WS
%import common.NEWLINE
%ignore WS
%ignore NEWLINE
%import common.INT
%import common.WORD
%import common.FLOAT
%import common.ESCAPED_STRING
%import .grammar.declarations  (declaration,BOOL,TYPE)
'''
## Primeiro precisamos da GIC
grammar = '''
start: code*
code: (declaration | instruction)+

instruction: atribution ";"
           | condition     
           | cycle          

atribution: var "=" (expression | list | tuple | set | dict)


var: WORD              
   | WORD "[" operand "]"

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

expression: boolexpr 
          | matexpr  

matexpr: operand (MAT_OPERATOR operand)*

simple_bool_expr: matexpr BOOL_OPERATOR matexpr
                | BOOL

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
%import .grammar.declarations  (declaration,BOOL,TYPE,set,tuple,dict,list)
'''
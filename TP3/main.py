from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar.grammar import grammar
from interpreter.interpreter import MainInterpreter
from interpreter.interpreterGraph import MainInterpreterGraph

phrase = """
str a = "1";

str b = a;
str ggg;
int lol;

str lol = 5;

int hh = 1;

if(z < a) {
    if( z < 1 ) {
        lol = 2;
        lol = 3;
        lol = 4;
    }
}
else {
    lol = 7;
    lol = 8;
}

for(lol = 0; lol < 1; lol = lol + 1) {
    lol = 4;
    lol = 5;
}

lol = 9;
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MainInterpreterGraph().visit(parse_tree)


# print("Número de estruturas de controlo aninhadas:"+str(data["controlInside"]))

#print(data["html"])

# import json

#print(json.dumps(data['vars'],sort_keys=True, indent=4))


# print(parse_tree.pretty())

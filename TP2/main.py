from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar.grammar import grammar
from interpreter.interpreter import MainInterpreter

phrase = """
str a = "1";

str b = a;
str ggg;
int b;

str gh = ggg;

int set c;
str set guy = {"on","tw","th","fo"};
float tuple tu = (1.2,2.,3.);
(int,str) dict di = {3:"ro",6:"he",7:"ko",9.:"o"};
bool goo = 2;

a = 1;

x=3;
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MainInterpreter().visit(parse_tree)

print(data["html"])

import json

print(json.dumps(data['vars'],sort_keys=True, indent=4))

# print(parse_tree.pretty())

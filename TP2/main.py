from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar.grammar import grammar
from interpreter.interpreter import MainInterpreter

phrase = """
str a = "1";
int b;
str b = 3.;

int set c;
str set guy = {"on","tw","th","fo"};
float tuple tu = (1.2,2.,3.);
bool goo = False;

a = 1;

x=3;
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MainInterpreter().visit(parse_tree)

print(data)

# print(parse_tree.pretty())

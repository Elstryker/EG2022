from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar import grammar
from interpreter import MyInterpreter

phrase = """
str a = "1";
int b;
a = 2;
if(3 > a) {
    b = "0";
}"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MyInterpreter().visit(parse_tree)

print(data)
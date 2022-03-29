from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar import grammar
from interpreter import MyInterpreter

phrase = """
str a = "1";
int b;
int c;
a = 2;
if (a > 2) {
    c = 4;
}
else {
    c = 2;
}

while(a >= 5) {
    c = 5;
    a = 1;
}
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MyInterpreter().visit(parse_tree)

print(data)
from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar import grammar
from interpreter import MyInterpreter

phrase = """
int z;

int x;

if(cond > 0) {
    if(y > 1) {
        if(z > 2) {
            z = 1; k = 3;
        }
        if(k > 2) {
            k=2; z=9; x=5;
        }
    }
    while(cond > 0) {
        if(z < 8) {
            z = 1;
        }
    }
}

x=3;
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MyInterpreter().visit(parse_tree)

print(data["html"])
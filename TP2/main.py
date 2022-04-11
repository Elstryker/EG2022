from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar.grammar import grammar
from interpreter.interpreter import MainInterpreter

phrase = """
str a = "1";
int b;

int set c;
int tuple a = (1.2,2.,3.);
(str,int) dict di = {3:"ro",6:"he"};
bool goo = False;

a = 1;

if(cond > 0 + 1 && a + 1 == 0 || cond < 2) {
    if(y[0] > 1) {
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
        else {
            x[1] = 0;
        }
    }
}

x=3;
"""

print(grammar)

p = Lark(grammar)

parse_tree = p.parse(phrase)

# data = MainInterpreter().visit(parse_tree)

print(parse_tree.pretty())
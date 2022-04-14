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

if(cond > 0 + 1 && a + 1 == 0 || cond < 2) {
    if(y[0] > 1) {
        if(z > 2) {
            z = 1; k = 3;
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
for(i = 0; i<a;a=a+1){
    a =1;
}
x=3;
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MainInterpreter().visit(parse_tree)

print(data["controlInside"])

# print(parse_tree.pretty())

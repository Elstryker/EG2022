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
int z;

str gh = ggg;

int set c;
str set guy = {"on","tw","th","fo"};
float tuple tu = (1.2,2.,3.);
(int,str) dict di = {3:"ro",6:"he",7:"ko",9:"o"};
bool goo = 2;
str teste;
a = 1;
teste = di[1];
if(cond > 0 + 1 && a + 1 == 0 || cond < 2) {
    if(y[0] > 1) { 
        if(z > 2) { 
            if(z > 3) {
                z = 1; k = 3;
            }
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


# print("Número de estruturas de controlo aninhadas:"+str(data["controlInside"]))

#print(data["html"])

# import json

#print(json.dumps(data['vars'],sort_keys=True, indent=4))


# print(parse_tree.pretty())

from lark import Discard
from lark import Lark,Token,Tree
from lark.tree import pydot__tree_to_png

from grammar import grammar
from interpreter import MyInterpreter

phrase = """
str a = "1";
int b;
int ds[1]=1;
int c;
a = 2;
if (a > 2) {
    if(b == 0 && 10>0 && b>10) {
        if(c) {
            c = 4 + 5 * 10 / 43;
            c = ds[1];
        }
        else {
            c = 10;
        }
    }
}
else {
    c = 2;
}
if (a > 3) {
    if(b == 0) {
        a = 2;
    }
}

while(a >= 5) {
    while(a>=5){
        while(a>0){
            c = 5;
            a = 1;
        }
    }
}
"""

p = Lark(grammar)

parse_tree = p.parse(phrase)

data = MyInterpreter().visit(parse_tree)

print(data["code"])
print("Nível máximo de aninhamento de ifs:",data["maxIfDepth"])
print("Número de ifs:",data["numberIfs"],"\n")
print("Nível máximo de aninhamento de ciclos:",data["maxCycleDepth"])
print("Número de ciclos:",data["numberCycles"],"\n")
print("Erros:")
print(data["errors"],"\n")
print("Warnings")
print(data["warnings"])